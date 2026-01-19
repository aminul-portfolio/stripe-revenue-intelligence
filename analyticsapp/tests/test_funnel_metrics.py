import uuid

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase
from django.utils import timezone

from analyticsapp.services.funnel import wishlist_funnel
from orders.models import Order
from products.models import Product
from wishlist.models import Wishlist


def _build_required_kwargs(model_cls, *, depth=0):
    """
    Minimal generic factory kwargs builder for unknown schemas.
    Handles common field types and required FKs (1 level deep).
    """
    kwargs = {}
    for f in model_cls._meta.fields:
        if f.primary_key or f.name in {"id", "pk"}:
            continue
        if getattr(f, "auto_now", False) or getattr(f, "auto_now_add", False):
            continue
        if f.has_default() or f.null or f.blank:
            continue

        # ForeignKey (one level deep)
        if isinstance(f, models.ForeignKey):
            if depth >= 1:
                # last resort: try NULL if allowed (but it shouldn't be here if required)
                continue
            rel_model = f.remote_field.model
            rel_obj = rel_model.objects.create(**_build_required_kwargs(rel_model, depth=depth + 1))
            kwargs[f.name] = rel_obj
            continue

        # Scalar fields
        if isinstance(f, (models.CharField, models.SlugField)):
            kwargs[f.name] = f"test-{f.name}-{uuid.uuid4().hex[:10]}"

        elif isinstance(f, models.TextField):
            kwargs[f.name] = f"test-{f.name}"
        elif isinstance(f, models.EmailField):
            kwargs[f.name] = "test@example.com"
        elif isinstance(f, (models.IntegerField, models.PositiveIntegerField, models.BigIntegerField)):
            kwargs[f.name] = 1
        elif isinstance(f, (models.BooleanField,)):
            kwargs[f.name] = False
        elif isinstance(f, (models.DecimalField,)):
            kwargs[f.name] = Decimal("10.00")
        elif isinstance(f, (models.DateField,)):
            kwargs[f.name] = timezone.localdate()
        elif isinstance(f, (models.DateTimeField,)):
            kwargs[f.name] = timezone.now()
        else:
            # If you hit this, your Product model has a required field of a type we didn't cover.
            # We'll extend the factory based on the traceback.
            raise AssertionError(f"Unsupported required field: {model_cls.__name__}.{f.name} ({type(f)})")

    return kwargs


class WishlistFunnelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.u_wish_only = User.objects.create_user("wish_only", "wish_only@example.com", "pass12345")
        self.u_wish_and_buy = User.objects.create_user("wish_buy", "wish_buy@example.com", "pass12345")
        self.u_buy_only = User.objects.create_user("buy_only", "buy_only@example.com", "pass12345")
        self.u_wish_outside = User.objects.create_user("wish_out", "wish_out@example.com", "pass12345")

        self.p1 = Product.objects.create(**_build_required_kwargs(Product))
        self.p2 = Product.objects.create(**_build_required_kwargs(Product))

    def test_wishlist_funnel_counts_distinct_users_in_same_window(self):
        now = timezone.now()
        start = now - timedelta(days=30)
        end = now

        t_in = now - timedelta(days=5)
        t_out = now - timedelta(days=365)

        # In-window wishlist users: wish_only + wish_and_buy
        w1 = Wishlist.objects.create(user=self.u_wish_only, product=self.p1)
        w2 = Wishlist.objects.create(user=self.u_wish_and_buy, product=self.p2)
        Wishlist.objects.filter(id=w1.id).update(created_at=t_in)
        Wishlist.objects.filter(id=w2.id).update(created_at=t_in)

        # Out-of-window wishlist user (should not count)
        w3 = Wishlist.objects.create(user=self.u_wish_outside, product=self.p1)
        Wishlist.objects.filter(id=w3.id).update(created_at=t_out)

        # Completed purchase in-window by wish_and_buy (should count)
        o1 = Order.objects.create(user=self.u_wish_and_buy, email="wish_buy@example.com", status="paid")
        Order.objects.filter(id=o1.id).update(created_at=t_in)

        # Completed purchase in-window by buy_only (should NOT count because not in wish_users)
        o2 = Order.objects.create(user=self.u_buy_only, email="buy_only@example.com", status="paid")
        Order.objects.filter(id=o2.id).update(created_at=t_in)

        # Non-completed order in-window by wish_only (should NOT count)
        o3 = Order.objects.create(user=self.u_wish_only, email="wish_only@example.com", status="pending")
        Order.objects.filter(id=o3.id).update(created_at=t_in)

        # Purchase in-window by wish_outside (should NOT count because wishlist is out of window)
        o4 = Order.objects.create(user=self.u_wish_outside, email="wish_out@example.com", status="paid")
        Order.objects.filter(id=o4.id).update(created_at=t_in)

        # Extra wishlist + extra order for same user should still count as 1 distinct
        w_extra = Wishlist.objects.create(user=self.u_wish_and_buy, product=self.p1)
        Wishlist.objects.filter(id=w_extra.id).update(created_at=t_in)
        o_extra = Order.objects.create(user=self.u_wish_and_buy, email="wish_buy@example.com", status="fulfilled")
        Order.objects.filter(id=o_extra.id).update(created_at=t_in)

        kpis = wishlist_funnel(start, end)

        self.assertEqual(kpis["wish_users"], 2)        # wish_only + wish_and_buy
        self.assertEqual(kpis["purchased_users"], 1)   # wish_and_buy only

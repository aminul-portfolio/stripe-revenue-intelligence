from django.contrib import admin, messages

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = (
        "product",
        "variant",
        "product_name",
        "sku",
        "unit_price",
        "qty",
        "line_total",
    )

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "status",
        "total",
        "stripe_payment_intent",
        "stripe_charge_id",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("email", "id", "stripe_payment_intent", "stripe_charge_id")
    inlines = [OrderItemInline]

    # Always read-only fields
    readonly_fields = (
        "subtotal",
        "total",
        "stripe_payment_intent",
        "stripe_charge_id",
        "created_at",
        "updated_at",
    )

    def _is_stripe_order(self, obj: Order) -> bool:
        return bool(obj.stripe_payment_intent) and obj.stripe_payment_intent.startswith(
            "pi_"
        )

    def _is_mock_paid(self, obj: Order) -> bool:
        return obj.stripe_payment_intent == "mock" or obj.stripe_charge_id == "mock"

    def get_readonly_fields(self, request, obj=None):
        """
        Lock down status edits for Stripe-tracked orders to avoid manual 'paid'
        without webhook truth.
        """
        ro = list(super().get_readonly_fields(request, obj=obj))
        if obj:
            # If Stripe mode (pi_), Ops should NOT manually change status.
            # Webhook is source of truth.
            if self._is_stripe_order(obj):
                ro.append("status")
        return tuple(ro)

    def save_model(self, request, obj, form, change):
        """
        Hard guard: prevent setting status=paid unless payment references exist
        (or mock mode) to avoid false 'paid' and monitoring noise.
        """
        if change:
            prev = Order.objects.get(pk=obj.pk)

            # Only validate if status is being changed (and not already read-only)
            if "status" in form.changed_data:
                # Block: manual paid without Stripe refs (unless mock)
                if obj.status == "paid":
                    is_mock = self._is_mock_paid(obj)
                    has_charge = bool(obj.stripe_charge_id)
                    # If Stripe intent exists but no charge -> webhook hasn't confirmed.
                    if not is_mock and not has_charge:
                        messages.error(
                            request,
                            "Blocked: You cannot set this order to PAID manually without a Stripe charge id "
                            "(or mock refs). Payment confirmation must come from the Stripe webhook.",
                        )
                        # Revert status to previous value and do not save the invalid change
                        obj.status = prev.status
                        return

                # Optional: block paid -> pending rollback (usually a compliance issue)
                if prev.status == "paid" and obj.status == "pending":
                    messages.error(
                        request,
                        "Blocked: You cannot revert a PAID order back to PENDING in admin.",
                    )
                    obj.status = prev.status
                    return

        super().save_model(request, obj, form, change)

# Refund Policy — PureLaka (Operational Rules)

This document defines the refund policy as **operational rules** (what Ops/Admin can do),
and as **system rules** (what the application must enforce).

It is intentionally conservative: any rule not yet verified in code remains **TBD** until confirmed.

---

## 1) Scope

- Refund types (full vs partial, if supported)
- Eligibility (time windows, order states, payment status)
- Roles and authorization (who can initiate/approve)
- Audit/monitoring requirements (what must be recorded)
- Implementation references (where the rules live in code)

---

## 2) Definitions (TBD until verified)

- **Refund:** reversal of funds for a paid order (TBD: provider rules)
- **Full refund:** refund entire paid amount (TBD)
- **Partial refund:** refund subset of paid amount (TBD)
- **Chargeback / dispute:** not a refund (TBD: tracked separately or out-of-scope)

---

## 3) Policy rules (initial template)

### 3.1 Eligibility (TBD until verified)
- Orders eligible for refund: **TBD**
- Orders NOT eligible for refund: **TBD**
- Time window constraints: **TBD**
- Refund after shipment/fulfillment: **TBD** (if fulfillment exists)
- Refund if already refunded: must be blocked (TBD where enforced)

### 3.2 Refund types supported (TBD until verified)
- [ ] Full refund supported: TBD
- [ ] Partial refund supported: TBD
- [ ] Multiple partial refunds supported: TBD

### 3.3 State transitions (TBD until verified)
Describe what happens to order status when a refund occurs.

- `PAID` → `REFUNDED` (TBD exact state strings)
- Partial refund status behavior: TBD (e.g., `PARTIALLY_REFUNDED`)

---

## 4) Roles / authorization (must be explicit)

- Admin: TBD
- Ops: TBD
- Analyst: no refund permission (TBD)
- Customer: TBD (self-serve or not)

Reference RBAC source of truth:
- `docs/rbac_matrix.md`

---

## 5) Required records (audit + monitoring)

Refund operations must create:
- [ ] An audit trail entry (who/when/what changed)
- [ ] A monitoring/issue signal if policy violated or refund fails (TBD)

---

## 6) Implementation references (to fill after verification)

- Refund initiation path: TBD
- Stripe/PSP integration (if any): TBD
- Order status mutation: TBD
- Tests asserting refund behavior: TBD
- Admin actions / endpoints: TBD

---

## 7) Verification checklist (complete once confirmed)

- [ ] Exact order status strings confirmed and inserted
- [ ] Refund trigger location(s) linked (code paths)
- [ ] Permission enforcement confirmed (RBAC)
- [ ] Tests exist and are referenced
- [ ] Monitoring hooks (if present) referenced

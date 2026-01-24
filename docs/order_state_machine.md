# Order State Machine (Lifecycle) — PureLaka

This document defines the **order lifecycle states**, the **allowed transitions**, and the **events** that trigger transitions.
It is written to be recruiter/auditor friendly: it distinguishes between **what we claim** and **what is evidenced in code**.

> **Source of truth:** the codebase.  
> This doc must be updated to match the current implementation after verification steps below.

---

## 1) What this covers

- [ ] Canonical order **states** (exact strings used in DB)
- [ ] Allowed **transitions** (state A → state B)
- [ ] Transition **triggers** (payment succeeded, refund issued, admin cancel, etc.)
- [ ] **Guards** (rules preventing invalid transitions)
- [ ] Where to find it in code (models/services/tests)

---

## 2) Implementation verification (NO guessing)

Run the commands in the Run section at the bottom and paste outputs back.
Then we will replace all **TBD** placeholders below with the confirmed implementation.

### Evidence we need from the repo
- [ ] Where order status is defined (model field / choices / enum)
- [ ] Any service layer that changes status (e.g., order service, payment webhooks)
- [ ] Any tests that assert status transitions
- [ ] Any admin actions / management commands that mutate status

---

## 3) Current lifecycle (draft template — replace TBD after verification)

### 3.1 Canonical states (TBD until verified)
> Replace these with the exact status values found in code.

- **TBD_STATE_1**
- **TBD_STATE_2**
- **TBD_STATE_3**
- **TBD_STATE_4**
- **TBD_STATE_5**

### 3.2 Allowed transitions (TBD until verified)
> Replace these with verified transitions from code/tests.

- `TBD_STATE_1` → `TBD_STATE_2` (trigger: TBD)
- `TBD_STATE_2` → `TBD_STATE_3` (trigger: TBD)
- `TBD_STATE_3` → `TBD_STATE_4` (trigger: TBD)

### 3.3 Mermaid diagram (template — update after verification)

```mermaid
stateDiagram-v2
  [*] --> TBD_STATE_1

  TBD_STATE_1 --> TBD_STATE_2: trigger TBD
  TBD_STATE_2 --> TBD_STATE_3: trigger TBD
  TBD_STATE_3 --> TBD_STATE_4: trigger TBD

  %% terminal example (adjust)
  TBD_STATE_4 --> [*]

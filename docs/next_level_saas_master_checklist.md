# ✅ Updated Master “Next Level SaaS” Template Polish Checklist (Job-First + £30k Sale-Ready) — Single Source of Truth

**Status rule:** Mark **Done** only with proof (**URL + screenshot path + file path + commit hash**).  
**Default status:** **Unknown / needs confirmation** until verified.

**Responsive proof standard (mandatory):**
- **Desktop guarantee:** **1280px**
- **Hero proof screenshot:** **1440px**
- **Mobile guarantee:** **390px**

---

## 0) Global UI System (applies to every template)

### 0.1 Layout + Visual System (P0)
- [ ] **1280px layout guarantee**: header/actions/toolbars look intentional; no clipping/overlap — **Unknown**
  - Proof: `..._1280.png` + CSS/file path + commit
  - Acceptance:
    - Header actions do not create awkward wraps
    - Toolbars are 1-line at ≥1280 OR controlled 2-line pattern (no chaos)
    - Tables never overlap; `.table-wrap` handles overflow safely

- [ ] **1440px hero proof**: premium “recruiter screenshot” captured — **Unknown**
  - Proof: `..._1440.png` + commit

- [ ] **390px mobile guarantee**: header stacks; CTAs tappable; tables scroll — **Unknown**
  - Proof: `..._390.png` + commit

- [ ] **Container + padding**: consistent max-width container + responsive padding — **Unknown**
  - Proof: screenshots at 1280/1440/390 + CSS path + commit
  - Acceptance: consistent gutters; no accidental edge-to-edge; no layout drift

- [ ] **Typography scale**: H1/H2/H3 + body + muted + code defined globally — **Unknown**
  - Proof: CSS tokens + screenshots (2 pages) + commit
  - Acceptance: headings clearly tiered; muted consistent; code readable

- [ ] **Spacing rhythm**: uses defined scale (4/8/12/16/24/32/40/48) — **Unknown**
  - Proof: CSS vars or documented scale + sample pages + commit
  - Acceptance: no random one-off spacing (unless justified)

- [ ] **Component consistency**: buttons/inputs/cards/tables/badges/alerts unified — **Unknown**
  - Proof: app.css component rules + screenshots (3 pages) + commit
  - Acceptance: same component looks/behaves the same across pages

- [ ] **Accessibility baseline**: labels, errors, focus states, keyboard usable — **Unknown**
  - Proof: focus screenshots + form error screenshot + commit
  - Acceptance: visible focus ring; labels present; errors readable

- [ ] **State system**: empty/loading/error/success standardized patterns — **Unknown**
  - Proof: partials/shared classes + screenshots + commit
  - Acceptance: no raw empty tables; errors are human-readable; success feedback exists where useful

- [ ] **Overflow safety**: tables/dropdowns/long text never clip or overlap — **Unknown**
  - Proof: long-text screenshots + CSS rules + commit
  - Acceptance: ellipsis/wrap/scroll strategies; no collisions

- [ ] **Breakpoints**: at least **>=900px** and **>=600px** behaviors defined — **Unknown**
  - Proof: media queries + screenshots + commit
  - Acceptance: responsive changes are intentional and tested (not accidental wraps)

---

### 0.2 Responsive Toolbar Standard (P0)
- [ ] **Toolbar rule at ≥1280px**: key toolbars/filters remain **single-line** (unless intentionally 2-row) — **Unknown**
  - Acceptance:
    - Search min-width ≥ 240px
    - Select min-width ≥ 160px
    - Primary actions grouped and aligned right
    - No horizontal scroll in toolbars

- [ ] **900–1279px controlled wrap**: toolbar may become **2 rows max** with consistent spacing — **Unknown**
  - Acceptance: wrap is predictable; actions move to row 2 intentionally

- [ ] **≤600px stacked**: filters/actions stack; buttons can become full-width — **Unknown**
  - Acceptance: touch targets ≥ 44px; no overlap; tables use `.table-wrap`

---

### 0.3 Asset Strategy (no conflicts) (P0)
- [ ] **Global CSS/JS used consistently**: `static/css/app.css`, `static/js/app.js` loaded once — **Unknown**
  - Proof: base.html include + view-source + commit

- [ ] **Page CSS scoped** under wrapper/body class (e.g., `.issues-page`) — **Unknown**
  - Proof: scoped selectors + commit

- [ ] **Page JS guarded** (runs only if wrapper exists) — **Unknown**
  - Proof: app.js guard checks + commit

- [ ] **No duplicate/competing component styles** across CSS files — **Unknown**
  - Proof: grep/diff + final CSS structure + commit

---

### 0.4 Base Layout + Partials (P0)
- [ ] `base.html` blocks exist and are used correctly: `title`, `body_class`, `extra_head`, `content`, `extra_js` — **Unknown**
  - Proof: base.html excerpt + commit

- [ ] Partials exist and are used in 2+ templates:
  - [ ] `_alerts.html`
  - [ ] `_page_header.html`
  - [ ] `_empty_state.html`
  - [ ] `_table_card.html`
  - Proof: file paths + usage grep + commit

- [ ] Global messages styled consistently — **Unknown**
  - Proof: screenshot with message + CSS + commit

---

## 1) Standard Component System (Single Source of Truth)

### 1.1 Buttons (P0)
- [ ] `.btn` + variants: primary/secondary/ghost/danger — **Unknown**
- [ ] Disabled state consistent — **Unknown**
- [ ] Loading state standard (spinner + “Running…”) — **Unknown**
- [ ] Sizes (`.btn-sm`, default) + consistent height — **Unknown**
- Proof: component CSS + screenshot (3 buttons) + commit

### 1.2 Cards (P0)
- [ ] `.card` + `.card-hd` + `.card-bd` + optional `.card-ft` — **Unknown**
- [ ] Card spacing consistent across pages — **Unknown**
- Proof: screenshots from 2 pages + commit

### 1.3 Tables (Dense SaaS) (P0)
- [ ] `.table-wrap` handles horizontal overflow — **Unknown**
- [ ] `.table--dense` row height/padding consistent — **Unknown**
- [ ] Long text strategy: `.clamp`/wrap/tooltip — **Unknown**
- [ ] Empty row looks intentional — **Unknown**
- Proof: long-text screenshot + commit

### 1.4 Forms + Filters (P0)
- [ ] `.field`, `.label`, `.input`, `.select`, `.help`, `.error` — **Unknown**
- [ ] Filter toolbar uses a reusable `.toolbar` / `.filters` component — **Unknown**
- Proof: screenshot at 1280 + 390 + commit

### 1.5 Alerts + Badges (P1)
- [ ] Alerts: info/success/warning/danger — **Unknown**
- [ ] Badges/pills: semantic variants — **Unknown**
- Proof: screenshot showing 2 variants + commit

### 1.6 Tabs + Menus (P1)
- [ ] Tabs accessible (`role="tablist"`, `aria-selected`) — **Unknown**
- [ ] Menus close on outside click + Escape (where used) — **Unknown**
- Proof: screenshot + JS path + commit

---

## 2) Job-First (Hiring Manager Priority)

### 2.1 P0 — Demo-critical templates

#### A) Analytics Dashboard — `templates/analytics/dashboard.html` (P0)
- [ ] Clear hierarchy: H1 + subtitle + primary actions — **Unknown**
- [ ] KPI grid consistent tiles + responsive stacking — **Unknown**
- [ ] Time window controls accessible, no overflow (≥1280 single-line) — **Unknown**
- [ ] Data freshness cue (“Last updated”) — **Unknown**
- [ ] Chart readability: no tick label overflow; consistent card headers — **Unknown**
- [ ] Empty state (no data) — **Unknown**
- [ ] Error state (query/snapshot failure) — **Unknown**
- [ ] Proof screenshots: 1280 + 1440 + 390 — **Unknown**

#### B) Monitoring Issues — `templates/monitoring/issues.html` (P0)
- [ ] Clear header: “Data Quality Monitoring” + CTA “Run Checks” — **Unknown**
- [ ] Run Checks: disabled + “Running…” prevents double-submit — **Unknown**
- [ ] KPI tiles: Total/Open/Resolved/Last Run correct — **Unknown**
- [ ] Filters single-line at ≥1280; controlled wrap 900–1279; stacked at ≤600 — **Unknown**
- [ ] Table: no overlap (Ref never collides with Status/Resolved) — **Unknown**
- [ ] Long text wraps/clamps cleanly; no row breakage — **Unknown**
- [ ] Dropdowns not clipped/overflowing — **Unknown**
- [ ] “View” works (no 403) — **Unknown**
- [ ] Export CSV respects filters/sort — **Unknown**
- [ ] Empty state styled (“No issues detected.”) — **Unknown**
- [ ] Error state banner on failure — **Unknown**
- [ ] Proof screenshots: 1280 + 1440 + 390 + (empty + running + error) — **Unknown**

#### C) Order Detail — `templates/orders/order_detail.html` (P0)
- [ ] Summary card: status badge, totals, timestamps — **Unknown**
- [ ] Refund tracking fields visible + labeled — **Unknown**
- [ ] Canonical lifecycle status names — **Unknown**
- [ ] Ops/admin actions grouped + RBAC protected — **Unknown**
- [ ] Items table uses `.table-wrap` + `.table--dense` — **Unknown**
- [ ] Empty states for items/refunds — **Unknown**
- [ ] Proof screenshots: 1280 + 1440 + 390 — **Unknown**

#### D) Checkout — `templates/orders/checkout.html` (P0)
- [ ] Clear sections (Summary → Address → Payment) — **Unknown**
- [ ] Form alignment + validation messaging — **Unknown**
- [ ] CTA alignment consistent — **Unknown**
- [ ] Error states: empty cart / invalid order — **Unknown**
- [ ] Proof screenshots: 1280 + 1440 + 390 — **Unknown**

#### E) Stripe Checkout — `templates/payments/stripe_checkout.html` (P0)
- [ ] Trust cues + clear payment initiation panel — **Unknown**
- [ ] Order summary + amount clear — **Unknown**
- [ ] Mock/Stripe-disabled messaging clean — **Unknown**
- [ ] Errors actionable (no raw exceptions) — **Unknown**
- [ ] Proof screenshots: 1280 + 1440 + 390 — **Unknown**

#### F) Account Dashboard — `templates/accounts/account_dashboard.html` (P0)
- [ ] Role-aware panels + quick links — **Unknown**
- [ ] Proof widgets: open issues / last run / snapshot — **Unknown**
- [ ] Empty state for new accounts — **Unknown**
- [ ] Proof screenshots: 1280 + 1440 + 390 — **Unknown**

#### G) Login — `templates/registration/login.html` (P0)
- [ ] Enterprise login look (not default Django) — **Unknown**
- [ ] Accessible labels + errors + focus states — **Unknown**
- [ ] Optional dev-only demo hint (no prod leakage) — **Unknown**
- [ ] Proof screenshots: 1280 + 1440 + 390 — **Unknown**

---

## 3) Sale-Ready (Buyer Priority)

### 3.1 P0 — Buyer conversion flow

#### H) Base Shell — `templates/base.html` (P0)
- [ ] Global nav responsive + active state — **Unknown**
- [ ] Global messages render + styled — **Unknown**
- [ ] Page CSS/JS blocks included without duplication — **Unknown**
- [ ] Footer minimal + optional build/version label — **Unknown**

#### I) Home — `templates/core/home.html` (P1)
- [ ] Value prop: “Stripe Revenue Intelligence” clear — **Unknown**
- [ ] CTA: Login / Dashboard / Monitoring — **Unknown**
- [ ] Credibility bullets (controls + reporting + CI gates) — **Unknown**
- [ ] Proof screenshots: 1280 + 1440 + 390 — **Unknown**

#### J) Product List — `templates/products/product_list.html` (P1)
- [ ] Grid/cards consistent with global system — **Unknown**
- [ ] Pagination styled — **Unknown**
- [ ] Empty state + CTA — **Unknown**
- [ ] Optional: minimal sort/filter UI — **Unknown**
- [ ] Proof screenshots: 1280 + 1440 + 390 — **Unknown**

#### K) Product Detail — `templates/products/product_detail.html` (P1)
- [ ] Product hero: price/stock/CTA clear — **Unknown**
- [ ] Out-of-stock state — **Unknown**
- [ ] Optional: related products — **Unknown**
- [ ] Trust cues (refund/shipping/secure pay) — **Unknown**
- [ ] Proof screenshots: 1280 + 1440 + 390 — **Unknown**

#### L) Cart — `templates/cart/cart.html` (P1)
- [ ] Stable cart table layout — **Unknown**
- [ ] Quantity controls aligned — **Unknown**
- [ ] Totals summary card consistent — **Unknown**
- [ ] Empty cart state — **Unknown**
- [ ] Proof screenshots: 1280 + 1440 + 390 — **Unknown**

#### M) Wishlist — `wishlist/templates/wishlist/my_wishlist.html` (P1)
- [ ] Clean list/grid + add-to-cart action — **Unknown**
- [ ] Empty state + CTA — **Unknown**
- [ ] Consistent cards/buttons — **Unknown**
- [ ] Proof screenshots: 1280 + 1440 + 390 — **Unknown**

---

## 4) Subscriptions (Sale Supporting)

#### N) My Subscriptions — `templates/subscriptions/my_subscriptions.html` (P2)
- [ ] List/table with status badges + actions — **Unknown**
- [ ] Empty state — **Unknown**
- [ ] Canonical naming (canceled vs cancelled) — **Unknown**
- [ ] Proof screenshots: 1280 + 1440 + 390 — **Unknown**

#### O) Confirm Subscription — `templates/subscriptions/confirm_subscription.html` (P2)
- [ ] Plan summary + price + cadence — **Unknown**
- [ ] Confirm + cancel paths — **Unknown**
- [ ] Error states — **Unknown**
- [ ] Proof screenshots: 1280 + 1440 + 390 — **Unknown**

#### P) Add Payment Method — `templates/subscriptions/add_payment_method.html` (P2)
- [ ] Clear form + secure messaging — **Unknown**
- [ ] Works in mock mode — **Unknown**
- [ ] Error states — **Unknown**
- [ ] Proof screenshots: 1280 + 1440 + 390 — **Unknown**

---

## 5) Professional Proof Pack (required for credibility)

### 5.1 Screenshot rules (each template) (P0)
- [ ] Desktop **1280px** screenshot — **Unknown**
- [ ] Hero **1440px** screenshot — **Unknown**
- [ ] Mobile **390px** screenshot — **Unknown**
- [ ] Empty state screenshot (if applicable) — **Unknown**
- [ ] Error state screenshot (if applicable) — **Unknown**
- [ ] Running/loading screenshot (if page has actions) — **Unknown**

### 5.2 Storage location (P0)
- [ ] Saved under `docs/proof/demo/` — **Unknown**

### 5.3 Filename standard (date-stamped) (P0)
- [ ] `YYYY-MM-DD_now_<page>_1280.png` — **Unknown**
- [ ] `YYYY-MM-DD_now_<page>_1440.png` — **Unknown**
- [ ] `YYYY-MM-DD_now_<page>_390.png` — **Unknown**
- [ ] Optional: `..._empty.png`, `..._error.png`, `..._running.png` — **Unknown**
- [ ] Optional target mock: `YYYY-MM-DD_target_<page>_1440.png` — **Unknown**

---

## 6) Pass Criteria (must be green before moving on) (P0)

For each template step:
- [ ] Page renders with no Django errors — **Unknown**
- [ ] No console errors — **Unknown**
- [ ] No overflow/clipping at **1280 + 1440 + 390** — **Unknown**
- [ ] Buttons/inputs aligned; consistent component styles — **Unknown**
- [ ] Empty/loading/error states present & readable — **Unknown**
- [ ] CSS scoped, JS guarded, no global conflicts — **Unknown**
- [ ] Proof screenshots captured + stored with correct filename — **Unknown**
- [ ] Proof line added: **URL + screenshot path + file path + commit hash** — **Unknown**

---

## 7) Execution Order (strict sequence)

### Phase A — Job-First P0
1) Analytics Dashboard  
2) Monitoring Issues  
3) Order Detail  
4) Checkout  
5) Stripe Checkout  
6) Account Dashboard  
7) Login  

### Phase B — Sale-Ready P1
8) Home  
9) Product List  
10) Product Detail  
11) Cart  
12) Wishlist  

### Phase C — Subscriptions P2
13) My Subscriptions  
14) Confirm Subscription  
15) Add Payment Method  

### Phase D — Base extraction + proof indexing
16) Extract partials + standardize base  
17) Final demo screenshot pack + proof index update

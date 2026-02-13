/* File: static/js/orders.js */
/* Orders JS — guarded by data-* root, page-scoped, null-safe. */
(function () {
  const body = document.body;
  if (!body || !body.classList.contains("orders-page")) return;

  // Data-root guard (required by project rules)
  const pageRoot =
    document.querySelector("[data-orders-root]") ||
    document.querySelector("[data-orders-detail-root]") ||
    document.querySelector("[data-orders-list-root]");

  if (!pageRoot) return;

  /* -----------------------------
   * 1) Copy buttons (data-copy)
   * ----------------------------- */
  const copyButtons = pageRoot.querySelectorAll("[data-copy]");
  const hasCopy = copyButtons && copyButtons.length > 0;

  async function copyText(text) {
    if (!text) return false;

    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
        return true;
      }
    } catch (_) {
      // fall back
    }

    try {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "absolute";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      ta.setSelectionRange(0, ta.value.length);
      const ok = document.execCommand("copy");
      document.body.removeChild(ta);
      return ok;
    } catch (_) {
      return false;
    }
  }

  function pulseButton(btn, ok) {
    const original = btn.textContent;
    const originalAria = btn.getAttribute("aria-label") || "";

    btn.textContent = ok ? "Copied" : "Failed";
    btn.disabled = true;
    btn.setAttribute("aria-label", ok ? "Copied" : "Copy failed");

    window.setTimeout(() => {
      btn.textContent = original;
      btn.disabled = false;
      if (originalAria) btn.setAttribute("aria-label", originalAria);
      else btn.removeAttribute("aria-label");
    }, 900);
  }

  if (hasCopy) {
    copyButtons.forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        // Prevent accidental submit if button is inside a form
        e.preventDefault();

        const sel = btn.getAttribute("data-copy");
        const node = sel ? pageRoot.querySelector(sel) : null;

        let text = "";
        if (node) {
          if (node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement) {
            text = (node.value || "").trim();
          } else {
            text = (node.textContent || "").trim();
          }
        }

        const ok = await copyText(text);
        pulseButton(btn, ok);
      });
    });
  }

  /* -----------------------------------------
   * 2) Checkout submit guard (double-submit)
   * ----------------------------------------- */
  const checkoutForm = pageRoot.querySelector("[data-checkout-form]");
  if (checkoutForm) {
    checkoutForm.addEventListener("submit", () => {
      const submits = checkoutForm.querySelectorAll(
        'button[type="submit"], input[type="submit"]'
      );
      if (!submits || !submits.length) return;

      submits.forEach((el) => {
        if (el instanceof HTMLButtonElement) {
          if (!el.dataset.prevText) el.dataset.prevText = el.textContent || "";
          el.textContent = "Processing…";
        }
        el.disabled = true;
      });
    });
  }

  /* -------------------------------------------------
   * 3) Confirm dangerous actions (optional hooks)
   * ------------------------------------------------- */
  const confirmEls = pageRoot.querySelectorAll("[data-confirm]");
  if (confirmEls && confirmEls.length) {
    confirmEls.forEach((el) => {
      el.addEventListener("click", (e) => {
        const msg = el.getAttribute("data-confirm") || "Are you sure?";
        if (!window.confirm(msg)) {
          e.preventDefault();
          e.stopPropagation();
        }
      });
    });
  }
})();

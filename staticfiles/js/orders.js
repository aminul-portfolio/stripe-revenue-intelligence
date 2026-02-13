/* File: static/js/orders.js */
/* Orders JS — guarded, page-scoped. Safe if selectors not present. */
(function () {
  const root = document.body;
  if (!root || !root.classList.contains("orders-page")) return;

  /* -----------------------------
   * 1) Copy buttons (data-copy)
   * ----------------------------- */
  const copyButtons = document.querySelectorAll("[data-copy]");
  const hasCopy = copyButtons && copyButtons.length > 0;

  async function copyText(text) {
    if (!text) return false;

    // Modern clipboard API
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
        return true;
      }
    } catch (_) {
      // fall back
    }

    // Fallback: execCommand
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
      btn.addEventListener("click", async () => {
        const sel = btn.getAttribute("data-copy");
        const node = sel ? document.querySelector(sel) : null;

        // Prefer value for inputs, fallback to textContent
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
  const checkoutForm = document.querySelector("[data-checkout-form]");
  if (checkoutForm) {
    checkoutForm.addEventListener("submit", () => {
      // disable all submit buttons in the form
      const submits = checkoutForm.querySelectorAll('button[type="submit"], input[type="submit"]');
      if (!submits || !submits.length) return;

      submits.forEach((el) => {
        // button text swap for nicer UX
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
   * -------------------------------------------------
   * Add data-confirm="Are you sure?" to any button/input
   * and this will guard it without page errors.
   */
  const confirmEls = document.querySelectorAll("[data-confirm]");
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

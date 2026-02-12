/* =========================================
   Dashboard-only JS
   File: analyticsapp/static/analyticsapp/js/dashboard.js

   Responsibilities:
   - dashboard-specific interactions
   - Plotly rendering (safe + race-proof)
   - Exports <details> close on outside click + Escape
   ========================================= */

(function () {
  "use strict";

  // Only run on dashboard pages
  const dashRoot = document.querySelector(".dash-shell");
  if (!dashRoot) return;

  /* ---------------------------------------
     Exports <details> helper (dashboard only)
     --------------------------------------- */
  document.addEventListener("click", (e) => {
    const openDetails = document.querySelector("details.menu[open]");
    if (!openDetails) return;

    // Click outside closes
    if (!e.target.closest("details.menu")) {
      openDetails.removeAttribute("open");
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    const openDetails = document.querySelector("details.menu[open]");
    if (openDetails) openDetails.removeAttribute("open");
  });

  /* ---------------------------------------
     Plotly rendering (dashboard-only)
     - Reads JSON from <script id="dash-plots" type="application/json">
     - Waits for Plotly (since Plotly is loaded with `defer`)
     --------------------------------------- */

  function readPlotsPayload() {
    const el = document.getElementById("dash-plots");
    if (!el) {
      console.warn("[dashboard] Missing #dash-plots payload script tag.");
      return null;
    }

    try {
      return JSON.parse(el.textContent);
    } catch (err) {
      console.error("[dashboard] Invalid JSON in #dash-plots.", err);
      return null;
    }
  }

  function renderPlot(divId, fig, cfg) {
    const node = document.getElementById(divId);
    if (!node) return;

    if (!fig || !fig.data || !fig.layout) {
      console.warn(`[dashboard] Plot payload missing for ${divId}`);
      return;
    }

    // newPlot overwrites safely (idempotent)
    Plotly.newPlot(divId, fig.data, fig.layout, cfg);
  }

  function initPlots() {
    const plots = readPlotsPayload();
    if (!plots) return;

    const cfg = {
      displayModeBar: false,
      responsive: true,
      scrollZoom: false,
    };

    renderPlot("revenue-daily", plots.revenueDaily, cfg);
    renderPlot("orders-daily", plots.ordersDaily, cfg);
    renderPlot("refunds-daily", plots.refundsDaily, cfg);

    renderPlot("product-units", plots.productUnitsBar, cfg);
    renderPlot("product-rev", plots.productRevBar, cfg);
    renderPlot("churn-line", plots.churnLine, cfg);
    renderPlot("funnel", plots.funnelFig, cfg);
  }

  function waitForPlotlyThenInit() {
    const maxWaitMs = 8000;
    const start = Date.now();

    const timer = setInterval(() => {
      if (typeof window.Plotly !== "undefined") {
        clearInterval(timer);
        initPlots();
        return;
      }

      if (Date.now() - start > maxWaitMs) {
        clearInterval(timer);
        console.error("[dashboard] Plotly did not load within timeout.");
      }
    }, 50);
  }

  // Run after full load so deferred scripts are ready.
  window.addEventListener("load", waitForPlotlyThenInit);
})();

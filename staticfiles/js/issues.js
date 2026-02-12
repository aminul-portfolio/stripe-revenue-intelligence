// File: static/js/issues.js

(function () {
  // Guard: only run on Issues page
  const isIssuesPage = document.body && document.body.classList.contains("issues-page");
  if (!isIssuesPage) return;

  const form = document.querySelector("[data-issues-run-form]");
  const btn = document.querySelector("[data-issues-run-btn]");
  const label = btn ? btn.querySelector(".issues__run-label") : null;

  if (!form || !btn) return;

  form.addEventListener("submit", function () {
    // Prevent double submits + show “Running…” state
    btn.classList.add("is-loading");
    btn.setAttribute("disabled", "disabled");
    if (label) label.textContent = "Running…";
  });
})();

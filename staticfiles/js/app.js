/* =========================================
   Global app.js
   - shared utilities
   - shared UI behaviors (wishlist hearts)
   ========================================= */

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Expose for other bundles (dashboard.js etc.)
window.PureLaka = window.PureLaka || {};
window.PureLaka.getCookie = getCookie;

/* -------------------------
   Wishlist hearts (global)
   ------------------------- */
document.addEventListener("click", async (e) => {
  const btn = e.target.closest(".heart");
  if (!btn) return;

  const pid = btn.getAttribute("data-product");
  if (!pid) return;

  try {
    const res = await fetch(`/wishlist/toggle/${pid}/`, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
    });

    // defensive: only parse JSON when ok
    if (!res.ok) {
      console.error("Wishlist toggle failed:", res.status);
      return;
    }

    const data = await res.json();
    btn.textContent = data.liked ? "♥" : "♡";
  } catch (err) {
    console.error(err);
  }
});

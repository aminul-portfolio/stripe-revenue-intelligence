function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

document.addEventListener("click", async (e) => {
  const btn = e.target.closest(".heart");
  if (!btn) return;
  const pid = btn.getAttribute("data-product");
  if (!pid) return;

  try {
    const res = await fetch(`/wishlist/toggle/${pid}/`, {
      method: "POST",
      headers: {"X-CSRFToken": getCookie("csrftoken")},
    });
    const data = await res.json();
    btn.textContent = data.liked ? "♥" : "♡";
  } catch (err) {
    console.error(err);
  }
});


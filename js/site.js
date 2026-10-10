(function () {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var pre = document.querySelector(".preloader");
  var seen = false;
  try {
    seen = sessionStorage.getItem("cch-seen") === "1";
    sessionStorage.setItem("cch-seen", "1");
  } catch (e) {
    seen = false;
  }

  function finish() {
    if (!pre) return;
    pre.classList.add("is-done");
    window.setTimeout(function () {
      pre.remove();
    }, 480);
  }

  var nodes = document.querySelectorAll("[data-count]");
  function paint(value) {
    nodes.forEach(function (node) {
      var target = Number(node.getAttribute("data-count") || 0);
      node.textContent = String(Math.round(target * value));
    });
  }

  var sheet = document.querySelector(".sheet");
  var played = false;
  function play() {
    if (played) return;
    played = true;
    if (sheet) sheet.classList.add("seen");
    if (!nodes.length) return;
    if (reduce) {
      paint(1);
      return;
    }
    var start = performance.now();
    function tick(now) {
      var t = Math.min(1, (now - start) / 900);
      paint(1 - Math.pow(1 - t, 3));
      if (t < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  if (reduce) {
    finish();
    play();
  } else {
    window.setTimeout(finish, seen ? 420 : 1250);
    if (sheet && "IntersectionObserver" in window) {
      var fallback = window.setTimeout(play, 2600);
      var observer = new IntersectionObserver(
        function (entries) {
          if (entries.some(function (entry) { return entry.isIntersecting; })) {
            window.clearTimeout(fallback);
            play();
            observer.disconnect();
          }
        },
        { threshold: 0.18 }
      );
      observer.observe(sheet);
    } else {
      play();
    }
  }

  document.querySelectorAll("[data-file]").forEach(function (slot) {
    if (!slot.textContent.trim()) {
      var name = location.pathname.split("/").filter(Boolean).pop() || "index.html";
      slot.textContent = name;
    }
  });
})();

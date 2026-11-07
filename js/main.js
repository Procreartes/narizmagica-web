(function () {
  "use strict";
  try { document.documentElement.classList.remove("sin-js"); } catch (e) {}
  var $ = function (s) { return document.querySelector(s); };

  // Menú móvil
  try {
    var boton = $(".boton-menu"), menu = $("#menu");
    if (boton && menu) {
      var cerrar = function () { menu.classList.remove("abierto"); boton.setAttribute("aria-expanded", "false"); };
      boton.addEventListener("click", function () { boton.setAttribute("aria-expanded", menu.classList.toggle("abierto") ? "true" : "false"); });
      menu.addEventListener("click", function (e) { if (e.target.tagName === "A") cerrar(); });
      document.addEventListener("keydown", function (e) { if (e.key === "Escape") cerrar(); });
    }
  } catch (e) {}

  // Aparición al hacer scroll
  try {
    var el = Array.prototype.slice.call(document.querySelectorAll(".aparece"));
    if ("IntersectionObserver" in window) {
      var obs = new IntersectionObserver(function (en) {
        en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add("visible"); obs.unobserve(x.target); } });
      }, { rootMargin: "0px 0px -8% 0px" });
      el.forEach(function (x) { obs.observe(x); });
    } else { el.forEach(function (x) { x.classList.add("visible"); }); }
  } catch (e) {}

  try { var a = $("#anio"); if (a) a.textContent = String(new Date().getFullYear()); } catch (e) {}
})();

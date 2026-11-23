/* Ajustes de diseno que dependen de lo que hay en cada pagina. */
(function () {
  'use strict';
  function listo(fn) { document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn); }

  // En iPhone/iPad el estilo :active (efecto al tocar las tarjetas) solo funciona si hay un listener de toque.
  document.addEventListener('touchstart', function () {}, { passive: true });

  // Formularios con validacion propia (novalidate): si falta completar algo, NO se envia,
  // no se muestra "Enviando…" y se lleva al primer campo con problema.
  // Va en fase de captura para frenar el envio antes que los onsubmit de cada plantilla.
  document.addEventListener('submit', function (ev) {
    var form = ev.target;
    if (!(form instanceof HTMLFormElement) || !form.noValidate || form.checkValidity()) return;
    ev.preventDefault();
    ev.stopPropagation();
    form.classList.add('was-validated');
    var invalidos = form.querySelectorAll(':invalid');
    var aviso = form.querySelector('.aviso-faltantes');
    if (!aviso) {
      aviso = document.createElement('div');
      aviso.className = 'aviso-faltantes alert alert-danger mt-2';
      aviso.setAttribute('role', 'alert');
      var btn = form.querySelector('[type="submit"]');
      (btn ? btn.parentNode : form).insertBefore(aviso, btn || null);
    }
    var n = Array.prototype.filter.call(invalidos, function (e) { return e.tagName !== 'FIELDSET'; }).length;
    aviso.textContent = n === 1 ? 'Falta completar 1 campo (marcado en rojo).' : 'Faltan completar ' + n + ' campos (marcados en rojo).';
    if (invalidos[0]) {
      invalidos[0].scrollIntoView({behavior: 'smooth', block: 'center'});
      try { invalidos[0].focus({preventScroll: true}); } catch (e) {}
    }
  }, true);

  // Al corregir, el aviso se actualiza o desaparece
  document.addEventListener('input', function (ev) {
    var form = ev.target.form;
    if (!form) return;
    var aviso = form.querySelector('.aviso-faltantes');
    if (aviso && form.checkValidity()) aviso.remove();
  }, true);

  listo(function () {
    // Sin menu lateral: el contenido usa todo el ancho
    if (!document.getElementById('sidebar')) document.body.classList.add('sin-menu');

    // Tablas que no estan dentro de una caja con desplazamiento: se envuelven
    document.querySelectorAll('#main table').forEach(function (t) {
      var cols = (t.rows[0] && t.rows[0].cells.length) || 0;
      if (cols > 3) t.classList.add('tabla-ancha');
      var p = t.parentElement;
      if (p.classList.contains('dataTable-container') || p.classList.contains('table-responsive') || p.classList.contains('tabla-scroll')) return;
      var caja = document.createElement('div');
      caja.className = 'tabla-scroll';
      p.insertBefore(caja, t);
      caja.appendChild(t);
    });

    // Aviso "desliza" solo si la tabla realmente es mas ancha que la pantalla
    function revisarAnchos() {
      document.querySelectorAll('.tabla-scroll, .dataTable-container').forEach(function (c) {
        var aviso = c.previousElementSibling;
        if (!aviso || !aviso.classList.contains('aviso-deslizar')) {
          aviso = document.createElement('div');
          aviso.className = 'aviso-deslizar';
          aviso.textContent = 'Deslizá la tabla hacia los costados para ver todas las columnas →';
          c.parentElement.insertBefore(aviso, c);
        }
        aviso.classList.toggle('visible', c.scrollWidth > c.clientWidth + 4);
      });
    }
    revisarAnchos();
    setTimeout(revisarAnchos, 800);          // las tablas con buscador se arman un poco despues
    window.addEventListener('resize', revisarAnchos);

    // Celular / tablet (o pantalla angosta): al deslizar, la tarjeta de evento mas cerca del
    // centro de la pantalla se agranda un poco (clase .tarjeta-centrada, ver tema.css).
    // Se evalua en cada movimiento, asi tambien funciona en la vista celular del navegador.
    var tarjetas = document.querySelectorAll('.grilla-eventos .tarjeta-evento');
    var sinMovimiento = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (tarjetas.length && !sinMovimiento) {
      var actual = null, pendiente = false;
      function modoCelular() {
        return window.innerWidth < 768 || (window.matchMedia && window.matchMedia('(hover: none)').matches);
      }
      function centrar() {
        pendiente = false;
        var mejor = null;
        if (modoCelular()) {
          var medio = window.innerHeight / 2, distMejor = Infinity;
          tarjetas.forEach(function (t) {
            var r = t.getBoundingClientRect();
            if (r.bottom < 0 || r.top > window.innerHeight) return;   // fuera de la pantalla
            var d = Math.abs(r.top + r.height / 2 - medio);
            if (d < distMejor) { distMejor = d; mejor = t; }
          });
          // solo si la tarjeta esta razonablemente cerca del centro de la pantalla
          if (mejor && distMejor > window.innerHeight * 0.35) mejor = null;
          // para que no salte de una tarjeta a otra cuando estan casi igual de centradas,
          // se cambia solo si la nueva esta bastante mas cerca del centro que la actual
          if (mejor && actual && mejor !== actual) {
            var ra = actual.getBoundingClientRect();
            var dActual = Math.abs(ra.top + ra.height / 2 - medio);
            if (dActual <= window.innerHeight * 0.35 && dActual - distMejor < 60) mejor = actual;
          }
        }
        if (mejor === actual) return;
        if (actual) actual.classList.remove('tarjeta-centrada');
        if (mejor) mejor.classList.add('tarjeta-centrada');
        actual = mejor;
      }
      function pedir() { if (!pendiente) { pendiente = true; window.requestAnimationFrame(centrar); } }
      window.addEventListener('scroll', pedir, { passive: true });
      document.addEventListener('scroll', pedir, { passive: true, capture: true });  // por si se desplaza otro contenedor
      window.addEventListener('resize', pedir);
      setTimeout(centrar, 600);   // despues de la animacion de entrada
    }

    // Foto de perfil rota en el encabezado: se reemplaza por un icono
    document.querySelectorAll('#header img').forEach(function (img) {
      function poner() {
        if (img.closest('.logo')) return;
        var i = document.createElement('i');
        i.className = 'bi bi-person-circle foto-perfil-vacia';
        img.replaceWith(i);
      }
      if (img.complete && img.naturalWidth === 0 && img.getAttribute('src')) poner();
      else img.addEventListener('error', poner);
    });
  });
})();

/* Menu lateral: marca el item de la pagina actual (el de direccion mas larga que coincida). */
(function () {
  var links = document.querySelectorAll('.menu-vivo .sidebar-nav a.nav-link[href]');
  var aqui = location.pathname, mejor = null, largo = 0;
  links.forEach(function (a) {
    var p = a.pathname;
    if (!p || p === '/' || a.getAttribute('href') === '#') return;
    var base = p.replace(/\/$/, '');
    if ((aqui === p || aqui.indexOf(base + '/') === 0 || aqui === base) && p.length > largo) { mejor = a; largo = p.length; }
  });
  if (mejor) mejor.classList.add('activo');
})();

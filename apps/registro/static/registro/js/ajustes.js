/* Ajustes de diseno que dependen de lo que hay en cada pagina. */
(function () {
  'use strict';
  function listo(fn) { document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn); }

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

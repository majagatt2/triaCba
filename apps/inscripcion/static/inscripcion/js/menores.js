/*
 * Inscripcion sin cuenta: el recuadro del adulto responsable aparece solo si,
 * por la fecha de nacimiento, la persona tiene menos de 18 anios el dia del evento.
 * Mientras se ve, sus datos principales son obligatorios.
 */
(function () {
  'use strict';
  document.addEventListener('DOMContentLoaded', function () {
    var panel = document.getElementById('panel-menores');
    var nacimiento = document.getElementById('id_fechaNacimiento');
    if (!panel || !nacimiento) return;
    var obligatorios = ['id_responsable_tutor', 'id_dni_responsable', 'id_telefono_responsable']
      .map(function (id) { return document.getElementById(id); }).filter(Boolean);
    var relacion = document.getElementById('id_relacion_legal');

    function edadAlEvento(valor) {
      var partes = (valor || '').split('-');
      if (partes.length !== 3) return null;
      var n = { a: +partes[0], m: +partes[1], d: +partes[2] };
      var ev = (panel.dataset.fechaEvento || '').split('-');
      var f = ev.length === 3 ? { a: +ev[0], m: +ev[1], d: +ev[2] } : (function () { var h = new Date(); return { a: h.getFullYear(), m: h.getMonth() + 1, d: h.getDate() }; })();
      if (!n.a || n.a < 1900) return null;
      return f.a - n.a - ((f.m < n.m || (f.m === n.m && f.d < n.d)) ? 1 : 0);
    }

    function revisarRelacion() {
      if (!relacion) return;
      relacion.setCustomValidity(!panel.hidden && (relacion.value === '' || relacion.value === '1')
        ? 'Elegí qué relación tiene con vos.' : '');
    }

    function actualizar(desplazar) {
      var edad = edadAlEvento(nacimiento.value);
      var menor = edad !== null && edad < 18;
      var antes = panel.hidden;
      panel.hidden = !menor;
      obligatorios.forEach(function (c) { c.required = menor; });
      revisarRelacion();
      if (menor && antes && desplazar) panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    nacimiento.addEventListener('change', function () { actualizar(true); });
    nacimiento.addEventListener('input', function () { actualizar(false); });
    if (relacion) relacion.addEventListener('change', revisarRelacion);
    actualizar(false);
  });
})();

/*
 * Formulario de inscripcion: la lista de formas de pago muestra solo los costos de la
 * modalidad elegida (select id_evento). Cada <option> de id_formaPago trae
 * data-modalidades="163 164 " (ids de las modalidades); si esta vacio, el costo vale
 * para todas las modalidades. El monto (id_montoDebeAbonar) sigue encadenado con
 * jquery.chained a la forma de pago. El servidor aplica la misma regla.
 */
(function () {
  'use strict';
  document.addEventListener('DOMContentLoaded', function () {
    var sel = document.getElementById('id_formaPago');
    var modalidad = document.getElementById('id_evento');
    if (!sel || !modalidad) return;

    var costos = [];
    var vistos = {};
    Array.prototype.forEach.call(sel.querySelectorAll('option[data-modalidades]'), function (o) {
      if (vistos[o.value]) return;  // el template puede repetir opciones
      vistos[o.value] = true;
      costos.push({ valor: o.value, texto: o.textContent,
                    modalidades: (o.dataset.modalidades || '').trim().split(/\s+/).filter(Boolean) });
    });

    function aplica(c, m) { return !c.modalidades.length || c.modalidades.indexOf(m) > -1; }

    function armar() {
      var m = modalidad.value;
      var elegida = /^\d+$/.test(m) && m !== '0';
      var lista = elegida ? costos.filter(function (c) { return aplica(c, m); }) : [];
      var actual = sel.value;

      sel.innerHTML = '';
      sel.add(new Option(elegida ? 'Elegí la forma de pago' : 'Primero elegí tu modalidad', ''));
      lista.forEach(function (c) { sel.add(new Option(c.texto, c.valor, false, c.valor === actual)); });
      sel.disabled = !elegida;

      // avisar a jquery.chained para que actualice el monto
      if (window.jQuery) window.jQuery(sel).trigger('change');
    }

    modalidad.addEventListener('change', armar);
    if (window.jQuery) window.jQuery(modalidad).on('change', armar);
    armar();
  });
})();

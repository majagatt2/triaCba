/*
 * Formulario de inscripcion: la lista de categorias muestra solo las de la modalidad elegida
 * y, si se conoce la fecha de nacimiento, solo las que corresponden a la edad de la persona
 * a la "fecha de calculo de edad" del evento (y a su sexo, si la categoria lo indica).
 *
 * Datos que usa (atributos del <select id="id_categoria">):
 *   data-fecha-calculo  fecha de calculo de edad del evento (AAAA-MM-DD)
 *   data-nacimiento / data-sexo  datos del usuario con cuenta (en el form publico se leen
 *                                de los campos id_fechaNacimiento / id_sexo)
 *   data-elegida        categoria elegida antes (cuando el form vuelve con errores)
 * Cada <option>: data-chained (id de la modalidad), data-desde, data-hasta, data-sexo.
 * Si ninguna categoria corresponde, se muestran todas para no bloquear la inscripcion
 * (el servidor aplica la misma regla).
 */
(function () {
  'use strict';
  document.addEventListener('DOMContentLoaded', function () {
    var sel = document.getElementById('id_categoria');
    var modalidad = document.getElementById('id_evento');
    if (!sel || !modalidad) return;
    var campoNac = document.getElementById('id_fechaNacimiento');
    var campoSexo = document.getElementById('id_sexo');
    var aviso = document.getElementById('aviso-categorias');
    var elegida = sel.dataset.elegida || '';

    function numero(v) { return v === '' || v == null ? null : parseInt(v, 10); }
    function fecha(v) {
      var p = (v || '').split('-');
      return p.length === 3 && +p[0] > 1900 ? { a: +p[0], m: +p[1], d: +p[2] } : null;
    }

    var todas = Array.prototype.map.call(sel.querySelectorAll('option[data-chained]'), function (o) {
      return { valor: o.value, texto: o.textContent, modalidad: String(o.dataset.chained),
               desde: numero(o.dataset.desde), hasta: numero(o.dataset.hasta), sexo: o.dataset.sexo || '' };
    });
    var calculo = fecha(sel.dataset.fechaCalculo);
    var fechaCalculoTexto = calculo ? ('0' + calculo.d).slice(-2) + '/' + ('0' + calculo.m).slice(-2) + '/' + calculo.a : '';

    function edad() {
      var n = fecha(sel.dataset.nacimiento || (campoNac && campoNac.value));
      if (!n || !calculo) return null;
      return calculo.a - n.a - ((calculo.m < n.m || (calculo.m === n.m && calculo.d < n.d)) ? 1 : 0);
    }
    function sexo() { return sel.dataset.sexo || (campoSexo && campoSexo.value) || ''; }
    function corresponde(c, e, s) {
      if (e !== null && ((c.desde !== null && e < c.desde) || (c.hasta !== null && e > c.hasta))) return false;
      return !(s && c.sexo && c.sexo !== s);
    }

    function armar() {
      var e = edad(), s = sexo();
      var deModalidad = todas.filter(function (c) { return c.modalidad === modalidad.value; });
      var aptas = deModalidad.filter(function (c) { return corresponde(c, e, s); });
      var lista = aptas.length ? aptas : deModalidad;
      var actual = sel.value && sel.value !== '0' ? sel.value : elegida;

      sel.innerHTML = '';
      var primera = new Option(deModalidad.length ? 'Elegí tu categoría' : 'Primero elegí el evento', '');
      sel.add(primera);
      var vistos = {};
      lista.forEach(function (c) {
        if (vistos[c.valor]) return;
        vistos[c.valor] = true;
        sel.add(new Option(c.texto, c.valor, false, c.valor === actual));
      });
      if (lista.length === 1) sel.selectedIndex = 1;
      sel.disabled = !deModalidad.length;

      if (!aviso) return;
      var texto = '';
      if (deModalidad.length) {
        if (e === null) {
          if (campoNac && todas.some(function (c) { return c.desde !== null || c.hasta !== null; }))
            texto = 'Completá tu fecha de nacimiento para ver solo las categorías de tu edad.';
        } else if (!aptas.length) {
          texto = 'No encontramos una categoría para tu edad (' + e + ' años al ' + fechaCalculoTexto + '). Elegí la que corresponda.';
        } else if (aptas.length < deModalidad.length) {
          texto = 'Te mostramos las categorías para tu edad: ' + e + ' años al ' + fechaCalculoTexto + '.';
        }
      }
      aviso.textContent = texto;
    }

    function escuchar(campo) {
      if (!campo) return;
      campo.addEventListener('change', armar);
      if (window.jQuery) window.jQuery(campo).on('change', armar); // el form tambien dispara change con jQuery
    }
    escuchar(modalidad);
    escuchar(campoNac);
    escuchar(campoSexo);
    if (campoNac) campoNac.addEventListener('input', armar);
    armar();
  });
})();

/*
 * Archivos de la inscripcion: controla el tamano apenas se elige cada archivo,
 * achica las fotos en el navegador antes de subirlas y muestra el estado del envio.
 * Se activa solo en todos los formularios del sitio que tienen campos para subir archivos
 * (inscripciones, asociarse, pagos, datos personales, registro). Los que no quieren este
 * comportamiento pueden llevar el atributo data-sin-control-archivos.
 */
(function () {
  'use strict';
  if (window.__controlArchivosTriaCba) return;   // por si la pagina lo carga dos veces
  window.__controlArchivosTriaCba = true;

  var LIMITE = 2 * 1024 * 1024;   // mismo limite que valida el servidor (2 MB)
  var LADO_MAX = 1600;            // lado mas largo de la foto achicada, en px
  var CALIDAD = 0.8;              // calidad JPEG

  function kb(bytes) {
    return bytes >= 1024 * 1024
      ? (bytes / 1024 / 1024).toFixed(1).replace('.', ',') + ' MB'
      : Math.round(bytes / 1024) + ' KB';
  }

  function aviso(input) {
    var el = input.parentNode.querySelector('.estado-archivo');
    if (!el) {
      el = document.createElement('div');
      el.className = 'estado-archivo mt-1 small fw-bold';
      input.parentNode.appendChild(el);
    }
    return el;
  }

  function mostrar(input, texto, tipo) {
    var el = aviso(input);
    el.textContent = texto;
    el.style.padding = '4px 8px';
    el.style.borderRadius = '4px';
    if (tipo === 'error') {
      el.style.background = '#b00020'; el.style.color = '#fff';
      input.classList.add('is-invalid');
    } else if (tipo === 'ok') {
      el.style.background = '#1b7f3b'; el.style.color = '#fff';
      input.classList.remove('is-invalid');
    } else {
      el.style.background = '#fff3cd'; el.style.color = '#664d03';
      input.classList.remove('is-invalid');
    }
  }

  function reemplazarArchivo(input, archivo) {
    try {
      var dt = new DataTransfer();
      dt.items.add(archivo);
      input.files = dt.files;
      return true;
    } catch (e) {
      return false;   // navegador viejo: queda el archivo original
    }
  }

  function achicarFoto(archivo) {
    return new Promise(function (resolve, reject) {
      var url = URL.createObjectURL(archivo);
      var img = new Image();
      img.onload = function () {
        var escala = Math.min(1, LADO_MAX / Math.max(img.width, img.height));
        var w = Math.round(img.width * escala), h = Math.round(img.height * escala);
        var canvas = document.createElement('canvas');
        canvas.width = w; canvas.height = h;
        var ctx = canvas.getContext('2d');
        ctx.fillStyle = '#fff';           // fondo blanco para PNG con transparencia
        ctx.fillRect(0, 0, w, h);
        ctx.drawImage(img, 0, 0, w, h);
        URL.revokeObjectURL(url);
        canvas.toBlob(function (blob) {
          if (!blob) { reject(new Error('sin blob')); return; }
          var nombre = archivo.name.replace(/\.[^.]+$/, '') + '.jpg';
          resolve(new File([blob], nombre, {type: 'image/jpeg', lastModified: Date.now()}));
        }, 'image/jpeg', CALIDAD);
      };
      img.onerror = function () { URL.revokeObjectURL(url); reject(new Error('no se pudo leer')); };
      img.src = url;
    });
  }

  function procesar(input) {
    var archivo = input.files && input.files[0];
    input.dataset.procesando = '';
    if (!archivo) { aviso(input).textContent = ''; return Promise.resolve(); }

    var esFoto = /^image\/(jpe?g|png|webp)$/i.test(archivo.type) || /\.(jpe?g|png|webp)$/i.test(archivo.name);

    if (!esFoto) {
      if (archivo.size > LIMITE) {
        mostrar(input, 'El archivo "' + archivo.name + '" pesa ' + kb(archivo.size) +
          '. El máximo es 2 MB. Elegí otro archivo o sacale una foto.', 'error');
        input.value = '';
      } else {
        mostrar(input, 'Listo: ' + archivo.name + ' (' + kb(archivo.size) + ')', 'ok');
      }
      return Promise.resolve();
    }

    if (archivo.size <= 600 * 1024) {   // foto ya liviana: se deja como esta
      mostrar(input, 'Listo: ' + archivo.name + ' (' + kb(archivo.size) + ')', 'ok');
      return Promise.resolve();
    }

    input.dataset.procesando = '1';
    mostrar(input, 'Achicando la foto…', 'info');
    return achicarFoto(archivo).then(function (chica) {
      var usar = chica.size < archivo.size ? chica : archivo;
      if (usar !== archivo && !reemplazarArchivo(input, usar)) usar = archivo;
      if (usar.size > LIMITE) {
        mostrar(input, 'La foto pesa ' + kb(usar.size) + ' y no se pudo achicar. Probá con otra foto o una captura de pantalla.', 'error');
        input.value = '';
      } else {
        mostrar(input, 'Listo: foto lista para subir (' + kb(usar.size) + ')', 'ok');
      }
    }).catch(function () {
      if (archivo.size > LIMITE) {
        mostrar(input, 'La foto pesa ' + kb(archivo.size) + '. El máximo es 2 MB. Probá con una captura de pantalla de la foto.', 'error');
        input.value = '';
      } else {
        mostrar(input, 'Listo: ' + archivo.name + ' (' + kb(archivo.size) + ')', 'ok');
      }
    }).then(function () { input.dataset.procesando = ''; });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var formularios = document.querySelectorAll('form');
    Array.prototype.forEach.call(formularios, function (form) {
      if (form.hasAttribute('data-sin-control-archivos')) return;
      var inputs = form.querySelectorAll('input[type="file"]');
      if (!inputs.length) return;
      Array.prototype.forEach.call(inputs, function (input) {
        input.addEventListener('change', function () { procesar(input); });
      });

      form.addEventListener('submit', function (ev) {
        var malo = null, ocupado = false;
        Array.prototype.forEach.call(inputs, function (input) {
          if (input.dataset.procesando === '1') ocupado = true;
          var f = input.files && input.files[0];
          if (f && f.size > LIMITE && !malo) malo = input;
        });
        var btn = form.querySelector('[type="submit"]');
        function cancelar() {
          ev.preventDefault();
          // algunos formularios desactivan el boton al enviar (onsubmit="send()"): se vuelve a activar
          setTimeout(function () { if (btn) { btn.disabled = false; btn.removeAttribute('disabled'); btn.style.width = ''; } }, 0);
        }
        if (ocupado) {
          cancelar();
          alertaArriba(form, 'Esperá unos segundos: todavía se está achicando una foto.');
          return;
        }
        if (malo) {
          cancelar();
          mostrar(malo, 'Este archivo pesa más de 2 MB. Elegí otro antes de confirmar.', 'error');
          malo.scrollIntoView({behavior: 'smooth', block: 'center'});
          return;
        }
        if (btn) {
          // solo si nadie mas freno el envio (por ejemplo, un campo obligatorio vacio)
          setTimeout(function () {
            if (ev.defaultPrevented) return;
            var texto = 'Enviando… no cierres esta página';
            if (btn.tagName === 'INPUT') btn.value = texto; else btn.textContent = texto;
            btn.disabled = true;
          }, 0);
        }
      });
    });
  });

  function alertaArriba(form, texto) {
    var btn = form.querySelector('[type="submit"]');
    var el = form.querySelector('.estado-envio');
    if (!el) {
      el = document.createElement('div');
      el.className = 'estado-envio alert alert-warning mt-2';
      (btn ? btn.parentNode : form).appendChild(el);
    }
    el.textContent = texto;
  }
})();

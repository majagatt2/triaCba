{% extends "base/index3.html" %}

{% load static %}
{% load i18n %}


{% block nav %}
{% endblock %}

{% block aside %}
{% endblock %}


{% block content %}
  <form action="" method="post">
  {% csrf_token %}


  {% if form.email.errors %}
    {{ form.email.errors }}
  {% endif %}
    <h3>Restablecer contraseña</h3>

    ¿Olvidaste tu contraseña? Ingrese su dirección de correo electrónico a continuación y le enviaremos las instrucciones para configurar una nueva..
      <p>{{ form.as_p }}</p>
    <input type="submit" class="btn btn-primary justify" value="Restablecer misss contraseña">
  </form>
{% endblock %}
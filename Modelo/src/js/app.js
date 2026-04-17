// INICIALIZACIÓN DE LA APLICACIÓN
// Espera a que el DOM esté completamente cargado antes de ejecutar el código
document.addEventListener('DOMContentLoaded', () => {
    iniciarApp();
});

// FUNCIÓN PRINCIPAL DE INICIO
// Llama a las funciones necesarias para inicializar la aplicación
function iniciarApp() {
    validarFormularioLogin();
}

// VALIDACIÓN DEL FORMULARIO DE LOGIN
// Configura la validación del formulario de login en el lado del cliente
function validarFormularioLogin() {
    // Selecciona el formulario de login por su ID
    const formulario = document.querySelector('#formulario-login');

    // Si el formulario existe en la página
    if (formulario) {
        // Añade un event listener para el evento 'submit'
        formulario.addEventListener('submit', function(e) {
            // Previene el envío automático del formulario
            e.preventDefault();

            // Obtiene los valores de los campos, eliminando espacios en blanco
            const email = document.querySelector('#email').value.trim();
            const password = document.querySelector('#password').value.trim();

            // VALIDACIÓN DE CAMPOS OBLIGATORIOS
            // Verifica que ambos campos estén llenos
            if (email === '' || password === '') {
                // Muestra una alerta de error si faltan campos
                mostrarAlerta('Todos los campos son obligatorios', 'error');
                return; // Detiene la ejecución
            }

            // Si la validación pasa, envía los datos al backend
            enviarDatosBackend(email, password);
        });
    }
}

// FUNCIÓN PARA MOSTRAR ALERTAS
// Crea y muestra mensajes de alerta temporales en la interfaz
function mostrarAlerta(mensaje, tipo) {
    // Elimina cualquier alerta previa para evitar duplicados
    const alertaPrevia = document.querySelector('.alerta');
    if (alertaPrevia) {
        alertaPrevia.remove();
    }

    // Crea un nuevo elemento div para la alerta
    const divAlerta = document.createElement('DIV');
    divAlerta.textContent = mensaje; // Establece el mensaje
    divAlerta.classList.add('alerta', `alerta-${tipo}`); // Añade clases CSS

    // Inserta la alerta al inicio de la sección del formulario
    const contenedorFormulario = document.querySelector('.seccion-formulario');
    if (contenedorFormulario) {
        contenedorFormulario.insertBefore(divAlerta, contenedorFormulario.firstChild);
    }

    // PROGRAMACIÓN PARA OCULTAR LA ALERTA
    // Elimina la alerta automáticamente después de 3 segundos
    setTimeout(() => {
        divAlerta.remove();
    }, 3000);
}

// ENVÍO DE DATOS AL BACKEND
// Maneja el envío de datos del formulario al servidor PHP
function enviarDatosBackend(email, password) {
    // Realiza el envío del formulario (el backend PHP procesará los datos)
    document.querySelector('#formulario-login').submit();
}
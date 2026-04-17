// Espera a que el DOM esté completamente cargado antes de ejecutar el código
document.addEventListener('DOMContentLoaded', () => {
    iniciarApp(); // Llama a la función principal de la aplicación
});

// Función principal que inicializa la aplicación
function iniciarApp() {
    validarFormularioLogin(); // Configura la validación del formulario de login
}

// Función que configura la validación del formulario de login
function validarFormularioLogin() {
    const formulario = document.querySelector('#formulario-login'); // Selecciona el formulario por ID

    if (formulario) { // Verifica que el formulario existe en la página
        formulario.addEventListener('submit', function(e) {
            e.preventDefault(); // Previene el envío por defecto del formulario

            // Obtiene y limpia los valores de los campos de entrada
            const email = document.querySelector('#email').value.trim();
            const password = document.querySelector('#password').value.trim();

            // Valida que ambos campos estén completos
            if (email === '' || password === '') {
                mostrarAlerta('Todos los campos son obligatorios', 'error'); // Muestra alerta de error
                return; // Detiene la ejecución
            }

            enviarDatosBackend(email, password); // Envía los datos al backend
        });
    }
}

// Función para mostrar alertas al usuario
function mostrarAlerta(mensaje, tipo) {
    const alertaPrevia = document.querySelector('.alerta'); // Busca alertas previas
    if (alertaPrevia) {
        alertaPrevia.remove(); // Remueve alertas existentes
    }

    // Crea un nuevo elemento div para la alerta
    const divAlerta = document.createElement('DIV');
    divAlerta.textContent = mensaje; // Establece el mensaje
    divAlerta.classList.add('alerta', `alerta-${tipo}`); // Añade clases CSS

    // Inserta la alerta al inicio del contenedor del formulario
    const contenedorFormulario = document.querySelector('.tarjeta-login');
    if (contenedorFormulario) {
        contenedorFormulario.insertBefore(divAlerta, contenedorFormulario.firstChild);
    }

    // Remueve la alerta automáticamente después de 3 segundos
    setTimeout(() => {
        divAlerta.remove();
    }, 3000);
}

// Función para enviar datos al backend (preparada para Fetch API)
function enviarDatosBackend(email, password) {
    console.log('Datos listos para enviar vía Fetch API a PHP PDO'); // Log para desarrollo
}

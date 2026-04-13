document.addEventListener('DOMContentLoaded', function() {
    iniciarApp();
});

function iniciarApp() {
    console.log('App iniciada correctamente.');
}
document.addEventListener('DOMContentLoaded', () => {
    iniciarApp();
});

function iniciarApp() {
    validarFormularioLogin();
}

function validarFormularioLogin() {
    const formulario = document.querySelector('#formulario-login');

    if (formulario) {
        formulario.addEventListener('submit', function(e) {
            e.preventDefault();

            const email = document.querySelector('#email').value.trim();
            const password = document.querySelector('#password').value.trim();

            if (email === '' || password === '') {
                mostrarAlerta('Todos los campos son obligatorios', 'error');
                return;
            }

            enviarDatosBackend(email, password);
        });
    }
}

function mostrarAlerta(mensaje, tipo) {
    const alertaPrevia = document.querySelector('.alerta');
    if (alertaPrevia) {
        alertaPrevia.remove();
    }

    const divAlerta = document.createElement('DIV');
    divAlerta.textContent = mensaje;
    divAlerta.classList.add('alerta', `alerta-${tipo}`);

    const contenedorFormulario = document.querySelector('.tarjeta-login');
    if (contenedorFormulario) {
        contenedorFormulario.insertBefore(divAlerta, contenedorFormulario.firstChild);
    }

    setTimeout(() => {
        divAlerta.remove();
    }, 3000);
}

function enviarDatosBackend(email, password) {
    console.log('Datos listos para enviar vía Fetch API a PHP PDO');
}
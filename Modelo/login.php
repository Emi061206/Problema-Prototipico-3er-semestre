<!DOCTYPE html>
<!-- Declara el tipo de documento como HTML5 -->
<html lang="es">
<!-- Define el idioma de la página como español -->
<head>
    <!-- Contiene metadatos y enlaces a recursos externos -->
    <meta charset="UTF-8">
    <!-- Especifica la codificación de caracteres como UTF-8 -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Configura la vista para dispositivos móviles -->
    <title>Iniciar Sesión - Agricultores</title>
    <!-- Título de la página que aparece en la pestaña del navegador -->
    <link rel="stylesheet" href="dist/css/app.css">
    <!-- Enlaza la hoja de estilos CSS compilada -->
    <style>
        /* Estilos CSS internos para la alerta de error */
        .alerta-error {
            background-color: #f8d7da; /* Color de fondo rojo claro */
            color: #721c24; /* Color de texto rojo oscuro */
            padding: 10px; /* Espaciado interno */
            margin-bottom: 15px; /* Margen inferior */
            border: 1px solid #f5c6cb; /* Borde rojo claro */
            border-radius: 4px; /* Bordes redondeados */
            text-align: center; /* Texto centrado */
            font-size: 0.9rem; /* Tamaño de fuente pequeño */
        }
    </style>
</head>
<body class="pantalla-login">
    <!-- Cuerpo de la página con clase para estilos -->
    <main class="tarjeta-login">
        <!-- Contenedor principal del formulario de login -->
        <header class="login-header">
            <!-- Encabezado del formulario -->
            <h2>INICIAR SESIÓN</h2>
            <!-- Título del formulario -->
        </header>

        <?php if (isset($_GET['error'])): ?>
            <!-- Verifica si hay un parámetro 'error' en la URL (GET) -->
            <div class="alerta-error">
                <!-- Muestra una alerta de error si las credenciales son incorrectas -->
                Correo o contraseña incorrectos. Por favor, intente de nuevo.
            </div>
        <?php endif; ?>

        <form action="procesar_login.php" method="POST" id="formulario-login" class="formulario">
            <!-- Formulario que envía datos a procesar_login.php mediante POST -->
            <div class="formulario-grupo">
                <!-- Grupo para el campo de correo -->
                <label for="email">CORREO</label>
                <!-- Etiqueta para el campo de entrada -->
                <input type="email" id="email" name="correo" class="entrada-texto" placeholder="ejemplo@correo.com" required>
                <!-- Campo de entrada para el correo electrónico, obligatorio -->
            </div>

            <div class="formulario-grupo">
                <!-- Grupo para el campo de contraseña -->
                <label for="password">CONTRASEÑA</label>
                <!-- Etiqueta para el campo de entrada -->
                <input type="password" id="password" name="password" class="entrada-texto" placeholder="********" required>
                <!-- Campo de entrada para la contraseña, obligatorio -->
            </div>

            <div class="acciones-formulario">
                <!-- Contenedor para el botón de envío -->
                <button type="submit" class="btn-primario">INICIAR SESIÓN</button>
                <!-- Botón para enviar el formulario -->
            </div>
        </form>

        <div class="login-footer">
            <!-- Pie del formulario con enlace de vuelta -->
            <a href="index.php">← VOLVER AL INICIO</a>
            <!-- Enlace para regresar a la página principal -->
        </div>
    </main>

    <!--<script src="dist/js/app.js"></script> -->
    <!-- Enlaza el archivo JavaScript compilado -->
</body>
</html>
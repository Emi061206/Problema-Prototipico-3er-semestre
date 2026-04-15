<!DOCTYPE html>
<!-- Define el tipo de documento como HTML5 -->
<html lang="es">
<!-- Establece el idioma de la página como español -->
<head>
    <!-- Configuración de metadatos y enlaces externos -->
    <meta charset="UTF-8">
    <!-- Define la codificación de caracteres como UTF-8 -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Configura la vista para dispositivos móviles -->
    <title>Iniciar Sesión - Agricultores</title>
    <!-- Título de la página que aparece en la pestaña del navegador -->
    <link rel="stylesheet" href="dist/css/app.css">
    <!-- Enlaza la hoja de estilos CSS compilada -->
</head>
<body class="pantalla-login">
    <!-- Cuerpo de la página con clase para estilos de pantalla de login -->
    <main class="tarjeta-login">
        <!-- Contenedor principal de la tarjeta de login -->
        <header class="login-header">
            <!-- Encabezado de la sección de login -->
            <h2>INICIAR SESIÓN</h2>
            <!-- Título principal de la página -->
        </header>
        
        <!-- Formulario que envía datos al script PHP para procesar el login -->
        <form action="procesar_login.php" method="POST" id="formulario-login" class="formulario">
            <!-- Campo para el correo electrónico -->
            <div class="formulario-grupo">
                <label for="email">CORREO</label>
                <!-- Etiqueta asociada al campo de email -->
                <input type="email" id="email" name="correo" class="entrada-texto" placeholder="ejemplo@correo.com" required>
                <!-- Campo de entrada de tipo email, obligatorio -->
            </div>
            
            <!-- Campo para la contraseña -->
            <div class="formulario-grupo">
                <label for="password">CONTRASEÑA</label>
                <!-- Etiqueta asociada al campo de contraseña -->
                <input type="password" id="password" name="password" class="entrada-texto" placeholder="********" required>
                <!-- Campo de entrada de tipo password, obligatorio -->
            </div>
            
            <!-- Botón para enviar el formulario -->
            <div class="acciones-formulario">
                <button type="submit" class="btn-primario">INICIAR SESIÓN</button>
                <!-- Botón que envía el formulario cuando se hace clic -->
            </div>
        </form>

        <!-- Enlace para volver a la página principal -->
        <div class="login-footer">
            <a href="index.html">← VOLVER AL INICIO</a>
            <!-- Enlace que redirige a la página de inicio -->
        </div>
    </main>

    <!-- Script JavaScript para validación del formulario -->
    <script src="dist/js/app.js"></script>
    <!-- Carga el archivo JavaScript compilado para funcionalidad interactiva -->
</body>
</html>
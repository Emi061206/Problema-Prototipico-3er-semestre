<!DOCTYPE html>
<html lang="es">
<head>
    <!-- Declaración del tipo de documento HTML5 -->
    <!-- Define el idioma de la página como español -->
    <meta charset="UTF-8">
    <!-- Especifica la codificación de caracteres UTF-8 -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Configura la página para ser responsive en dispositivos móviles -->
    <title>Iniciar Sesión - Smart Agroforestry</title>
    <!-- Título que aparece en la pestaña del navegador -->
    <link rel="stylesheet" href="dist/css/app.css">
    <!-- Importa el archivo CSS compilado con los estilos de la aplicación -->
</head>
<!-- Inicia el cuerpo del documento con la clase 'pantalla-login-nueva' para estilos específicos -->
<body class="pantalla-login-nueva">
    <!-- Elemento principal de la página que contiene el layout en dos columnas -->
    <main class="contenedor-split">
        
        <!-- SECCIÓN IZQUIERDA: Imagen decorativa -->
        <div class="seccion-imagen">
            <!-- Círculo decorativo con flores para visual atractivo -->
            <div class="circulo-flores"></div>
        </div>

        <!-- SECCIÓN DERECHA: Formulario de login -->
        <div class="seccion-formulario">
            <!-- Encabezado del formulario -->
            <h2>Iniciar sesión</h2>

            <!-- MENSAJE DE ERROR CONDICIONAL -->
            <!-- Se muestra solo si existe parámetro 'error' en la URL (GET) -->
            <!-- Esto ocurre cuando el login falla por credenciales incorrectas -->
            <?php if (isset($_GET['error'])): ?>
                <div class="alerta-error" style="background: rgba(255,0,0,0.2); border: 1px solid white; color: white; padding: 10px; margin-bottom: 15px; text-align: center; border-radius: 4px;">
                    Correo o contraseña incorrectos.
                </div>
            <?php endif; ?>

            <!-- FORMULARIO DE LOGIN -->
            <!-- Método POST envía datos de forma segura al procesador de login -->
            <!-- Action: Apunta al archivo 'procesar_login.php' que valida las credenciales -->
            <form action="procesar_login.php" method="POST" id="formulario-login">
                <!-- Campo de email -->
                <!-- type="email": Valida el formato de email en navegadores modernos -->
                <!-- required: Campo obligatorio, el formulario no se envía sin llenar -->
                <div class="formulario-grupo">
                    <input type="email" id="email" name="correo" class="entrada-transparente" placeholder="CORREO" required>
                </div>

                <!-- Campo de contraseña -->
                <!-- type="password": Oculta los caracteres mientras se escriben -->
                <!-- required: Campo obligatorio para enviar el formulario -->
                <div class="formulario-grupo">
                    <input type="password" id="password" name="password" class="entrada-transparente" placeholder="CONTRASEÑA" required>
                </div>

                <!-- Botón de envío -->
                <!-- Al hacer clic, envía los datos POST a procesar_login.php -->
                <button type="submit" class="btn-transparente">INICIAR SESIÓN</button>
            </form>
            <!-- Cierre del formulario de login -->
        </div>
        <!-- Cierre de la sección del formulario -->

    </main>
    <!-- Cierre del contenedor principal (split layout) -->

    <!-- Importa el archivo JavaScript compilado para funcionalidad interactiva -->
    <!-- Contiene lógica del cliente y manejo de eventos del formulario -->
    <script src="dist/js/app.js"></script>
</body>
</html>
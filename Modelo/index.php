<?php
// Inicia la sesión del usuario para mantener el estado de autenticación
session_start();

// Verifica si el usuario ha iniciado sesión correctamente
// Comprueba que exista la clave 'login_exitoso' en $_SESSION y que sea true
$usuario_autenticado = isset($_SESSION['login_exitoso']) && $_SESSION['login_exitoso'] === true;

// Obtiene el nombre del agricultor autenticado de la sesión
// Si el usuario no está autenticado, asigna una cadena vacía
// htmlspecialchars() previene ataques XSS al convertir caracteres especiales
$nombre_agricultor = $usuario_autenticado ? htmlspecialchars($_SESSION['usuario_nombre']) : '';
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <!-- Metaetiquetas de configuración del documento -->
    <meta charset="UTF-8">
    <!-- Define el conjunto de caracteres como UTF-8 para soporte de caracteres especiales -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Configuración de responsividad: ajusta la escala inicial para dispositivos móviles -->
    <title>Análisis Agrícola - Xochimilco</title>
    <!-- Título que aparece en la pestaña del navegador -->
    <link rel="stylesheet" href="dist/css/app.css">
    <!-- Enlaza el archivo CSS compilado para estilos visuales -->
</head>
<body>
    <!-- Encabezado principal del sitio -->
    <header class="encabezado-principal">
        <h1>ANÁLISIS TÉCNICO-ECONÓMICO PARA LA DIVERSIFICACIÓN DE CULTIVOS EN MÉXICO</h1>
        
        <!-- Mostrar mensaje de bienvenida solo si el usuario está autenticado -->
        <?php if($usuario_autenticado): ?>
            <p style="color: white; margin-top: 10px; font-weight: bold;">
                Bienvenido, Productor: <?php echo $nombre_agricultor; ?>
                <!-- Muestra el nombre del agricultor autenticado -->
            </p>
        <?php endif; ?>
    </header>

    <!-- Sección decorativa con imagen de fondo (banner de Xochimilco) -->
    <div class="hero-xochimilco"></div>

    <!-- Contenedor principal del contenido -->
    <main class="contenedor-principal">
        <!-- Menú de navegación con botones para diferentes secciones -->
        <nav class="menu-navegacion">
            <button class="btn-nav">ESTADÍSTICAS</button>
            <!-- Botón para ver estadísticas agrícolas -->
            <button class="btn-nav">DATOS DE CULTIVOS</button>
            <!-- Botón para acceder a información de cultivos -->
            <button class="btn-nav">UN POCO DE INTRODUCCIÓN</button>
            <!-- Botón para ver información introductoria del sistema -->
        </nav>
        
        <!-- Sección de acceso al sistema con botón dinámico según estado de autenticación -->
        <section class="acceso-sistema">
            <?php if(!$usuario_autenticado): ?>
                <!-- Si el usuario NO está autenticado, muestra botón para iniciar sesión -->
                <a href="login.php" class="btn-login">INICIAR SESIÓN (AGRICULTORES)</a>
            <?php else: ?>
                <!-- Si el usuario ESTÁ autenticado, muestra botón para cerrar sesión -->
                <!-- El color rojo (#d32f2f) diferencia visualmente la acción de cerrar sesión -->
                <a href="logout.php" class="btn-login" style="background-color: #d32f2f; color: white;">CERRAR SESIÓN</a>
            <?php endif; ?>
        </section>
    </main>

    <!-- Pie de página con información de derechos de autor -->
    <footer class="pie-pagina">
        <p>DERECHOS RESERVADOS</p>
        <!-- Leyenda de derechos de autor -->
        <p>UNRC 2026</p>
        <!-- Universidad y año del proyecto -->
    </footer>

    <!-- Script principal con funcionalidades JavaScript compiladas -->
    <script src="dist/js/app.js"></script>
</body>
</html>
<?php
session_start();
$usuario_autenticado = isset($_SESSION['login_exitoso']) && $_SESSION['login_exitoso'] === true;
$nombre_agricultor = $usuario_autenticado ? htmlspecialchars($_SESSION['usuario_nombre']) : '';
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis Agrícola - Xochimilco</title>
    <link rel="stylesheet" href="dist/css/app.css">
</head>
<body>
    <header class="encabezado-principal">
        <h1>ANÁLISIS TÉCNICO-ECONÓMICO PARA LA DIVERSIFICACIÓN DE CULTIVOS EN MÉXICO</h1>
        <main class="contenedor-principal">
        <nav class="menu-navegacion">
            <button class="btn-nav">ESTADÍSTICAS</button>
            <button class="btn-nav">DATOS DE CULTIVOS</button>
            <button class="btn-nav">UN POCO DE INTRODUCCIÓN</button>
        </nav>

        <section class="acceso-sistema">
            <?php if(!$usuario_autenticado): ?>
                <a href="login.php" class="btn-login">INICIAR SESIÓN (AGRICULTORES)</a>
            <?php else: ?>
                <p>Bienvenido, <strong><?php echo $nombre_agricultor; ?></strong></p>
                <a href="logout.php" class="btn-login" style="color: #d32f2f;">CERRAR SESIÓN</a>
            <?php endif; ?>
        </section>
    </main>
    </header>

    

    <section class="hero-xochimilco"></section>



    <footer class="pie-pagina">
        <p>DERECHOS RESERVADOS</p>
        <p>UNRC 2026</p>
    </footer>

    <script src="dist/js/app.js"></script>
</body>
</html>
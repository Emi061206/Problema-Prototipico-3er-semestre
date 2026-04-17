<?php
// 1. Iniciar la sesión para poder manipularla
session_start();

// 2. Limpiar todas las variables de sesión
$_SESSION = array();

// 3. Destruir la cookie de sesión en el navegador
if (ini_get("session.use_cookies")) {
    $params = session_get_cookie_params();
    setcookie(session_name(), '', time() - 42000,
        $params["path"], $params["domain"],
        $params["secure"], $params["httponly"]
    );
}

// 4. Destruir la sesión en el servidor
session_destroy();

// 5. Redirigir directamente al index
header("Location: index.php");
exit;
?>
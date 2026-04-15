<?php
function obtenerConexionAgro() {
    $ruta_env = dirname(__DIR__) . '/.env';
    $env_vars = parse_ini_file($ruta_env);

    if (!$env_vars) {
        die("Error estructural: No se pudo cargar la configuración del entorno.");
    }

    $host = $env_vars['DB_HOST'];
    $db = $env_vars['DB_NAME_AGRO'];
    $user = $env_vars['DB_USER'];
    $pass = $env_vars['DB_PASSWORD'];

    try {
        $dsn = "mysql:host=$host;dbname=$db;charset=utf8mb4";
        
        $opciones = [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false
        ];
        
        return new PDO($dsn, $user, $pass, $opciones);
    } catch (PDOException $e) {
        die("Error de conexión estructural.");
    }
}
?>
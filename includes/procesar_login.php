<?php
// CONFIGURACIÓN INICIAL DEL SCRIPT
// Muestra errores para depuración durante desarrollo
ini_set('display_errors', 1);
error_reporting(E_ALL);

// Inicia la sesión para manejar variables de estado del usuario
session_start();

// Incluye el archivo de conexión a la base de datos
require_once __DIR__ . '/../includes/conexion.php';

// VERIFICACIÓN DEL MÉTODO DE SOLICITUD
// Solo procesa si es una solicitud POST (envío de formulario)
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // OBTENCIÓN Y SANITIZACIÓN DE DATOS DEL FORMULARIO
    // Sanitiza el email para prevenir inyección de código malicioso
    $email = filter_input(INPUT_POST, 'correo', FILTER_SANITIZE_EMAIL);
    // Obtiene la contraseña sin sanitizar (se verifica con hash después)
    $password = $_POST['password'];

    // VALIDACIÓN BÁSICA DE CAMPOS
    // Verifica que ambos campos estén presentes y no vacíos
    if (!$email || !$password) {
        // Redirige de vuelta al login con indicador de error
        header('Location: login.php?error=1');
        exit;
    }

    try {
        // CONEXIÓN A LA BASE DE DATOS
        // Obtiene la conexión PDO configurada para la base de datos agroforestal
        $db = obtenerConexionAgro();
        
        // CONSULTA DE AUTENTICACIÓN
        // Busca al usuario por email, limitando a 1 resultado por seguridad
        $query = "SELECT ID_Productor, Nombre_Chinampa, password FROM productores WHERE correo = :email LIMIT 1";
        $stmt = $db->prepare($query);
        $stmt->bindParam(':email', $email, PDO::PARAM_STR);
        $stmt->execute();
        
        // Obtiene el resultado de la consulta
        $usuario = $stmt->fetch();

        // VERIFICACIÓN DE CREDENCIALES
        // Verifica que el usuario existe y la contraseña coincide con el hash almacenado
        if ($usuario && password_verify($password, $usuario['password'])) {
            // LOGIN EXITOSO: Configurar sesión y redirigir al dashboard
            // Regenera el ID de sesión para prevenir ataques de fijación de sesión
            session_regenerate_id(true);
            
            // Establece variables de sesión para mantener el estado del usuario
            $_SESSION['login_exitoso'] = true;
            $_SESSION['usuario_nombre'] = "Productor";
            
            // Redirige al usuario al panel principal (index.php en el directorio padre)
            header("Location: ../index.php");
            exit();
        } else {
            // LOGIN FALLIDO: Credenciales incorrectas
            // Redirige de vuelta al login con indicador de error específico
            header('Location: login.php?error=credenciales');
            exit;
        }

    } catch (PDOException $e) {
        // ERROR DE SISTEMA: Problemas con la base de datos
        // Registra el error (en producción) y redirige con error genérico
        // error_log($e->getMessage()); // Descomentado en producción
        header('Location: login.php?error=sistema');
        exit;
    }
} else {
    // SOLICITUD NO VÁLIDA: No es POST
    // Redirige al formulario de login si se accede directamente al archivo
    header('Location: login.php');
    exit;
}
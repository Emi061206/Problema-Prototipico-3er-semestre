<?php
session_start();
require_once __DIR__ . '/../includes/conexion.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = filter_input(INPUT_POST, 'correo', FILTER_SANITIZE_EMAIL);
    $password = $_POST['password'];

    if (!$email || !$password) {
        header('Location: login.php?error=1');
        exit;
    }

    try {
        $db = obtenerConexionAgro();
        
        $query = "SELECT id, nombre, password FROM Productores WHERE correo = :email LIMIT 1";
        $stmt = $db->prepare($query);
        $stmt->bindParam(':email', $email, PDO::PARAM_STR);
        $stmt->execute();
        
        $usuario = $stmt->fetch();

        if ($usuario && password_verify($password, $usuario['password'])) {
            session_regenerate_id(true);
            $_SESSION['usuario_id'] = $usuario['id'];
            $_SESSION['usuario_nombre'] = $usuario['nombre'];
            $_SESSION['login_exitoso'] = true;

            header('Location: index.php');
            exit;
        } else {
            header('Location: login.php?error=credenciales');
            exit;
        }

    } catch (PDOException $e) {
        header('Location: login.php?error=sistema');
        exit;
    }
} else {
    header('Location: login.php');
    exit;
}
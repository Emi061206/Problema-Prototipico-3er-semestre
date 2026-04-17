<?php
session_start();
require_once __DIR__ . '/../includes/conexion.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $correo = filter_input(INPUT_POST, 'correo', FILTER_SANITIZE_EMAIL);
    $password = $_POST['password'] ?? '';

    try {
        $db = obtenerConexionAgro();
        $query = "SELECT id, nombre, password FROM productores WHERE correo = :email LIMIT 1";
        $stmt = $db->prepare($query);
        $stmt->execute([':email' => $correo]);
        $usuario = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($usuario && password_verify($password, $usuario['password'])) {
            session_regenerate_id(true);
            $_SESSION['login_exitoso'] = true;
            $_SESSION['usuario_id'] = $usuario['id'];
            $_SESSION['usuario_nombre'] = $usuario['nombre'];

            header("Location: index.php");
            exit;
        } else {
            header("Location: login.php?error=1");
            exit;
        }
    } catch (PDOException $e) {
        header("Location: login.php?error=sistema");
        exit;
    }
}
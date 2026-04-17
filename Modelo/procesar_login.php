<?php
session_start();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // MANEJO DE ACCESO CORRECTO: Configura sesión y redirige
    $_SESSION['login_exitoso'] = true;
    $_SESSION['usuario_nombre'] = "Productor";
    header("Location: ../index.php");
    exit();
} else {
    // SI NO ES POST, redirige al login
    header("Location: login.php");
    exit();
}
<?php
session_start();
$_SESSION['test'] = "Funciona";
echo "Sesion iniciada. ID: " . session_id() . "<br>";
echo "Valor guardado: " . $_SESSION['test'];
?>
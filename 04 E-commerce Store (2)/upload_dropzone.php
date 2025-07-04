<?php
$upload_dir = __DIR__ . '/imagenes_por_validar/';
if (!is_dir($upload_dir)) mkdir($upload_dir);

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['file'])) {
    $archivo = $_FILES['file'];
    $nombre = basename($archivo['name']);
    $destino = $upload_dir . $nombre;

    if (move_uploaded_file($archivo['tmp_name'], $destino)) {
        http_response_code(200);
        echo "OK";
    } else {
        http_response_code(500);
        echo "ERROR";
    }
}
?>

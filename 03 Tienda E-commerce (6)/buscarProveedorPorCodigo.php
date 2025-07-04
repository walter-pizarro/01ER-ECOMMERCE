<?php
// Verificar si se proporcionó un código de proveedor
if (isset($_GET['codigo_proveedor'])) {
    $codigoProveedor = $_GET['codigo_proveedor'];

    // Realizar la conexión a la base de datos (ajusta las credenciales según tu configuración)
    $conexion = new mysqli("localhost", "aquitulogo23", "g-i,F6+{MawJ", "aquitulogo23_tienda_virtual");

    // Verificar la conexión
    if ($conexion->connect_error) {
        die("Error en la conexión: " . $conexion->connect_error);
    }

    // Preparar la consulta para buscar proveedores por código
    $sql = "SELECT * FROM proveedores WHERE codigo_proveedor LIKE ?";
    $stmt = $conexion->prepare($sql);
    $stmt->bind_param('s', $codigoProveedor);
    $stmt->execute();
    $resultado = $stmt->get_result();

    // Verificar si se encontraron resultados
    if ($resultado->num_rows > 0) {
        // Obtener los resultados de la búsqueda
        $resultadosProveedor = $resultado->fetch_all(MYSQLI_ASSOC);

        // Devolver los resultados como respuesta JSON
        echo json_encode($resultadosProveedor);
    } else {
        // Enviar una respuesta JSON indicando que no se encontraron resultados
        echo json_encode(array('error' => 'No se encontraron proveedores con ese código.'));
    }

    // Cerrar la conexión y la consulta
    $stmt->close();
    $conexion->close();
} else {
    // Enviar una respuesta JSON indicando que no se proporcionó un código de proveedor
    echo json_encode(array('error' => 'No se proporcionó un código de proveedor.'));
}
?>

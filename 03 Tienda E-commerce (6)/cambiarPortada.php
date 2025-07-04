<?php

// Verificar si se recibe una solicitud POST
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    
    // Obtener el ID del producto y la nueva portada
    $productoId = $_POST['productoId'];
    $nuevaPortada = $_FILES['nuevaPortada'];
    
    // Ruta donde se almacenarán las imágenes (ajústala según tu configuración)
    $directorioDestino = 'assets/images/productos/';
        
    // Obtener información del archivo
    $nombreArchivo = $_FILES['nuevaPortada']['name'];
    $tipoArchivo = $_FILES['nuevaPortada']['type'];
    $tamanoArchivo = $_FILES['nuevaPortada']['size'];
    $archivoTemporal = $_FILES['nuevaPortada']['tmp_name'];
    $errorArchivo = $_FILES['nuevaPortada']['error'];

    //echo "id: " . $productoId . "<br>";
    
    // Obtener la extensión del archivo
    $extension = pathinfo($nombreArchivo, PATHINFO_EXTENSION);
    
    // Validar la extensión (en este caso, solo permitir archivos jpg)
    if ($extension != 'jpg' && $extension != 'png' && $extension != 'jpeg') {
        //echo "Error: Solo se permiten archivos JPG.";
        echo "<script>   
                alert('Error: Solo se permiten archivos JPG.')
                location.href='https://aquitulogo.cl/tienda/productos';       
                </script>";
    } else {
        
        // Ruta donde se almacenarán las imágenes (ajústala según tu configuración)
        $directorioDestino = 'assets/images/productos/';
    
        // Mostrar el nombre del archivo
        //echo "Nombre del archivo: " . $nombreArchivo . "<br>";
    
        // Mover el archivo a la carpeta de destino
        $rutaDestino = $directorioDestino . $nombreArchivo;
    
        $rutaCompleta = $directorioDestino . $nombreArchivo;
    
        if (move_uploaded_file($archivoTemporal, $rutaDestino)) {
            //echo "Archivo subido con éxito.";
            
            // Datos de conexión a la base de datos
            $servername = "localhost";
            $username = "aquitulogo23";
            $password = "g-i,F6+{MawJ";
            $dbname = "aquitulogo23_tienda_virtual";

            $conexion = new mysqli($servername, $username, $password, $dbname);

            if ($conexion->connect_error) {
                //die("Error de conexión a la base de datos: " . $conexion->connect_error);
                echo "<script>   
                alert('Error de conexión a la base de datos.')
                location.href='https://aquitulogo.cl/tienda/productos';       
                </script>";
            }

            $sql = "UPDATE productos SET imagen = '$rutaCompleta' WHERE id = $productoId";

            if ($conexion->query($sql) === TRUE) {
                //echo 'La portada se ha cambiado correctamente';
                echo "<script>   
                alert('La portada se ha cambiado correctamente.')
                location.href='https://aquitulogo.cl/tienda/productos';       
                </script>";
            } else {
                //echo 'Error al actualizar la base de datos';
                echo "<script>   
                alert('Error al actualizar portada.')
                location.href='https://aquitulogo.cl/tienda/productos';       
                </script>";
            }


        } else {
            //echo "Error al subir el archivo.";
            echo "<script>   
            alert('Error al subir el archivo.')
            location.href='https://aquitulogo.cl/tienda/productos';       
            </script>";
        }
    }

    
} else {
    //echo "error";
    echo "<script>   
    alert('No se cargo imagen.')
    location.href='https://aquitulogo.cl/tienda/productos';       
    </script>";
}

?>

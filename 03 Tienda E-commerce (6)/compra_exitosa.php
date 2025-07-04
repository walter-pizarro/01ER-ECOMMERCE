<?php

    // Iniciar la sesi車n
    session_start();

    // Verificar si ya se ha creado una ID de sesi車n
    if (isset($_SESSION['id_session'])) {
        //echo "Tu ID de sesion existente es: " . $_SESSION['id_session'];
    } else {
        // Generar una nueva ID de sesi車n
        $_SESSION['id_session'] = session_id();
        //echo "Tu nueva ID de sesion es: " . $_SESSION['id_session'];
    }
    
    //muestra de errores
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);
?>
    
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../assets/css/bootstrap.min.css'; ">
    <link rel="stylesheet" href="assets/css/templatemo.css'; ">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
    
    <title>Compra Exitosa</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin:0;
            background-color: #f7f7f7;
        }
        .receipt-container {
            max-width: 500px;
            margin: 50px auto;
            padding: 20px;
            border: 1px solid #ccc;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .success-message {
            font-size: 45px;
            font-weight: bold;
        }
        .receipt-info {
            text-align: left;
            margin-bottom: 20px;
        }
        .receipt-info p {
            margin: 5px 0;
        }
        .receipt-total {
            font-weight: bold;
        }
        .btn-util {
            background-color: #3773ff;
            color: #ffffff;
            cursor: pointer;
            outline: none;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            text-decoration: none;
        }
        .summary {
            font-size: 18px;
            margin-top: 30px;
        }
        #countdown {
            font-size: 20px;
            margin-top: 20px;
        }
        /* Nav */

        /* General */
        .logo {
            font-weight: 500 !important;
        }
        
        .text-warning {
            color: #ede861 !important;
        }
        
        .text-muted {
            color: #bcbcbc !important;
        }
        
        .text-success {
            color: #59ab6e !important;
        }
        
        .text-util {
            color: #3773ff !important;
        }
        
        .text-light {
            color: #cfd6e1 !important;
        }
        
        .bg-dark {
            background-color: #212934 !important;
        }
        
        .bg-light {
            background-color: #e9eef5 !important;
        }
        
        .bg-black {
            background-color: #1d242d !important;
        }
        
        .bg-success {
            background-color: #59ab6e !important;
        }
        
        .bg-util {
            background-color: #3773ff !important;
        }
        
        .btn-success {
            background-color: #59ab6e !important;
            border-color: #56ae6c !important;
        }
        
        .btn-util:hover {
            background-color: #ff003c !important;
        }
        
        .pagination .page-link:hover {
            color: #000;
        }
        
        .pagination .page-link:hover,
        .pagination .page-link.active {
            background-color: #3773ff;
            color: #fff;
        }
        
        
        /* Nav */
        
        #templatemo_nav_top {
            min-height: 40px;
        }
        
        #templatemo_nav_top * {
            font-size: .9em !important;
        }
        
        #templatemo_main_nav a {
            color: #212934;
        }
        
        #templatemo_main_nav a:hover {
            color: #66a6ef;
        }
        
        #templatemo_main_nav .navbar .nav-icon {
            margin-right: 20px;
        }
    </style>
</head>
<body>
    
    <!-- Start Top Nav -->
    <nav class="navbar navbar-expand-lg bg-dark navbar-light" id="templatemo_nav_top">
        <div class="container text-light">
          <div class="w-100 d-flex justify-content-between">
            <div>
              <i class="fa fa-envelope mx-2"></i>
              <a class="navbar-sm-brand text-light text-decoration-none" href="mailto:soporte.hosting@walcom.cl">soporte.hosting@walcom.cl</a>
              <i class="fa fa-phone mx-2"></i>
              <a class="navbar-sm-brand text-light text-decoration-none" href="tel:56 9 5736 04347">+56 9 5736 04347</a>
            </div>
            <div>
              <a class="text-light" href="https://aquitulogo.cl/tienda/" target="_blank" rel="sponsored"><i class="fab fa-facebook-square fa-sm fa-fw me-2"></i></a>
              <a class="text-light" href="https://aquitulogo.cl/tienda/" target="_blank"><i class="fab fa-instagram fa-sm fa-fw me-2"></i></a>
              <a class="text-light" href="https://aquitulogo.cl/tienda/" target="_blank"><i class="fab fa-twitter fa-sm fa-fw me-2"></i></a>
              <a class="text-light" href="https://aquitulogo.cl/tienda/" target="_blank"><i class="fab fa-linkedin fa-sm fa-fw"></i></a>
            </div>
          </div>
        </div>
    </nav>
    <!-- Close Top Nav -->
    
    <div class="row m-0">
        <div class="col pt-2">
            <img src="assets/images/logo.png" width="100px;"><hr>
        </div>
    </div>
    <div class="row m-0">
        <div class="col">
            <div class="success-message mb-2">¡Compra Exitosa!</div>
            
            <div class="row m-0">
                
                <div class="col-6">
                    <img src="https://cdn2.shopify.com/s/files/1/0025/0340/9739/files/Banner_800_x_600_-_Pago_Exitoso_600x600.png?v=1563210428" width="70%">
                </div>
                
                <div class="col-6">
                    <?php
                        // Verificamos que se hayan recibido los datos encriptados y el IV en la URL
                        if (isset($_GET['datos']) && isset($_GET['iv'])) {
                            // Obtenemos los datos encriptados y el IV desde la URL
                            $datosEncriptadosBase64 = $_GET['datos'];
                            $ivBase64 = $_GET['iv'];
                        
                            // Decodificamos el IV desde base64
                            $iv = base64_decode($ivBase64);
                        
                            // Decodificamos los datos encriptados desde base64
                            $datosEncriptados = base64_decode($datosEncriptadosBase64);
                        
                            // Desencriptamos los datos utilizando AES
                            $clave = 'FFww2649xl'; 
                            $datosDesencriptados = openssl_decrypt($datosEncriptados, 'aes-256-cbc', $clave, 0, $iv);
                        
                            // Convertimos los datos desencriptados de JSON a array asociativo
                            $datos = json_decode($datosDesencriptados, true);
                        
                            // Ahora puedes acceder a los datos como antes
                            $numeroOrdenPedido = $datos['numeroOrdenPedido'];
                            $montoTransaccion = $datos['montoTransaccion'];
                            $monedaTransaccion = $datos['monedaTransaccion'];
                            $codigoAutorizacion = $datos['codigoAutorizacion'];
                            $fechaTransaccion = $datos['fechaTransaccion'];
                            $tipoPago = $datos['tipoPago'];
                            $cantidadCuotas = $datos['cantidadCuotas'];
                            $ultimosDigitosTarjeta = $datos['ultimosDigitosTarjeta'];
                            
                            //tipo de pago
                            if($tipoPago == 'VD'){
                                $tpago = 'Debito';
                            }else{
                                $tpago = 'Credito';
                            }
                            
                            // Asegurarse de que las variables sean de tipo numérico antes de realizar la división
                            $montoTransaccion = floatval($montoTransaccion); // Convertir a decimal (número con decimales)
                            $cantidadCuotas = intval($cantidadCuotas); // Convertir a entero (número sin decimales)
                            
                            // Verificar si $cantidadCuotas es mayor a cero para evitar la división por cero
                            if ($cantidadCuotas > 0) {
                                $montoCuota = $montoTransaccion / $cantidadCuotas;
                            } else {
                                // Manejar el caso de división por cero si es necesario
                                // Por ejemplo, mostrar un mensaje de error o asignar un valor por defecto a $montoCuota
                                $montoCuota = 0;
                            }
                        
                            ?>
                                <div class="receipt-info container">
                                    <div class="row justify-content-center m-0 mb-2">
                                        <div class="col">
                                            <h4><b>Datos de transacción</b></h4>
                                            <p>Número de orden de pedido: <?php echo $numeroOrdenPedido; ?></p>
                                            <p>Nombre del comercio: WALCOM.CL</p>
                                            <p>Monto y moneda de la transacción: <?php echo $montoTransaccion . ' ' . $monedaTransaccion; ?></p>
                                            <p>Código de autorización de la transacción: <?php echo $codigoAutorizacion; ?></p>
                                            <p>Fecha de la transacción: <?php echo $fechaTransaccion; ?></p>
                                            <p>Tipo de pago realizado: <?php echo $tpago; ?></p>
                                            <p>Cantidad de cuotas: <?php echo $cantidadCuotas; ?></p>
                                            <p>Monto de cada cuota: <?php echo $montoCuota; ?></p>           <!-- dividimos el monto por la cantidad de cuotas -->   
                                            <p>Cuatro últimos dígitos de la tarjeta bancaria: <?php echo $ultimosDigitosTarjeta; ?></p>
                                            
                                            <!-- productos comprados -->
                                            
                                            <?php
                                            
                                                // Datos de conexión a la base de datos
                                                $servername = "localhost";
                                                $username = "aquitulogo23";
                                                $password = "g-i,F6+{MawJ";
                                                $database = "aquitulogo23_tienda_virtual";
                                                
                                                $conn = new mysqli($servername, $username, $password, $database);
                                                if ($conn->connect_error) {
                                                    die("Error de conexión: " . $conn->connect_error);
                                                }
                                                
                                                // Consulta SQL para unir las tablas 'detalle_pedidos' y 'pedidos'
                                                $sql = "SELECT dp.producto, dp.precio, dp.cantidad, dp.atributos FROM detalle_pedidos dp INNER JOIN pedidos p ON dp.id_pedido = p.id WHERE p.id_transaccion = '$numeroOrdenPedido';";
                                                
                                                $result = $conn->query($sql);
                                                
                                                if ($result->num_rows > 0) {
                                                    // Inicio de la tabla
                                                    echo '<table class="table">';
                                                    echo '<tr><th>Producto</th><th>Precio</th><th>Cantidad</th><th>Atributos</th></tr>';
                                                
                                                    // Procesar los resultados de la consulta
                                                    while ($row = $result->fetch_assoc()) {
                                                        // Obtener los datos de cada fila
                                                        $producto = $row["producto"];
                                                        $precio = $row["precio"];
                                                        $cantidad = $row["cantidad"];
                                                        $atributos = $row["atributos"];
                                                
                                                        // Mostrar los datos en la tabla
                                                        echo '<tr>';
                                                        echo '<td>' . $producto . '</td>';
                                                        echo '<td>' . $precio . '</td>';
                                                        echo '<td>' . $cantidad . '</td>';
                                                        echo '<td>' . $atributos . '</td>';
                                                        echo '</tr>';
                                                    }
                                                
                                                    // Fin de la tabla
                                                    echo '</table>';
                                                } else {
                                                    echo "No se encontraron resultados.";
                                                }
                                                
                                                $conn->close();
                                            ?>
                                            
                                            <hr>
                                            
                                            <div class="receipt-total">Total: <?php echo $montoTransaccion . ' ' . $monedaTransaccion; ?></div>
                                        </div>
                                    </div>
                                    
                                </div>
                                
                                
                                
                            <?php
                            
                        } else {
                            // Si los datos encriptados y el IV no están presentes en la URL, puede que haya habido un error en la redirección
                            echo "error al cargar datos de URL";
                        }
                    ?>
                    
                </div>
            </div>
            
        </div>
    </div>
    
    <div id="countdown">Serás redirigido a la tienda en <span id="seconds">15</span> segundos...</div>
    <div> <a href="https://aquitulogo.cl/tienda/"><button class="btn btn-util">Volver a la tienda</button></a></div>

    <!-- Start Footer -->
    <footer class="bg-dark" id="tempaltemo_footer" style="position:absolute; bottom:0; width:100%;">
        
        <div class="w-100 bg-black py-3">
            <div class="container">
                <div class="row pt-2">
                    <div class="col-12">
                        <p class="text-left text-light p-4">
                            Copyright &copy; <?php echo date('Y'); ?> Walcom.cl
                        </p>
                    </div>
                </div>
            </div>
        </div>
    
    </footer>
    <!-- End Footer -->
    
    <!-- Script para el contador regresivo y redirección a la tienda -->
    <script>
        // Función para actualizar el contador regresivo
        function updateCountdown(seconds) {
            document.getElementById("seconds").textContent = seconds;
        }

        // Contador regresivo de 15 segundos
        var countdownSeconds = 15;
        updateCountdown(countdownSeconds);

        var countdownInterval = setInterval(function() {
            countdownSeconds--;
            updateCountdown(countdownSeconds);
            if (countdownSeconds === 0) {
                clearInterval(countdownInterval);
                // Redireccionar a la tienda después de 15 segundos
                window.location.href = "https://aquitulogo.cl/tienda/";
            }
        }, 1000);
        
        localStorage.clear();
        
    </script>
    
</body>
</html>

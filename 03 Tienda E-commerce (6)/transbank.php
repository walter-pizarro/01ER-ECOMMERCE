<?php
    $tipo = $_POST["tipo"];
    
    if (isset($_POST["tipo"]) && $_POST["tipo"] === "planes") {
        
        session_start();
        
        // La variable "tipo" se recibió y su valor es "planes"
        // Puedes realizar las acciones que desees aquí
        //echo "La variable 'tipo' es igual a 'planes'.";
        
        // Verificar si ya se ha creado una ID de sesi車n
        if (isset($_SESSION['id_session'])) {
            //echo "Tu ID de sesion existente es: " . $_SESSION['id_session'];
        } else {
            // Generar una nueva ID de sesi車n
            $_SESSION['id_session'] = session_id();
            //echo "Tu nueva ID de sesion es: " . $_SESSION['id_session'];
        }
        
        date_default_timezone_set('America/Santiago');
        $fechas = date('Y-m-d H:i:s');
        
        //muestra de errores
        ini_set('display_errors', 1);
        ini_set('display_startup_errors', 1);
        error_reporting(E_ALL);
        
        // Obtener la cadena JSON de la variable $_POST
        $jsonDatosRecibidos = $_POST['datos_json'];
        
        // Decodificar el JSON a un array asociativo
        $arrayDatosRecibidos = json_decode($jsonDatosRecibidos, true);
        
            // datos tomados
            /*echo "<h2>TESTEO PARA DATOS 'RECIBIDOS'</h2><br>";
            
            echo "ID: " . $arrayDatosRecibidos['id'] . "<br>";
            echo "Plan: " . $arrayDatosRecibidos['plan'] . "<br>";
            echo "Descripción: " . $arrayDatosRecibidos['descripcion'] . "<br>";
            echo "Precio del plan: " . $arrayDatosRecibidos['precio_plan'] . "<br>";
            echo "Precio de instalación: " . $arrayDatosRecibidos['precio_instalacion'] . "<br>";
            echo "Precio CLP: " . $arrayDatosRecibidos['precio_clp'] . "<br>";
            echo "Condición: " . $arrayDatosRecibidos['condicion'] . "<br><br><hr>";*/
            
            //DATOS PARA BD DETALLE PLANES
            $id_detalle = $_POST["id_detalle"];
            $id_cliente = $_POST["id_cliente"];
            $id_plan = $_POST["id_plan"];
            $precio = $arrayDatosRecibidos['precio_plan'];
            $fecha = date('Y-m-d');
            $hora = date('H:i:s');
            $id_user = 1;
            $estado = 1;
            $precio_clp_pago = $arrayDatosRecibidos['precio_clp'];
            
            $documento = $_POST["documento"];
            
            // BD: PAGOS PLANES
            /*echo "<h2>TESTEO PARA BD 'DETALLE_PLANES'</h2><br>";
            
            echo "ID DETALLE: " . $id_detalle . "<br>";
            echo "ID CLIENTE: " . $id_plan . "<br>";
            echo "ID PLAN: " . $id_plan . "<br>";
            echo "PRECIO: " . $precio . "<br>";
            echo "FECHA: " . $fecha . "<br>";
            echo "HORA: " . $hora . "<br>";
            echo "ID USER: " . $id_user . "<br>";
            echo "ESTADO: " . $estado . "<br><br><hr>";*/
            
            function generarOrdenCompra()
            {
                // Caracteres permitidos (numeros y letras en mayusculas)
                $caracteres = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
            
                // Longitud de la orden de compra
                $longitudOrdenCompra = 17;
            
                // Generar 4 o 5 letras en mayusculas
                $numLetras = rand(4, 5);
                $ordenCompra = '';
                for ($i = 0; $i < $numLetras; $i++) {
                    $ordenCompra .= $caracteres[rand(10, 35)]; // 10 al 35 son letras en mayusculas en el string $caracteres
                }
            
                // Generar el resto de caracteres como numeros
                $numCaracteres = $longitudOrdenCompra - $numLetras;
                for ($i = 0; $i < $numCaracteres; $i++) {
                    $ordenCompra .= $caracteres[rand(0, 9)]; // 0 al 9 son numeros en el string $caracteres
                }
            
                // Mezclar aleatoriamente los caracteres
                $ordenCompra = str_shuffle($ordenCompra);
            
                return $ordenCompra;
            }
            // Generar la orden de compra con 17 caracteres
            $ordenCompra = generarOrdenCompra();
            
            //datos para transbank
            $total = $precio_clp_pago;
            $session_id = $_SESSION['id_session'];
            $return_url = "https://aquitulogo.cl/tienda/procesar_estado_compra.php";
            
            //testeo de datos para transbank
            //echo "Monto: " . $total . "<br>";
            //echo "orden de compra: " . $ordenCompra . "<br>";
            //echo "id sesion: " . $session_id . "<br>";
            //echo "url: " . $return_url . "<br><br>";
        
         
        function get_ws($data,$method,$type,$endpoint){
            
            $curl = curl_init();
            
            if($type=='live'){
        		$TbkApiKeyId='597043249735';
        		$TbkApiKeySecret='a2fdbcd54daaba465cfdfd3f8c98bb66';
                $url="https://webpay3g.transbank.cl".$endpoint;//Live
            }else{
        		$TbkApiKeyId='597055555532';
        		$TbkApiKeySecret='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C';
                $url="https://webpay3gint.transbank.cl".$endpoint;//Testing
            }
            
            curl_setopt_array($curl, array(
              CURLOPT_URL => $url,
              CURLOPT_RETURNTRANSFER => true,
              CURLOPT_ENCODING => '',
              CURLOPT_MAXREDIRS => 10,
              CURLOPT_TIMEOUT => 0,
              CURLOPT_FOLLOWLOCATION => true,
              CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
              CURLOPT_CUSTOMREQUEST => $method,
              CURLOPT_POST => true,
              CURLOPT_POSTFIELDS => $data,
              CURLOPT_HTTPHEADER => array(
                'Tbk-Api-Key-Id: '.$TbkApiKeyId.'',
                'Tbk-Api-Key-Secret: '.$TbkApiKeySecret.'',
                'Content-Type: application/json'
              ),
            ));
            
            $response = curl_exec($curl);
            $httpCode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
            
            curl_close($curl);
            //echo $response;
            
            //return json_decode($response);
            
            if ($httpCode === 200) {
                // La solicitud se realiz車 con 谷xito
                $responseData = json_decode($response);
                $responseData->success = true;
                echo "la solicitud se envio con exito";
                return $responseData;
            } else {
                // Hubo un error en la solicitud
                $responseData = json_decode($response, true);
                $responseData['success'] = false;
                echo "error en la solicitud";
                return $responseData;
            }
        }
        
        $baseurl = "https://" . $_SERVER['HTTP_HOST'] . $_SERVER['PHP_SELF'];
        $url="https://webpay3g.transbank.cl/";//Live
        $url="https://webpay3gint.transbank.cl/";//Testing
        
        $action = isset($_GET["action"]) ? $_GET["action"] : 'init';
        $message=null;
        $post_array = false;
        
        switch ($action) {
            
            case "init":
                $message.= 'init';
                $buy_order=$ordenCompra;
                $session_id= $session_id;
                $amount=$total;
                $return_url = "https://aquitulogo.cl/tienda/procesar_estado_compra.php?action=getResult&documento=$documento";
        		$type="live";    //sandbox para prueba y live para produccion
                    $data='{
                            "buy_order": "'.$ordenCompra.'",
                            "session_id": "'.$session_id.'",
                            "amount": '.$amount.',
                            "return_url": "'.$return_url.'"
                            }';
                    $method='POST';
                    $endpoint='/rswebpaytransaction/api/webpay/v1.0/transactions';
                    
                    $response = get_ws($data,$method,$type,$endpoint);
                    $message.= "<pre>";
                    $message.= print_r($response,TRUE);
                    $message.= "</pre>";
                    $url_tbk = $response->url;
                    $token = $response->token;
                    $submit='Continuar!';
        
            break;
        
            case "getResult":
                
                $message.= "<pre>".print_r($_POST,TRUE)."</pre>";
                if (!isset($_POST["token_ws"]))
                    break;
        
                /** Token de la transacci車n */
                $token = filter_input(INPUT_POST, 'token_ws');
                
                $request = array(
                    "token" => filter_input(INPUT_POST, 'token_ws')
                );
                
                $data='';
        		$method='PUT';
        		$type='sandbox';
        		$endpoint='/rswebpaytransaction/api/webpay/v1.0/transactions/'.$token;
        		
                $response = get_ws($data,$method,$type,$endpoint);
               
                $message.= "<pre>";
                $message.= print_r($response,TRUE);
                $message.= "</pre>";
                
                $url_tbk = $baseurl."?action=getStatus";
                $submit='Ver Status!';
                
                break;
                
            case "getStatus":
                
                if (!isset($_POST["token_ws"]))
                    break;
        
                /** Token de la transacci車n */
                $token = filter_input(INPUT_POST, 'token_ws');
                
                $request = array(
                    "token" => filter_input(INPUT_POST, 'token_ws')
                );
                
                $data='';
        		$method='GET';
        		$type='sandbox';
        		$endpoint='/rswebpaytransaction/api/webpay/v1.0/transactions/'.$token;
        		
                $response = get_ws($data,$method,$type,$endpoint);
               
                $message.= "<pre>";
                $message.= print_r($response,TRUE);
                $message.= "</pre>";
                
                $url_tbk = $baseurl."?action=refund";
                $submit='Refund!';
                break;
                
            case "refund":
                
                if (!isset($_POST["token_ws"]))
                    break;
        
                /** Token de la transacci車n */
                $token = filter_input(INPUT_POST, 'token_ws');
                
                $request = array(
                    "token" => filter_input(INPUT_POST, 'token_ws')
                );
                $amount=15000;
                $data='{
                          "amount": '.$amount.'
                        }';
        		$method='POST';
        		$type='sandbox';
        		$endpoint='/rswebpaytransaction/api/webpay/v1.0/transactions/'.$token.'/refunds';
        		
                $response = get_ws($data,$method,$type,$endpoint);
               
                $message.= "<pre>";
                $message.= print_r($response,TRUE);
                $message.= "</pre>";
                $submit='Crear nueva!';
                $url_tbk = $baseurl;
                break;        
        }        
    
    ?>   
        
        
    <!doctype html>
    <html lang="es">
            <head>
                <meta charset="utf-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                <meta name="description" content="Webpay Plus Mall">
                <meta name="author" content="VendoOnline.cl">
            
                <title>Pagos</title>
                <style>
                    .container {
                      height: 200px;
                      position: relative;
                      text-align: center;
                      
                    }
                    
                    .vertical-center {
                        margin-top: 20%;
                      /*margin: 0;
                      position: absolute;
                      top: 50%;
                      -ms-transform: translateY(-50%);
                      transform: translateY(-50%);*/
                    }
                    .lds-hourglass {
                      display: inline-block;
                      position: relative;
                      width: 80px;
                      height: 80px;
                    }
                    .lds-hourglass:after {
                      content: " ";
                      display: block;
                      border-radius: 50%;
                      width: 0;
                      height: 0;
                      margin: 8px;
                      box-sizing: border-box;
                      border: 32px solid purple;
                      border-color: purple transparent purple transparent;
                      animation: lds-hourglass 1.2s infinite;
                    }
                    @keyframes lds-hourglass {
                      0% {
                        transform: rotate(0);
                        animation-timing-function: cubic-bezier(0.55, 0.055, 0.675, 0.19);
                      }
                      50% {
                        transform: rotate(900deg);
                        animation-timing-function: cubic-bezier(0.215, 0.61, 0.355, 1);
                      }
                      100% {
                        transform: rotate(1800deg);
                      }
                    }
                </style>
            </head>
            <body>
                <div class="container">
                  <div class="vertical-center">
                      <div class="lds-hourglass"></div>
                      <img src="WebpayPlus_FB_300px.png">
                      <p><?php //echo $message; ?></p>
                        <?php if (strlen($url_tbk)) { ?>
                        <form name="brouterForm" id="brouterForm"  method="POST" action="<?=$url_tbk?>" style="display:block;">
                          <input type="hidden" name="token_ws" value="<?=$token?>" />
                          <input type="submit" value="<?=(($submit)? $submit : 'Cargando...')?>" style="border: 1px solid #6b196b;
                            border-radius: 4px;
                            background-color: #6b196b;
                            color: #fff;
                            font-family: Roboto,Arial,Helvetica,sans-serif;
                            font-size: 1.14rem;
                            font-weight: 500;
                            margin: auto 0 0;
                            padding: 12px;
                            position: relative;
                            text-align: center;
                            -webkit-transition: .2s ease-in-out;
                            transition: .2s ease-in-out;
                            max-width: 200px;" />
                        </form>
                        <script>
                    
                        var auto_refresh = setInterval(
                        function()
                        {
                            //submitform();
                        }, 15000);
                    //}, 5000);
                        function submitform()
                        {
                          //alert('test');
                          document.brouterForm.submit();
                        }
                        </script>
                    <?php } ?>
                    </div>
                </div>
            </body>
        </html>
        
        <?php
        
    } else {
        // La variable "tipo" no se recibió o su valor no es "planes"
        // Puedes manejar este caso o mostrar algún mensaje de error
        //echo "La variable 'tipo' no se recibió o su valor no es 'planes'.";
        
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
        
        date_default_timezone_set('America/Santiago');
        $fecha = date('Y-m-d H:i:s');
        
        //muestra de errores
        ini_set('display_errors', 1);
        ini_set('display_startup_errors', 1);
        error_reporting(E_ALL);
        
        // Datos de conexión a la base de datos
        $servername = "localhost";
        $username = "aquitulogo23";
        $password = "g-i,F6+{MawJ";
        $database = "aquitulogo23_tienda_virtual";
        
        // Crear una conexión a la base de datos
        $conectar = new mysqli($servername, $username, $password, $database);
        
        // Verificar si la conexión fue exitosa
        if ($conectar->connect_error) {
            die("Conexión fallida: " . $conectar->connect_error);
        }

        
        if ($_SERVER["REQUEST_METHOD"] === "POST") {
            
            // Recibir los datos del formulario
            $buy_order = $_POST["buy_order"];
            $session_id = $_SESSION['id_session'];
            $total = $_POST["amount"];
            // Paso 1: Eliminar comas
            $total_sin_comas = str_replace(',', '', $total); // Valor sin comas: "86000"
            
            // Paso 2: Convertir a entero
            $total_entero = (int) $total_sin_comas; // Valor entero: 86000
            
            //echo $total_entero;

            //echo "to " . $total;
            $pesosChilenos = round($total_entero);
            $return_url = "https://aquitulogo.cl/tienda/procesar_estado_compra.php";
            
            // Recibir el JSON de los datos y convertirlo en un array
            $datosJSON = $_POST["datos"];
            $datos = json_decode($datosJSON, true);
            
            $sumaPrecios = 0;
            
            // Mostrar los datos recibidos
            if (!empty($datos)) {
                //echo "<h1>Datos recibidos de los productos:</h1>";
                //echo "<ul>";
        
                foreach ($datos as $producto) {
                    /*echo "<li>ID: " . $producto['id'] . "</li>";
                    echo "<li>Nombre: " . $producto['nombre'] . "</li>";
                    echo "<li>Atributo MP: " . $producto['atributoMP'] . "</li>";
                    echo "<li>Cantidad: " . $producto['cantidad'] . "</li>";
                    echo "<li>Precio: " . $producto['precio'] . "</li>";
                    echo "<br>";*/
                    
                    $sumaPrecios += $producto['precio'];
                }
                
                // Formatear la suma total de precios con 2 decimales y guardarla en otra variable
                $sumaFormateada = number_format($sumaPrecios, 2);
                
                // Mostrar la suma total de precios formateada con 2 decimales
                //echo "La suma total de precios es: " . $sumaFormateada;
        
               // echo "</ul>";
            } else {
                echo "<p>No se han recibido datos de productos.</p>";
            }
            
            function generarOrdenCompra()
            {
                // Caracteres permitidos (numeros y letras en mayusculas)
                $caracteres = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
            
                // Longitud de la orden de compra
                $longitudOrdenCompra = 17;
            
                // Generar 4 o 5 letras en mayusculas
                $numLetras = rand(4, 5);
                $ordenCompra = '';
                for ($i = 0; $i < $numLetras; $i++) {
                    $ordenCompra .= $caracteres[rand(10, 35)]; // 10 al 35 son letras en mayusculas en el string $caracteres
                }
            
                // Generar el resto de caracteres como numeros
                $numCaracteres = $longitudOrdenCompra - $numLetras;
                for ($i = 0; $i < $numCaracteres; $i++) {
                    $ordenCompra .= $caracteres[rand(0, 9)]; // 0 al 9 son numeros en el string $caracteres
                }
            
                // Mezclar aleatoriamente los caracteres
                $ordenCompra = str_shuffle($ordenCompra);
            
                return $ordenCompra;
            }
            
            // Generar la orden de compra con 17 caracteres
            $ordenCompra = generarOrdenCompra();
            
            //testear si se recibio los datos
            //echo "Monto Total = USD" . $sumaFormateada . " - CLP " . $pesosChilenos . "<br>";
        
            //variables para BD PEDIDOS
            $ID_Transaccion = "$ordenCompra";
            $Metodo = "TRANSBANK";
            $Monto = $sumaFormateada;
            $Estado = "PROCESANDO";
            $Fecha = $fecha;
            $Email = "";
            $Nombre = "";
            $Apellido = "";
            $Direccion = "";
            $Ciudad = "";
            $ID_cliente = $_SESSION['idCliente'];
            $Proceso = 1;
            $MontoCLP = $pesosChilenos;
        
            // Asignar el valor a la variable de sesión
            $_SESSION['ID_Transaccion'] = $ID_Transaccion;
        
            //obtener los datos del usuario
            $sqlc = "SELECT * FROM clientes WHERE id = $ID_cliente";
        
            // Ejecutar la consulta y obtener el resultado
            $resultado = $conectar->query($sqlc);
            
            // Verificar si se encontraron resultados
            if ($resultado->num_rows > 0) {
                // Recorrer los resultados y mostrar los datos del cliente
                while ($row = $resultado->fetch_assoc()) {
                    
                    $Nombre = $row["nombre"];
                    $Apellido = $row["apellido"];
                    $Email = $row["correo"];
                    $Direccion = $row["direccion"];
                    $Telefono = $row["telefono"];
                    
                }
            } else {
                echo "No se encontraron resultados para el ID de cliente: $ID_cliente";
            }
        
            //TESTEO
            /*echo "<h2>TESTEO PARA BD PEDIDO</h2><br>";
            
            echo "ID Transaccion: " . $ID_Transaccion . "<br>";
            echo "Metodo: " . $Metodo . "<br>";
            echo "Monto: " . $Monto . "<br>";
            echo "Estado: " . $Estado . "<br>";
            echo "Fecha: " . $Fecha . "<br>";
            echo "Email: " . $Email . "<br>";
            echo "Nombre: " . $Nombre . "<br>";
            echo "Apellido: " . $Apellido . "<br>";
            echo "Direccion: " . $Direccion . "<br>";
            echo "ID_cliente: " . $ID_cliente . "<br>";
            echo "Proceso: " . $Proceso . "<br>";
            echo "Monto en CLP: " . $MontoCLP . "<br><br>";*/
            
            //registros a base de datos
            $sql = "INSERT INTO `pedidos` (`id`, `id_transaccion`, `metodo`, `monto`, `estado`, `fecha`, `email`, `nombre`, `apellido`, `direccion`, `id_cliente`, `proceso`, `precio_clp`) 
                VALUES (NULL, '$ID_Transaccion', '$Metodo', '$Monto', '$Estado', '$Fecha', '$Email', '$Nombre', '$Apellido', '$Direccion', '$ID_cliente', '$Proceso', $MontoCLP)";
        
            // Ejecutar la consulta
            if ($conectar->query($sql) === TRUE) {
            
                // La inserción fue exitosa
                $ultimoIDInsertado = $conectar->insert_id;
                //echo "El pedido ha sido registrado correctamente. ID del pedido: " . $ultimoIDInsertado;
            } else {
            
                // Ocurrió un error durante la inserción
                //echo "Error al registrar el pedido: " . $conectar->error;
                
            }
        
            
            
            //echo "<hr>";
            
            //echo "<h2>TESTEO PARA BD DETALLE_PEDIDO</h2><br>";
            
            // Declarar arreglos para almacenar los atributos
            $nombresProductos = array();
            $cantidades = array();
            $precios = array();
            $atributosMP = array();
            $idProductos = array();
        
            // Declarar la consulta preparada para la inserción en detalle_pedidos
            $sql2 = "INSERT INTO `detalle_pedidos` (`id`, `producto`, `precio`, `cantidad`, `atributos`, `id_pedido`, `id_producto`) VALUES 
                (NULL, ?, ?, ?, ?, ?, ?)";
        
            // Preparar la consulta
            $stmt = $conectar->prepare($sql2);
        
            // Vincular parámetros con los placeholders de la consulta
            $stmt->bind_param("sddssi", $nombre_p, $precio, $cantidad_P, $atributoMP, $ultimoIDInsertado, $id_producto);
        
            foreach ($datos as $producto) {
                /*echo "<li>Producto: " . $producto['nombre'] . "</li>";
                echo "<li>Cantidad: " . $producto['cantidad'] . "</li>";
                echo "<li>Precio: " . $producto['precio'] . "</li>";
                echo "<li>Atributo MP: " . $producto['atributoMP'] . "</li>";
                echo "<li>ID Pedido: " . $ultimoIDInsertado . "</li>";
                echo "<li>ID Producto: " . $producto['id'] . "</li>";
                echo "<br>";*/
            
                // Almacenar los atributos del producto actual en los arreglos correspondientes
                $nombresProductos[] = $producto['nombre'];
                $cantidades[] = $producto['cantidad'];
                $precios[] = $producto['precio'];
                $atributosMP[] = $producto['atributoMP'];
                $idProductos[] = $producto['id'];
                
                // Asignar valores a los parámetros de la consulta preparada
                $nombre_p = $producto['nombre'];
                $precio = $producto['precio'];
                $cantidad_P = $producto['cantidad'];
                $atributoMP = $producto['atributoMP'];
                $id_producto = $producto['id'];
                
                // Ejecutar la consulta preparada
                if ($stmt->execute()) {
                    // La inserción fue exitosa
                } else {
                    // Ocurrió un error durante la inserción
                    //echo "Error al registrar el pedido: " . $conectar->error;
                }
            }
            
            // Mostrar la orden de compra
            //echo "Orden de compra: " . $ordenCompra . "<br>";
        
            $buy_order = $ordenCompra;
        
            // Crear la estructura $data con los datos recibidos
            $data = array(
                "buy_order" => $buy_order,
                "session_id" => $session_id,
                "amount" => $pesosChilenos,
                "return_url" => $return_url,
            );
        
        }
        
        
        function get_ws($data,$method,$type,$endpoint){
            
            $curl = curl_init();
            
            if($type=='live'){
        		$TbkApiKeyId='597043249735';
        		$TbkApiKeySecret='a2fdbcd54daaba465cfdfd3f8c98bb66';
                $url="https://webpay3g.transbank.cl".$endpoint;//Live
            }else{
        		$TbkApiKeyId='597055555532';
        		$TbkApiKeySecret='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C';
                $url="https://webpay3gint.transbank.cl".$endpoint;//Testing
            }
            
            curl_setopt_array($curl, array(
              CURLOPT_URL => $url,
              CURLOPT_RETURNTRANSFER => true,
              CURLOPT_ENCODING => '',
              CURLOPT_MAXREDIRS => 10,
              CURLOPT_TIMEOUT => 0,
              CURLOPT_FOLLOWLOCATION => true,
              CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
              CURLOPT_CUSTOMREQUEST => $method,
              CURLOPT_POST => true,
              CURLOPT_POSTFIELDS => $data,
              CURLOPT_HTTPHEADER => array(
                'Tbk-Api-Key-Id: '.$TbkApiKeyId.'',
                'Tbk-Api-Key-Secret: '.$TbkApiKeySecret.'',
                'Content-Type: application/json'
              ),
            ));
            
            $response = curl_exec($curl);
            $httpCode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
            
            curl_close($curl);
            //echo $response;
            
            //return json_decode($response);
            
            if ($httpCode === 200) {
                // La solicitud se realiz車 con 谷xito
                $responseData = json_decode($response);
                $responseData->success = true;
                //echo "la solicitud se envio con exito";
                return $responseData;
            } else {
                // Hubo un error en la solicitud
                $responseData = json_decode($response, true);
                $responseData['success'] = false;
                //echo "error en la solicitud";
                return $responseData;
            }
        }
        
        $baseurl = "https://" . $_SERVER['HTTP_HOST'] . $_SERVER['PHP_SELF'];
        $url="https://webpay3g.transbank.cl/";//Live
        $url="https://webpay3gint.transbank.cl/";//Testing
        
        $action = isset($_GET["action"]) ? $_GET["action"] : 'init';
        $message=null;
        $post_array = false;
        
        switch ($action) {
            
            case "init":
                $message.= 'init';
                $buy_order=$ordenCompra;
                $session_id=$_SESSION['id_session'];
                $amount=$pesosChilenos;
                $return_url = "https://aquitulogo.cl/tienda/procesar_estado_compra.php?action=getResult&id_trans=$ID_Transaccion";
        		$type="live";    //sandbox para prueba y live para produccion
                    $data='{
                            "buy_order": "'.$ordenCompra.'",
                            "session_id": "'.$session_id.'",
                            "amount": '.$amount.',
                            "return_url": "'.$return_url.'"
                            }';
                    $method='POST';
                    $endpoint='/rswebpaytransaction/api/webpay/v1.0/transactions';
                    
                    $response = get_ws($data,$method,$type,$endpoint);
                    $message.= "<pre>";
                    $message.= print_r($response,TRUE);
                    $message.= "</pre>";
                    $url_tbk = $response->url;
                    $token = $response->token;
                    $submit='Continuar!';
        
            break;
        
            case "getResult":
                
                $message.= "<pre>".print_r($_POST,TRUE)."</pre>";
                if (!isset($_POST["token_ws"]))
                    break;
        
                /** Token de la transacci車n */
                $token = filter_input(INPUT_POST, 'token_ws');
                
                $request = array(
                    "token" => filter_input(INPUT_POST, 'token_ws')
                );
                
                $data='';
        		$method='PUT';
        		$type='sandbox';
        		$endpoint='/rswebpaytransaction/api/webpay/v1.0/transactions/'.$token;
        		
                $response = get_ws($data,$method,$type,$endpoint);
               
                $message.= "<pre>";
                $message.= print_r($response,TRUE);
                $message.= "</pre>";
                
                $url_tbk = $baseurl."?action=getStatus";
                $submit='Ver Status!';
                
                break;
                
            case "getStatus":
                
                if (!isset($_POST["token_ws"]))
                    break;
        
                /** Token de la transacci車n */
                $token = filter_input(INPUT_POST, 'token_ws');
                
                $request = array(
                    "token" => filter_input(INPUT_POST, 'token_ws')
                );
                
                $data='';
        		$method='GET';
        		$type='sandbox';
        		$endpoint='/rswebpaytransaction/api/webpay/v1.0/transactions/'.$token;
        		
                $response = get_ws($data,$method,$type,$endpoint);
               
                $message.= "<pre>";
                $message.= print_r($response,TRUE);
                $message.= "</pre>";
                
                $url_tbk = $baseurl."?action=refund";
                $submit='Refund!';
                break;
                
            case "refund":
                
                if (!isset($_POST["token_ws"]))
                    break;
        
                /** Token de la transacci車n */
                $token = filter_input(INPUT_POST, 'token_ws');
                
                $request = array(
                    "token" => filter_input(INPUT_POST, 'token_ws')
                );
                $amount=15000;
                $data='{
                          "amount": '.$amount.'
                        }';
        		$method='POST';
        		$type='sandbox';
        		$endpoint='/rswebpaytransaction/api/webpay/v1.0/transactions/'.$token.'/refunds';
        		
                $response = get_ws($data,$method,$type,$endpoint);
               
                $message.= "<pre>";
                $message.= print_r($response,TRUE);
                $message.= "</pre>";
                $submit='Crear nueva!';
                $url_tbk = $baseurl;
                break;        
        }        
        ?>
        
        <!doctype html>
        <html lang="es">
            <head>
                <meta charset="utf-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                <meta name="description" content="Webpay Plus Mall">
                <meta name="author" content="VendoOnline.cl">
            
                <title>Pagos</title>
                <style>
                    .container {
                      height: 200px;
                      position: relative;
                      text-align: center;
                      
                    }
                    
                    .vertical-center {
                        margin-top: 20%;
                      /*margin: 0;
                      position: absolute;
                      top: 50%;
                      -ms-transform: translateY(-50%);
                      transform: translateY(-50%);*/
                    }
                    .lds-hourglass {
                      display: inline-block;
                      position: relative;
                      width: 80px;
                      height: 80px;
                    }
                    .lds-hourglass:after {
                      content: " ";
                      display: block;
                      border-radius: 50%;
                      width: 0;
                      height: 0;
                      margin: 8px;
                      box-sizing: border-box;
                      border: 32px solid purple;
                      border-color: purple transparent purple transparent;
                      animation: lds-hourglass 1.2s infinite;
                    }
                    @keyframes lds-hourglass {
                      0% {
                        transform: rotate(0);
                        animation-timing-function: cubic-bezier(0.55, 0.055, 0.675, 0.19);
                      }
                      50% {
                        transform: rotate(900deg);
                        animation-timing-function: cubic-bezier(0.215, 0.61, 0.355, 1);
                      }
                      100% {
                        transform: rotate(1800deg);
                      }
                    }
                </style>
            </head>
            <body>
                <div class="container">
                  <div class="vertical-center">
                      <div class="lds-hourglass"></div>
                      <img src="WebpayPlus_FB_300px.png">
                      <p><?php //echo $message; ?></p>
                        <?php if (strlen($url_tbk)) { ?>
                        <form name="brouterForm" id="brouterForm"  method="POST" action="<?=$url_tbk?>" style="display:block;">
                          <input type="hidden" name="token_ws" value="<?=$token?>" />
                          <input type="submit" value="<?=(($submit)? $submit : 'Cargando...')?>" style="border: 1px solid #6b196b;
                            border-radius: 4px;
                            background-color: #6b196b;
                            color: #fff;
                            font-family: Roboto,Arial,Helvetica,sans-serif;
                            font-size: 1.14rem;
                            font-weight: 500;
                            margin: auto 0 0;
                            padding: 12px;
                            position: relative;
                            text-align: center;
                            -webkit-transition: .2s ease-in-out;
                            transition: .2s ease-in-out;
                            max-width: 200px;" />
                        </form>
                        <script>
                    
                        var auto_refresh = setInterval(
                        function()
                        {
                            //submitform();
                        }, 15000);
                    //}, 5000);
                        function submitform()
                        {
                          //alert('test');
                          document.brouterForm.submit();
                        }
                        </script>
                    <?php } ?>
                    </div>
                </div>
            </body>
        </html>
        
        <?php
    }
 ?>   


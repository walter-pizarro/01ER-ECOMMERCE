<?php
class Productos extends Controller
{
    public function __construct()
    {
        parent::__construct();
        session_start();
        if (empty($_SESSION['nombre_usuario'])) {
            header('Location: ' . BASE_URL . 'admin');
            exit;
        }
    }
    public function index()
    {
        $data['title'] = 'productos';
        $data['categorias'] = $this->model->getDatos('categorias');
        $data['colores'] = $this->model->getDatos('colores');
        $data['tallas'] = $this->model->getDatos('tallas');
        $this->views->getView('admin/productos', "index", $data);
    }
    public function listar()
    {
        $data = $this->model->getProductos(1);
        for ($i = 0; $i < count($data); $i++) {
            if ($data[$i]['descargable']) {
                $accion = '';
                $data[$i]['cantidad'] = '<span class="badge bg-info">ILIMITADO</span>';
            } else {
                $accion = '<li><a class="dropdown-item" href="#" onclick="mantenimiento(' . $data[$i]['id'] . ')">Atributos</a>
                </li>';
                $data[$i]['cantidad'] = '<span class="badge bg-success">' . $data[$i]['cantidad'] . '</span>';
            }

            $data[$i]['imagen'] = '<a href="#" data-bs-toggle="modal" data-bs-target="#modalIMG" data-id="' . $data[$i]['id'] . '">
    <img class="img-thumbnail" src="' . $data[$i]['imagen'] . '" alt="' . $data[$i]['nombre'] . '" width="50">
</a>';
            $data[$i]['accion'] = '
            <div class="btn-group">
				<button type="button" class="btn btn-outline-secondary dropdown-toggle dropdown-toggle-split" data-bs-toggle="dropdown" aria-expanded="false">	<span class="visually-hidden">Toggle Dropdown</span>
				</button>
				<ul class="dropdown-menu">
					<li><a class="dropdown-item" href="#" onclick="agregarImagenes(' . $data[$i]['id'] . ')"><i class="fas fa-images"></i> Galeria</a>
					</li>
					<!--<li><a class="dropdown-item" href="#" onclick="editPro(' . $data[$i]['id'] . ')"><i class="fas fa-edit"></i> Editar</a>
					</li>-->
					<li><a class="dropdown-item" href="#" data-bs-toggle="modal" data-bs-target="#miModal" data-id="' . $data[$i]['id'] . '"><i class="fas fa-edit"></i> Editar</a></li>

					<li><a class="dropdown-item" href="#" onclick="eliminarPro(' . $data[$i]['id'] . ')"><i class="fas fa-trash"></i> Eliminar</a>
					</li>
					<li>
						<hr class="dropdown-divider">
					</li>
					' . $accion . '
					
					 
                    
                    
				</ul>
			</div>';
        }
        echo json_encode($data);
        die();
    }

    public function registrar()
    {
        if (isset($_POST['nombre']) && isset($_POST['precio'])) {
            $nombre = $_POST['nombre'];
            
            $costo_impresion = $_POST['costo_impresion']; //NUEVO
            $margen = $_POST['margen']; //NUEVO
            
            $margenDecimal = $margen / 100; // Convertir a decimal (0.20 en este caso)

            // Formatear el valor con 2 decimales
            $margenFormateado = number_format($margenDecimal, 2, '.', '');
            
            $precio_costo = $_POST['precio_costo']; //NUEVO
            $precio = $_POST['precio'];
            $precio_clp = $_POST['precio_clp'];//NUEVO
            $cantidad = (!empty($_POST['cantidad'])) ? $_POST['cantidad'] : 0;
            $descargable = (!empty($_POST['descargable'])) ? 1 : 0;
            $descripcion = $_POST['descripcion'];
            $categoria = $_POST['categoria'];
            $imagen = $_FILES['imagen'];
            $tmp_name = $imagen['tmp_name'];
            $id = $_POST['id'];
            $ruta = 'assets/temp/';
            $nombreImg = date('YmdHis');
            
            if (empty($nombre) || empty($precio) || empty($precio_clp)) {
                $respuesta = array('msg' => 'todo los campos son requeridos', 'icono' => 'warning');
            } else {
                ###### MOVER IMG TEMPORALMENTE ########
                if (!empty($imagen['name'])) {
                    if (!file_exists('assets/temp')) {
                        mkdir('assets/temp');
                    }
                    $destinoTemp = $ruta . $nombreImg . '.jpg';
                    $destino = 'assets/images/productos/' . $nombreImg . '.jpg';
                    move_uploaded_file($tmp_name, $destinoTemp);
                }
                ##### VERIFICAR IMG ACTUAL #####
                if (!empty($_POST['imagen_actual']) && empty($imagen['name'])) {
                    $destino = $_POST['imagen_actual'];
                }

                $link = null;
                if ($descargable == 1) {
                    ##### VERIFICAR ARCHIVOS #####
                    if (empty($_POST['url_actual']) && empty($_POST['ruta'])) {
                        $link = null;
                    } else if (!empty($_POST['url_actual']) && empty($_POST['ruta'])) {
                        $link = $_POST['url_actual'];
                    } else {
                        $link = $_POST['ruta'];
                    }
                }

                ##### VERIFICAR SI EXISTE ID ######
                if (empty($id)) {
                    if ($link == null && $descargable == 1) {
                        $respuesta = array('msg' => 'seleccionar un archivo', 'icono' => 'error');
                    } else {
                        if (empty($imagen['name'])) {
                            $respuesta = array('msg' => 'seleccionar una imagen', 'icono' => 'error');
                        } else {
                            #### REGISTRAR PRODUCTO #####
                            $data = $this->model->registrar($nombre, $descripcion, $precio, $cantidad, $destino, $descargable, $categoria, $precio_clp, $precio_costo, $margenDecimal, $costo_impresion);
                            if ($data > 0) {
                                #### VERIFICAR SI ES DESCARGABLE #####
                                if (!empty($_POST['descargable'])) {
                                    $this->model->registrarUrl($_POST['ruta'], $data);
                                }
                                #### ACORTAR IMAGEN #####
                                $this->acortarImg($imagen['type'], $destinoTemp, $nombreImg);
                                $respuesta = array('msg' => 'producto registrado', 'icono' => 'success');
                            } else {
                                $respuesta = array('msg' => 'error al registrar', 'icono' => 'error');
                            }
                        }
                    }
                } else {
                    if ($link == null && $descargable == 1) {
                        $respuesta = array('msg' => 'seleccionar un archivo', 'icono' => 'error');
                    } else {
                        if (empty($destino)) {
                            $respuesta = array('msg' => 'seleccionar una imagen', 'icono' => 'error');
                        } else {
                            #### MODIFICAR PRODUCTO #####
                            $data = $this->model->modificar($nombre, $descripcion, $precio, $cantidad, $destino, $descargable, $categoria, $id, $precio_clp);
                            if ($data == 1) {
                                #### VERIFICAR SI ES DESCARGABLE #####
                                if (!empty($_POST['descargable'])) {
                                    $this->model->modificarUrl($link, $id);
                                }
                                if (!empty($imagen['name'])) {
                                    $this->acortarImg($imagen['type'], $destinoTemp, $nombreImg);
                                }
                                $respuesta = array('msg' => 'producto modificado', 'icono' => 'success');
                            } else {
                                $respuesta = array('msg' => 'error al modificar', 'icono' => 'error');
                            }
                        }
                    }
                }
            }
            echo json_encode($respuesta);
        }
        die();
    }
    //eliminar pro
    public function delete($idPro)
    {
        if (is_numeric($idPro)) {
            $data = $this->model->eliminar($idPro);
            if ($data == 1) {
                $respuesta = array('msg' => 'producto dado de baja', 'icono' => 'success');
            } else {
                $respuesta = array('msg' => 'error al eliminar', 'icono' => 'error');
            }
        } else {
            $respuesta = array('msg' => 'error desconocido', 'icono' => 'error');
        }
        echo json_encode($respuesta);
        die();
    }
    public function subirArchivos()
    {
        $folder_name = 'assets/archivos/productos/';
        if (!empty($_FILES)) {
            if (!file_exists($folder_name)) {
                mkdir($folder_name);
            }
            $temp_name = $_FILES['file']['tmp_name'];
            $ruta = $folder_name . date('YmdHis') . '_' . $_FILES['file']['name'];
            move_uploaded_file($temp_name, $ruta);
        }
    }
    public function cargarArchivos()
    {
        $result = array();
        $directorio = 'assets/archivos/productos/';
        if (file_exists($directorio)) {
            $imagenes = scandir($directorio);
            if (false !== $imagenes) {
                foreach ($imagenes as $file) {
                    if ('.' != $file && '..' != $file) {
                        array_push($result, $file);
                    }
                }
            }
        }
        echo json_encode($result);
        die();
    }
    //editar pro
    public function edit($idPro)
    {
        if (is_numeric($idPro)) {
            $data = $this->model->getProducto($idPro);
            $data['url'] = '';
            if ($data['descargable']) {
                $ruta = $this->model->getLink($idPro);
                if (!empty($ruta)) {
                    $data['url'] = $ruta['ruta'];
                }                
            }
            echo json_encode($data, JSON_UNESCAPED_UNICODE);
        }
        die();
    }

    public function galeriaImagenes()
    {
        $id = $_POST['idProducto'];
        $folder_name = 'assets/images/productos/' . $id . '/';
        if (!empty($_FILES)) {
            if (!file_exists($folder_name)) {
                mkdir($folder_name);
            }
            $temp_name = $_FILES['file']['tmp_name'];
            $ruta = $folder_name . date('YmdHis') . $_FILES['file']['name'];
            move_uploaded_file($temp_name, $ruta);
        }
    }

    public function verGaleria($id_producto)
    {
        $result = array();
        $directorio = 'assets/images/productos/' . $id_producto;
        if (file_exists($directorio)) {
            $imagenes = scandir($directorio);
            if (false !== $imagenes) {
                foreach ($imagenes as $file) {
                    if ('.' != $file && '..' != $file) {
                        array_push($result, $file);
                    }
                }
            }
        }
        echo json_encode($result);
        die();
    }

    public function eliminarImg()
    {
        $datos = file_get_contents('php://input');
        $json = json_decode($datos, true);
        $destino = 'assets/images/productos/' . $json['url'];
        if (unlink($destino)) {
            $res = array('msg' => 'IMAGEN ELIMINADO', 'icono' => 'success');
        } else {
            $res = array('msg' => 'ERROR AL ELIMINAR', 'icono' => 'error');
        }
        echo json_encode($res);
        die();
    }

    public function eliminarArchivo()
    {
        $datos = file_get_contents('php://input');
        $json = json_decode($datos, true);
        $destino = 'assets/archivos/productos/' . $json['url'];
        if (file_exists($destino)) {
            if (unlink($destino)) {
                $res = array('msg' => 'ARCHIVO ELIMINADO', 'icono' => 'success');
            } else {
                $res = array('msg' => 'ERROR AL ELIMINAR', 'icono' => 'error');
            }
        } else {
            $res = array('msg' => 'EL ARCHIVO YA NO EXISTE', 'icono' => 'warning');
        }
        echo json_encode($res);
        die();
    }

    public function acortarImg($type, $imagen, $nombreImg)
    {
        $imagenNueva = 'assets/images/productos/' . $nombreImg . '.jpg'; //Nueva imagen
        $nAncho = 600; //Nuevo ancho
        $nAlto = 800;  //Nuevo alto
        if ($type == 'image/png') {

            //Creamos una nueva imagen a partir del fichero inicial

            $imagen = imagecreatefrompng($imagen);
            //Obtenemos el tamaño 
            $x = imagesx($imagen);
            $y = imagesy($imagen);

            //Validamos los tamaños y calculamos la relación de aspecto
            if ($x >= $y) {
                $nAncho = $nAncho;
                $nAlto = $nAncho * $y / $x;
            } else {
                $nAlto = $nAlto;
                $nAncho = $x / $y * $nAlto;
            }
            // Crear una nueva imagen, copia y cambia el tamaño de la imagen
            $img = imagecreatetruecolor($nAncho, $nAlto);
            imagecopyresampled($img, $imagen, 0, 0, 0, 0, floor($nAncho), floor($nAlto), $x, $y);

            //Creamos el archivo jpg
            imagepng($img, $imagenNueva);
        } else {

            $imagen = imagecreatefromjpeg($imagen);
            //Obtenemos el tamaño 
            $x = imagesx($imagen);
            $y = imagesy($imagen);

            //Validamos los tamaños y calculamos la relación de aspecto
            if ($x >= $y) {
                $nAncho = $nAncho;
                $nAlto = $nAncho * $y / $x;
            } else {
                $nAlto = $nAlto;
                $nAncho = $x / $y * $nAlto;
            }
            // Crear una nueva imagen, copia y cambia el tamaño de la imagen
            $img = imagecreatetruecolor($nAncho, $nAlto);
            imagecopyresampled($img, $imagen, 0, 0, 0, 0, floor($nAncho), floor($nAlto), $x, $y);

            //Creamos el archivo jpg
            imagejpeg($img, $imagenNueva);
        }
        if (file_exists('assets/temp')) {
            $this->borra_dir('assets/temp');
        }
    }

    public function borra_dir($dir)
    {
        $files = scandir($dir);
        foreach ($files as $file) {
            if ($file != '.' && $file != '..') {
                unlink($dir . '/' . $file);
            }
        }
        rmdir($dir);
    }

    public function getAtributos($id_producto)
    {
        $data['producto'] = $this->model->getProducto($id_producto);
        $data['detalle'] = $this->model->getAtributos($id_producto);
        echo json_encode($data, JSON_UNESCAPED_UNICODE);
        die();
    }

    public function mantenimiento()
    {
        $id_producto = $_POST['id_producto'];
        $talla = $_POST['talla'];
        $color = $_POST['color'];
        $cantidad = $_POST['quantity'];
        $price = $_POST['price'];
        $price_clp = $_POST['price_clp'];
        $demo = $_POST['demo'];
        $consulta = $this->model->getVerificar($talla, $color, $id_producto);
        $producto = $this->model->getProducto($id_producto);
        $datos = $this->model->getTotalStock($id_producto);
        $totalCantidad = ($datos['total'] != null) ? ($datos['total'] + $cantidad)  : $cantidad;
        if ($producto['cantidad'] >= $totalCantidad) {
            if (empty($consulta)) {
                $data = $this->model->registrarMantenimiento($talla, $color, $cantidad, $price, $id_producto, $price_clp, $demo);
                if ($data > 0) {
                    $respuesta = array('msg' => 'ATRIBUTO AGREGADO', 'icono' => 'success');
                } else {
                    $respuesta = array('msg' => 'ERROR AL AGREGAR', 'icono' => 'error');
                }
            } else {
                $data = $this->model->actualizarMantenimiento($talla, $color, $cantidad, $price, $id_producto, $price_clp);
                if ($data == 1) {
                    $respuesta = array('msg' => 'ATRIBUTO MODIFICADO', 'icono' => 'success');
                } else {
                    $respuesta = array('msg' => 'ERROR AL MODIFICAR', 'icono' => 'error');
                }
            }
        } else {
            $respuesta = array('msg' => 'LA SUMA DE LOS ATRIBUTOS SUPERA AL STOCK GENERAL ' . $totalCantidad, 'icono' => 'error');
        }
        echo json_encode($respuesta);
        die();
    }

    public function eliminarDetalle($id)
    {
        if (is_numeric($id)) {
            $data = $this->model->eliminarDetalle($id);
            if ($data == 1) {
                $respuesta = array('msg' => 'detalle eliminado', 'icono' => 'success');
            } else {
                $respuesta = array('msg' => 'error al eliminar', 'icono' => 'error');
            }
        } else {
            $respuesta = array('msg' => 'error desconocido', 'icono' => 'error');
        }
        echo json_encode($respuesta);
        die();
    }
}

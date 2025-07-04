<?php
class ProductosModel extends Query{
 
    public function __construct()
    {
        parent::__construct();
    }
    public function getProductos($estado)
    {
        $sql = "SELECT p.*, c.categoria FROM productos p INNER JOIN categorias c ON p.id_categoria = c.id WHERE 1";
        return $this->selectAll($sql);
    }
    public function getDatos($table)
    {
        $sql = "SELECT * FROM $table WHERE estado = 1";
        return $this->selectAll($sql);
    }

    public function registrar($nombre, $descripcion, $precio, $cantidad, $imagen, $descargable, $categoria, $precio_clp, $precio_costo, $margenDecimal, $costo_impresion)
    {
        $sql = "INSERT INTO productos (nombre, descripcion, precio, cantidad, imagen, descargable, id_categoria, precio_clp, precio_costo, margen, costo_impresion) VALUES (?,?,?,?,?,?,?,?,?,?,?)";
        $array = array($nombre, $descripcion, $precio, $cantidad, $imagen, $descargable, $categoria, $precio_clp, $precio_costo, $margenDecimal, $costo_impresion);
        return $this->insertar($sql, $array);
    }

    public function registrarUrl($ruta, $idPro)
    {
        $sql = "INSERT INTO descargables (ruta, id_producto) VALUES (?,?)";
        $array = array($ruta, $idPro);
        return $this->insertar($sql, $array);
    }

    public function modificarUrl($ruta, $idPro)
    {
        $sql = "UPDATE descargables SET ruta=? WHERE id_producto=?";
        $array = array($ruta, $idPro);
        return $this->save($sql, $array);
    }

    public function eliminar($idPro)
    {
        $sql = "UPDATE productos SET estado = ? WHERE id = ?";
        $array = array(0, $idPro);
        return $this->save($sql, $array);
    }

    public function getProducto($idPro)
    {
        $sql = "SELECT * FROM productos WHERE id = $idPro";
        return $this->select($sql);
    }

    public function getLink($idPro)
    {
        $sql = "SELECT * FROM descargables WHERE id_producto = $idPro";
        return $this->select($sql);
    }

    public function modificar($nombre, $descripcion, $precio, $cantidad, $destino, $descargable, $categoria, $id, $precio_clp)
    {
        $sql = "UPDATE productos SET nombre=?, descripcion=?, precio=?, cantidad=?, imagen=?, descargable=?, id_categoria=?, precio_clp=? WHERE id = ?";
        $array = array($nombre, $descripcion, $precio, $cantidad, $destino, $descargable, $categoria, $id, $precio_clp);
        return $this->save($sql, $array);
    }

    public function getAtributos($id_producto)
    {
        $sql = "SELECT d.id, d.cantidad, t.nombre AS talla, c.nombre, c.color, d.precio_clp FROM tallas_colores d INNER JOIN tallas t ON d.id_talla = t.id INNER JOIN colores c ON d.id_color = c.id WHERE d.id_producto = $id_producto ORDER BY d.id DESC";
        return $this->selectAll($sql);
    }

    public function getTotalStock($id_producto)
    {
        $sql = "SELECT SUM(cantidad) AS total FROM tallas_colores WHERE id_producto = $id_producto";
        return $this->select($sql);
    }

    public function getVerificar($talla, $color, $id_producto)
    {
        $sql = "SELECT * FROM tallas_colores WHERE id_talla = $talla AND id_color = $color AND id_producto = $id_producto";
        return $this->select($sql);
    }

    public function registrarMantenimiento($talla, $color, $cantidad, $price, $id_producto, $precio_clp, $demo)
    {
        $sql = "INSERT INTO tallas_colores (id_talla, id_color, cantidad, precio, id_producto, precio_clp, demo) VALUES (?,?,?,?,?,?,?)";
        $array = array($talla, $color, $cantidad, $price, $id_producto, $precio_clp, $demo);
        return $this->insertar($sql, $array);
    }

    public function actualizarMantenimiento($talla, $color, $cantidad, $price, $id_producto)
    {
        $sql = "UPDATE tallas_colores SET cantidad=?, precio=? WHERE id_talla=? AND id_color=? AND id_producto=?";
        $array = array($cantidad, $price, $talla, $color, $id_producto);
        return $this->save($sql, $array);
    }

    public function eliminarDetalle($id)
    {
        $sql = "DELETE FROM tallas_colores WHERE id = ?";
        $array = array($id);
        return $this->save($sql, $array);
    }
}
 
?>
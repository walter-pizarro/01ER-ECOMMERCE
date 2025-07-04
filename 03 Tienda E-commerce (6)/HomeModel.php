<?php
class HomeModel extends Query{
 
    public function __construct()
    {
        parent::__construct();
    }
    public function getCategorias()
    {
        $sql = "SELECT * FROM categorias";
        return $this->selectAll($sql);
    }
    public function getNuevosProductos()
    {
        $sql = "SELECT * FROM productos ORDER BY id DESC LIMIT 8";
        return $this->selectAll($sql);
    }

    public function getCalificacion($accion, $id)
    {
        $sql = "SELECT $accion(cantidad) AS total FROM calificaciones WHERE id_producto = $id";
        return $this->select($sql);
    }

    public function getTestimonial()
    {
        $sql = "SELECT t.mensaje, cl.nombre, cl.perfil FROM testimonial t INNER JOIN clientes cl ON t.id_cliente = cl.id ORDER BY RAND() LIMIT 12";
        return $this->selectAll($sql);
    }

    public function getSliders()
    {
        $sql = "SELECT * FROM sliders LIMIT 3";
        return $this->selectAll($sql);
    }

    public function getSizeColor($table, $id)
    {
        $sql = "SELECT * FROM $table WHERE id = $id";
        return $this->select($sql);
    }
}
 
?>
import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import axios from 'axios';

const ProductManagement = () => {
  const { user, isAuthenticated } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  
  // Estados para la gestión de productos
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [bulkAction, setBulkAction] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  
  // Verificar autenticación y rol de administrador
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: '/admin/products' } });
    } else if (user && user.role !== 'admin') {
      navigate('/unauthorized');
    }
  }, [isAuthenticated, user, navigate]);
  
  // Cargar productos y categorías
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Obtener productos con paginación y filtros
        const productsResponse = await axios.get('/api/admin/products', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
          params: {
            page: currentPage,
            search: searchTerm,
            category: selectedCategory,
            sort_by: sortBy,
            sort_order: sortOrder
          }
        });
        
        // Obtener categorías para el filtro
        const categoriesResponse = await axios.get('/api/admin/categories', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        
        setProducts(productsResponse.data.products);
        setTotalPages(productsResponse.data.pagination.total_pages);
        setCategories(categoriesResponse.data);
      } catch (err) {
        console.error('Error fetching products data:', err);
        setError('Error al cargar los productos. Por favor, intente nuevamente.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [currentPage, searchTerm, selectedCategory, sortBy, sortOrder]);
  
  // Manejar cambio de página
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };
  
  // Manejar búsqueda
  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1); // Resetear a la primera página al buscar
  };
  
  // Manejar cambio de categoría
  const handleCategoryChange = (e) => {
    setSelectedCategory(e.target.value);
    setCurrentPage(1); // Resetear a la primera página al filtrar
  };
  
  // Manejar cambio de ordenamiento
  const handleSortChange = (e) => {
    const [newSortBy, newSortOrder] = e.target.value.split('-');
    setSortBy(newSortBy);
    setSortOrder(newSortOrder);
    setCurrentPage(1); // Resetear a la primera página al ordenar
  };
  
  // Manejar selección de productos
  const handleSelectProduct = (productId) => {
    setSelectedProducts(prev => {
      if (prev.includes(productId)) {
        return prev.filter(id => id !== productId);
      } else {
        return [...prev, productId];
      }
    });
  };
  
  // Manejar selección de todos los productos
  const handleSelectAllProducts = () => {
    if (selectedProducts.length === products.length) {
      setSelectedProducts([]);
    } else {
      setSelectedProducts(products.map(product => product.id));
    }
  };
  
  // Manejar acción masiva
  const handleBulkAction = async () => {
    if (!bulkAction || selectedProducts.length === 0) return;
    
    try {
      switch (bulkAction) {
        case 'delete':
          setIsDeleting(true);
          await axios.post('/api/admin/products/bulk-delete', 
            { product_ids: selectedProducts },
            { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
          );
          showToast('Productos eliminados correctamente', 'success');
          setSelectedProducts([]);
          // Recargar productos
          setCurrentPage(1);
          break;
          
        case 'feature':
          await axios.post('/api/admin/products/bulk-update', 
            { product_ids: selectedProducts, data: { is_featured: true } },
            { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
          );
          showToast('Productos destacados correctamente', 'success');
          // Actualizar productos en la lista actual
          setProducts(prev => prev.map(product => 
            selectedProducts.includes(product.id) 
              ? { ...product, is_featured: true } 
              : product
          ));
          break;
          
        case 'unfeature':
          await axios.post('/api/admin/products/bulk-update', 
            { product_ids: selectedProducts, data: { is_featured: false } },
            { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
          );
          showToast('Productos desmarcados como destacados correctamente', 'success');
          // Actualizar productos en la lista actual
          setProducts(prev => prev.map(product => 
            selectedProducts.includes(product.id) 
              ? { ...product, is_featured: false } 
              : product
          ));
          break;
          
        default:
          break;
      }
    } catch (err) {
      console.error('Error performing bulk action:', err);
      showToast('Error al realizar la acción masiva', 'error');
    } finally {
      setIsDeleting(false);
      setBulkAction('');
    }
  };
  
  // Manejar eliminación de producto individual
  const handleDeleteProduct = async (productId) => {
    if (!window.confirm('¿Está seguro de que desea eliminar este producto?')) return;
    
    try {
      await axios.delete(`/api/admin/products/${productId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      showToast('Producto eliminado correctamente', 'success');
      // Actualizar lista de productos
      setProducts(prev => prev.filter(product => product.id !== productId));
    } catch (err) {
      console.error('Error deleting product:', err);
      showToast('Error al eliminar el producto', 'error');
    }
  };
  
  // Renderizar paginación
  const renderPagination = () => {
    const pages = [];
    
    // Botón de página anterior
    pages.push(
      <button
        key="prev"
        onClick={() => handlePageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className={`px-3 py-1 rounded-md ${currentPage === 1 
          ? 'bg-gray-200 text-gray-500 cursor-not-allowed' 
          : 'bg-white text-gray-700 hover:bg-gray-50'}`}
      >
        &laquo;
      </button>
    );
    
    // Páginas
    for (let i = 1; i <= totalPages; i++) {
      // Mostrar siempre la primera página, la última página y las páginas cercanas a la actual
      if (
        i === 1 || 
        i === totalPages || 
        (i >= currentPage - 2 && i <= currentPage + 2)
      ) {
        pages.push(
          <button
            key={i}
            onClick={() => handlePageChange(i)}
            className={`px-3 py-1 rounded-md ${currentPage === i 
              ? 'bg-indigo-600 text-white' 
              : 'bg-white text-gray-700 hover:bg-gray-50'}`}
          >
            {i}
          </button>
        );
      } else if (
        (i === currentPage - 3 && currentPage > 4) || 
        (i === currentPage + 3 && currentPage < totalPages - 3)
      ) {
        // Agregar puntos suspensivos para páginas omitidas
        pages.push(
          <span key={`ellipsis-${i}`} className="px-3 py-1">
            &hellip;
          </span>
        );
      }
    }
    
    // Botón de página siguiente
    pages.push(
      <button
        key="next"
        onClick={() => handlePageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className={`px-3 py-1 rounded-md ${currentPage === totalPages 
          ? 'bg-gray-200 text-gray-500 cursor-not-allowed' 
          : 'bg-white text-gray-700 hover:bg-gray-50'}`}
      >
        &raquo;
      </button>
    );
    
    return (
      <div className="flex justify-center mt-6">
        <div className="flex space-x-1">
          {pages}
        </div>
      </div>
    );
  };
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error!</strong>
        <span className="block sm:inline"> {error}</span>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Gestión de Productos</h1>
        <Link 
          to="/admin/products/new" 
          className="bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-md flex items-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
          </svg>
          Nuevo Producto
        </Link>
      </div>
      
      {/* Filtros y búsqueda */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex flex-wrap items-center justify-between">
          <form onSubmit={handleSearch} className="flex mb-4 md:mb-0">
            <input
              type="text"
              placeholder="Buscar productos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="border border-gray-300 rounded-l-md px-4 py-2 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
            <button
              type="submit"
              className="bg-indigo-600 text-white px-4 py-2 rounded-r-md hover:bg-indigo-700"
            >
              Buscar
            </button>
          </form>
          
          <div className="flex flex-wrap">
            <div className="mr-4 mb-2 sm:mb-0">
              <select
                value={selectedCategory}
                onChange={handleCategoryChange}
                className="border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Todas las categorías</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <select
                value={`${sortBy}-${sortOrder}`}
                onChange={handleSortChange}
                className="border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="created_at-desc">Más recientes</option>
                <option value="created_at-asc">Más antiguos</option>
                <option value="name-asc">Nombre (A-Z)</option>
                <option value="name-desc">Nombre (Z-A)</option>
                <option value="price-asc">Precio (menor a mayor)</option>
                <option value="price-desc">Precio (mayor a menor)</option>
                <option value="stock-asc">Stock (menor a mayor)</option>
                <option value="stock-desc">Stock (mayor a menor)</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      
      {/* Acciones masivas */}
      {selectedProducts.length > 0 && (
        <div className="bg-indigo-50 p-4 rounded-lg shadow mb-6 flex items-center justify-between">
          <div>
            <span className="font-medium">{selectedProducts.length} productos seleccionados</span>
          </div>
          <div className="flex items-center">
            <select
              value={bulkAction}
              onChange={(e) => setBulkAction(e.target.value)}
              className="border border-gray-300 rounded-l-md px-4 py-2 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Seleccionar acción</option>
              <option value="delete">Eliminar</option>
              <option value="feature">Marcar como destacado</option>
              <option value="unfeature">Desmarcar como destacado</option>
            </select>
            <button
              onClick={handleBulkAction}
              disabled={!bulkAction || isDeleting}
              className={`px-4 py-2 rounded-r-md ${
                !bulkAction || isDeleting
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700'
              }`}
            >
              {isDeleting ? 'Procesando...' : 'Aplicar'}
            </button>
          </div>
        </div>
      )}
      
      {/* Tabla de productos */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedProducts.length === products.length && products.length > 0}
                    onChange={handleSelectAllProducts}
                    className="rounded text-indigo-600 focus:ring-indigo-500"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Imagen
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nombre
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  SKU
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Precio
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Categoría
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {products.length === 0 ? (
                <tr>
                  <td colSpan="9" className="px-6 py-4 text-center text-gray-500">
                    No se encontraron productos
                  </td>
                </tr>
              ) : (
                products.map(product => (
                  <tr key={product.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="checkbox"
                        checked={selectedProducts.includes(product.id)}
                        onChange={() => handleSelectProduct(product.id)}
                        className="rounded text-indigo-600 focus:ring-indigo-500"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {product.images && product.images.length > 0 ? (
                        <img 
                          src={product.images[0].image_url} 
                          alt={product.name} 
                          className="h-12 w-12 object-cover rounded-md"
                        />
                      ) : (
                        <div className="h-12 w-12 bg-gray-200 rounded-md flex items-center justify-center">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{product.name}</div>
                      {product.is_featured && (
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                          Destacado
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {product.sku}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      ${product.price.toLocaleString()}
                      {product.sale_price && (
                        <div className="text-xs text-red-600 line-through">
                          ${product.sale_price.toLocaleString()}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className={`${
                        product.stock === 0 ? 'text-red-600 font-medium' : 
                        product.stock < 10 ? 'text-yellow-600 font-medium' : 
                        'text-green-600'
                      }`}>
                        {product.stock}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {product.category?.name || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        product.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {product.is_active ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <Link 
                          to={`/admin/products/edit/${product.id}`}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          Editar
                        </Link>
                        <button
                          onClick={() => handleDeleteProduct(product.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Eliminar
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* Paginación */}
      {totalPages > 1 && renderPagination()}
    </div>
  );
};

export default ProductManagement;


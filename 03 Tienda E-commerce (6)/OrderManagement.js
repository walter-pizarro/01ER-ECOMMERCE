import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import axios from 'axios';

const OrderManagement = () => {
  const { user, isAuthenticated } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  
  // Estados para la gestión de pedidos
  const [orders, setOrders] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [dateRange, setDateRange] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [selectedOrders, setSelectedOrders] = useState([]);
  const [bulkAction, setBulkAction] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [viewOrderId, setViewOrderId] = useState(null);
  const [orderDetails, setOrderDetails] = useState(null);
  
  // Verificar autenticación y rol de administrador
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: '/admin/orders' } });
    } else if (user && user.role !== 'admin') {
      navigate('/unauthorized');
    }
  }, [isAuthenticated, user, navigate]);
  
  // Cargar pedidos
  useEffect(() => {
    const fetchOrders = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Obtener pedidos con paginación y filtros
        const response = await axios.get('/api/admin/orders', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
          params: {
            page: currentPage,
            search: searchTerm,
            status: statusFilter,
            date_range: dateRange,
            sort_by: sortBy,
            sort_order: sortOrder
          }
        });
        
        setOrders(response.data.orders);
        setTotalPages(response.data.pagination.total_pages);
      } catch (err) {
        console.error('Error fetching orders:', err);
        setError('Error al cargar los pedidos. Por favor, intente nuevamente.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchOrders();
  }, [currentPage, searchTerm, statusFilter, dateRange, sortBy, sortOrder]);
  
  // Cargar detalles de un pedido específico
  useEffect(() => {
    const fetchOrderDetails = async () => {
      if (!viewOrderId) return;
      
      try {
        const response = await axios.get(`/api/admin/orders/${viewOrderId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        
        setOrderDetails(response.data);
      } catch (err) {
        console.error('Error fetching order details:', err);
        showToast('Error al cargar los detalles del pedido', 'error');
      }
    };
    
    fetchOrderDetails();
  }, [viewOrderId, showToast]);
  
  // Manejar cambio de página
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };
  
  // Manejar búsqueda
  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1); // Resetear a la primera página al buscar
  };
  
  // Manejar cambio de filtro de estado
  const handleStatusChange = (e) => {
    setStatusFilter(e.target.value);
    setCurrentPage(1); // Resetear a la primera página al filtrar
  };
  
  // Manejar cambio de rango de fechas
  const handleDateRangeChange = (e) => {
    setDateRange(e.target.value);
    setCurrentPage(1); // Resetear a la primera página al filtrar
  };
  
  // Manejar cambio de ordenamiento
  const handleSortChange = (e) => {
    const [newSortBy, newSortOrder] = e.target.value.split('-');
    setSortBy(newSortBy);
    setSortOrder(newSortOrder);
    setCurrentPage(1); // Resetear a la primera página al ordenar
  };
  
  // Manejar selección de pedidos
  const handleSelectOrder = (orderId) => {
    setSelectedOrders(prev => {
      if (prev.includes(orderId)) {
        return prev.filter(id => id !== orderId);
      } else {
        return [...prev, orderId];
      }
    });
  };
  
  // Manejar selección de todos los pedidos
  const handleSelectAllOrders = () => {
    if (selectedOrders.length === orders.length) {
      setSelectedOrders([]);
    } else {
      setSelectedOrders(orders.map(order => order.id));
    }
  };
  
  // Manejar acción masiva
  const handleBulkAction = async () => {
    if (!bulkAction || selectedOrders.length === 0) return;
    
    try {
      setIsProcessing(true);
      
      switch (bulkAction) {
        case 'mark-processing':
          await axios.post('/api/admin/orders/bulk-update', 
            { order_ids: selectedOrders, status: 'processing' },
            { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
          );
          showToast('Pedidos actualizados a "En Proceso"', 'success');
          break;
          
        case 'mark-completed':
          await axios.post('/api/admin/orders/bulk-update', 
            { order_ids: selectedOrders, status: 'completed' },
            { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
          );
          showToast('Pedidos actualizados a "Completados"', 'success');
          break;
          
        case 'mark-cancelled':
          await axios.post('/api/admin/orders/bulk-update', 
            { order_ids: selectedOrders, status: 'cancelled' },
            { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
          );
          showToast('Pedidos actualizados a "Cancelados"', 'success');
          break;
          
        case 'export-csv':
          const response = await axios.post('/api/admin/orders/export', 
            { order_ids: selectedOrders, format: 'csv' },
            { 
              headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
              responseType: 'blob'
            }
          );
          
          // Crear un enlace para descargar el archivo
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', `orders-export-${new Date().toISOString().slice(0, 10)}.csv`);
          document.body.appendChild(link);
          link.click();
          link.remove();
          
          showToast('Pedidos exportados correctamente', 'success');
          break;
          
        default:
          break;
      }
      
      // Recargar pedidos después de la acción masiva
      setCurrentPage(1);
      setSelectedOrders([]);
    } catch (err) {
      console.error('Error performing bulk action:', err);
      showToast('Error al realizar la acción masiva', 'error');
    } finally {
      setIsProcessing(false);
      setBulkAction('');
    }
  };
  
  // Manejar actualización de estado de pedido individual
  const handleUpdateOrderStatus = async (orderId, newStatus) => {
    try {
      await axios.put(`/api/admin/orders/${orderId}/status`, 
        { status: newStatus },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      
      showToast(`Pedido #${orderId} actualizado correctamente`, 'success');
      
      // Actualizar el estado del pedido en la lista
      setOrders(prev => prev.map(order => 
        order.id === orderId ? { ...order, status: newStatus } : order
      ));
      
      // Si estamos viendo los detalles de este pedido, actualizar también
      if (viewOrderId === orderId) {
        setOrderDetails(prev => prev ? { ...prev, status: newStatus } : null);
      }
    } catch (err) {
      console.error('Error updating order status:', err);
      showToast('Error al actualizar el estado del pedido', 'error');
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
  
  // Renderizar modal de detalles de pedido
  const renderOrderDetailsModal = () => {
    if (!viewOrderId || !orderDetails) return null;
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Pedido #{orderDetails.id}</h2>
              <button 
                onClick={() => setViewOrderId(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <h3 className="text-lg font-semibold mb-2">Información del Cliente</h3>
                <p><span className="font-medium">Nombre:</span> {orderDetails.customer.name}</p>
                <p><span className="font-medium">Email:</span> {orderDetails.customer.email}</p>
                <p><span className="font-medium">Teléfono:</span> {orderDetails.customer.phone || 'No especificado'}</p>
                <p><span className="font-medium">Cliente desde:</span> {new Date(orderDetails.customer.created_at).toLocaleDateString()}</p>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold mb-2">Información del Pedido</h3>
                <p>
                  <span className="font-medium">Estado:</span>
                  <span className={`ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    orderDetails.status === 'completed' ? 'bg-green-100 text-green-800' : 
                    orderDetails.status === 'processing' ? 'bg-blue-100 text-blue-800' : 
                    orderDetails.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 
                    'bg-red-100 text-red-800'
                  }`}>
                    {orderDetails.status === 'completed' ? 'Completado' : 
                     orderDetails.status === 'processing' ? 'En Proceso' : 
                     orderDetails.status === 'pending' ? 'Pendiente' : 
                     'Cancelado'}
                  </span>
                </p>
                <p><span className="font-medium">Fecha:</span> {new Date(orderDetails.created_at).toLocaleString()}</p>
                <p><span className="font-medium">Método de Pago:</span> {orderDetails.payment_method}</p>
                <p><span className="font-medium">Método de Envío:</span> {orderDetails.shipping_method}</p>
              </div>
            </div>
            
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2">Dirección de Envío</h3>
              <p>{orderDetails.shipping_address.street}</p>
              <p>{orderDetails.shipping_address.city}, {orderDetails.shipping_address.state} {orderDetails.shipping_address.postal_code}</p>
              <p>{orderDetails.shipping_address.country}</p>
            </div>
            
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2">Productos</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Producto</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Precio</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cantidad</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subtotal</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {orderDetails.items.map(item => (
                      <tr key={item.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            {item.product_image && (
                              <img 
                                src={item.product_image} 
                                alt={item.product_name} 
                                className="h-10 w-10 rounded-full mr-3 object-cover"
                              />
                            )}
                            <div>
                              <div className="text-sm font-medium text-gray-900">{item.product_name}</div>
                              {item.variant && (
                                <div className="text-xs text-gray-500">{item.variant}</div>
                              )}
                              {item.sku && (
                                <div className="text-xs text-gray-500">SKU: {item.sku}</div>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          ${item.price.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {item.quantity}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          ${(item.price * item.quantity).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            
            <div className="mb-6 flex justify-end">
              <div className="w-64">
                <div className="flex justify-between py-2 border-b">
                  <span className="font-medium">Subtotal:</span>
                  <span>${orderDetails.subtotal.toLocaleString()}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="font-medium">Envío:</span>
                  <span>${orderDetails.shipping_cost.toLocaleString()}</span>
                </div>
                {orderDetails.discount > 0 && (
                  <div className="flex justify-between py-2 border-b text-green-600">
                    <span className="font-medium">Descuento:</span>
                    <span>-${orderDetails.discount.toLocaleString()}</span>
                  </div>
                )}
                {orderDetails.tax > 0 && (
                  <div className="flex justify-between py-2 border-b">
                    <span className="font-medium">Impuestos:</span>
                    <span>${orderDetails.tax.toLocaleString()}</span>
                  </div>
                )}
                <div className="flex justify-between py-2 font-bold text-lg">
                  <span>Total:</span>
                  <span>${orderDetails.total.toLocaleString()}</span>
                </div>
              </div>
            </div>
            
            {orderDetails.notes && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2">Notas</h3>
                <p className="text-gray-700">{orderDetails.notes}</p>
              </div>
            )}
            
            <div className="border-t pt-6 flex justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-2">Cambiar Estado</h3>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleUpdateOrderStatus(orderDetails.id, 'pending')}
                    disabled={orderDetails.status === 'pending'}
                    className={`px-3 py-1 rounded-md ${
                      orderDetails.status === 'pending'
                        ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                        : 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
                    }`}
                  >
                    Pendiente
                  </button>
                  <button
                    onClick={() => handleUpdateOrderStatus(orderDetails.id, 'processing')}
                    disabled={orderDetails.status === 'processing'}
                    className={`px-3 py-1 rounded-md ${
                      orderDetails.status === 'processing'
                        ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                        : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
                    }`}
                  >
                    En Proceso
                  </button>
                  <button
                    onClick={() => handleUpdateOrderStatus(orderDetails.id, 'completed')}
                    disabled={orderDetails.status === 'completed'}
                    className={`px-3 py-1 rounded-md ${
                      orderDetails.status === 'completed'
                        ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                        : 'bg-green-100 text-green-800 hover:bg-green-200'
                    }`}
                  >
                    Completado
                  </button>
                  <button
                    onClick={() => handleUpdateOrderStatus(orderDetails.id, 'cancelled')}
                    disabled={orderDetails.status === 'cancelled'}
                    className={`px-3 py-1 rounded-md ${
                      orderDetails.status === 'cancelled'
                        ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                        : 'bg-red-100 text-red-800 hover:bg-red-200'
                    }`}
                  >
                    Cancelado
                  </button>
                </div>
              </div>
              <div>
                <button
                  onClick={() => setViewOrderId(null)}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 px-4 rounded-md"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
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
        <h1 className="text-3xl font-bold">Gestión de Pedidos</h1>
      </div>
      
      {/* Filtros y búsqueda */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex flex-wrap items-center justify-between">
          <form onSubmit={handleSearch} className="flex mb-4 md:mb-0">
            <input
              type="text"
              placeholder="Buscar por ID o cliente..."
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
                value={statusFilter}
                onChange={handleStatusChange}
                className="border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Todos los estados</option>
                <option value="pending">Pendiente</option>
                <option value="processing">En Proceso</option>
                <option value="completed">Completado</option>
                <option value="cancelled">Cancelado</option>
              </select>
            </div>
            
            <div className="mr-4 mb-2 sm:mb-0">
              <select
                value={dateRange}
                onChange={handleDateRangeChange}
                className="border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="all">Todas las fechas</option>
                <option value="today">Hoy</option>
                <option value="yesterday">Ayer</option>
                <option value="last7days">Últimos 7 días</option>
                <option value="last30days">Últimos 30 días</option>
                <option value="thismonth">Este mes</option>
                <option value="lastmonth">Mes pasado</option>
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
                <option value="total-desc">Mayor importe</option>
                <option value="total-asc">Menor importe</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      
      {/* Acciones masivas */}
      {selectedOrders.length > 0 && (
        <div className="bg-indigo-50 p-4 rounded-lg shadow mb-6 flex items-center justify-between">
          <div>
            <span className="font-medium">{selectedOrders.length} pedidos seleccionados</span>
          </div>
          <div className="flex items-center">
            <select
              value={bulkAction}
              onChange={(e) => setBulkAction(e.target.value)}
              className="border border-gray-300 rounded-l-md px-4 py-2 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Seleccionar acción</option>
              <option value="mark-processing">Marcar como En Proceso</option>
              <option value="mark-completed">Marcar como Completados</option>
              <option value="mark-cancelled">Marcar como Cancelados</option>
              <option value="export-csv">Exportar a CSV</option>
            </select>
            <button
              onClick={handleBulkAction}
              disabled={!bulkAction || isProcessing}
              className={`px-4 py-2 rounded-r-md ${
                !bulkAction || isProcessing
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700'
              }`}
            >
              {isProcessing ? 'Procesando...' : 'Aplicar'}
            </button>
          </div>
        </div>
      )}
      
      {/* Tabla de pedidos */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedOrders.length === orders.length && orders.length > 0}
                    onChange={handleSelectAllOrders}
                    className="rounded text-indigo-600 focus:ring-indigo-500"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fecha
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total
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
              {orders.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-4 text-center text-gray-500">
                    No se encontraron pedidos
                  </td>
                </tr>
              ) : (
                orders.map(order => (
                  <tr key={order.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="checkbox"
                        checked={selectedOrders.includes(order.id)}
                        onChange={() => handleSelectOrder(order.id)}
                        className="rounded text-indigo-600 focus:ring-indigo-500"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      #{order.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {order.customer_name}
                      <div className="text-xs">{order.customer_email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(order.created_at).toLocaleDateString()}
                      <div className="text-xs">{new Date(order.created_at).toLocaleTimeString()}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      ${order.total.toLocaleString()}
                      <div className="text-xs">{order.items_count} productos</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        order.status === 'completed' ? 'bg-green-100 text-green-800' : 
                        order.status === 'processing' ? 'bg-blue-100 text-blue-800' : 
                        order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 
                        'bg-red-100 text-red-800'
                      }`}>
                        {order.status === 'completed' ? 'Completado' : 
                         order.status === 'processing' ? 'En Proceso' : 
                         order.status === 'pending' ? 'Pendiente' : 
                         'Cancelado'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => setViewOrderId(order.id)}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          Ver
                        </button>
                        <div className="relative group">
                          <button className="text-gray-600 hover:text-gray-900">
                            Estado
                          </button>
                          <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg hidden group-hover:block z-10">
                            <div className="py-1">
                              <button
                                onClick={() => handleUpdateOrderStatus(order.id, 'pending')}
                                disabled={order.status === 'pending'}
                                className={`block px-4 py-2 text-sm text-left w-full ${
                                  order.status === 'pending'
                                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                    : 'text-gray-700 hover:bg-gray-100'
                                }`}
                              >
                                Pendiente
                              </button>
                              <button
                                onClick={() => handleUpdateOrderStatus(order.id, 'processing')}
                                disabled={order.status === 'processing'}
                                className={`block px-4 py-2 text-sm text-left w-full ${
                                  order.status === 'processing'
                                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                    : 'text-gray-700 hover:bg-gray-100'
                                }`}
                              >
                                En Proceso
                              </button>
                              <button
                                onClick={() => handleUpdateOrderStatus(order.id, 'completed')}
                                disabled={order.status === 'completed'}
                                className={`block px-4 py-2 text-sm text-left w-full ${
                                  order.status === 'completed'
                                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                    : 'text-gray-700 hover:bg-gray-100'
                                }`}
                              >
                                Completado
                              </button>
                              <button
                                onClick={() => handleUpdateOrderStatus(order.id, 'cancelled')}
                                disabled={order.status === 'cancelled'}
                                className={`block px-4 py-2 text-sm text-left w-full ${
                                  order.status === 'cancelled'
                                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                    : 'text-gray-700 hover:bg-gray-100'
                                }`}
                              >
                                Cancelado
                              </button>
                            </div>
                          </div>
                        </div>
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
      
      {/* Modal de detalles de pedido */}
      {renderOrderDetailsModal()}
    </div>
  );
};

export default OrderManagement;


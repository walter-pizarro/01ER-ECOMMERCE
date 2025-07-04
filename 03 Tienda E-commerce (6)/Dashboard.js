import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Bar, Line, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import axios from 'axios';

// Registrar componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  
  // Estados para datos del dashboard
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    salesSummary: {},
    recentOrders: [],
    topProducts: [],
    customerStats: {},
    inventoryAlerts: []
  });
  
  // Estados para filtros
  const [dateRange, setDateRange] = useState('week'); // 'day', 'week', 'month', 'year'
  
  // Verificar autenticación y rol de administrador
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: '/admin/dashboard' } });
    } else if (user && user.role !== 'admin') {
      navigate('/unauthorized');
    }
  }, [isAuthenticated, user, navigate]);
  
  // Cargar datos del dashboard
  useEffect(() => {
    const fetchDashboardData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Obtener resumen de ventas
        const salesResponse = await axios.get(`/api/admin/stats/sales?range=${dateRange}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        
        // Obtener pedidos recientes
        const ordersResponse = await axios.get('/api/admin/orders/recent', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        
        // Obtener productos más vendidos
        const productsResponse = await axios.get('/api/admin/products/top', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        
        // Obtener estadísticas de clientes
        const customersResponse = await axios.get('/api/admin/customers/stats', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        
        // Obtener alertas de inventario
        const inventoryResponse = await axios.get('/api/admin/inventory/alerts', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        
        setStats({
          salesSummary: salesResponse.data,
          recentOrders: ordersResponse.data,
          topProducts: productsResponse.data,
          customerStats: customersResponse.data,
          inventoryAlerts: inventoryResponse.data
        });
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Error al cargar los datos del dashboard. Por favor, intente nuevamente.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchDashboardData();
  }, [dateRange]);
  
  // Datos para gráfico de ventas
  const salesChartData = {
    labels: stats.salesSummary.labels || [],
    datasets: [
      {
        label: 'Ventas',
        data: stats.salesSummary.sales || [],
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      },
      {
        label: 'Pedidos',
        data: stats.salesSummary.orders || [],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
    ],
  };
  
  // Datos para gráfico de productos más vendidos
  const topProductsChartData = {
    labels: stats.topProducts.map(product => product.name) || [],
    datasets: [
      {
        label: 'Unidades vendidas',
        data: stats.topProducts.map(product => product.quantity) || [],
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
        ],
        borderWidth: 1,
      },
    ],
  };
  
  // Datos para gráfico de clientes
  const customerChartData = {
    labels: ['Nuevos', 'Recurrentes'],
    datasets: [
      {
        label: 'Clientes',
        data: [
          stats.customerStats.newCustomers || 0,
          stats.customerStats.returningCustomers || 0
        ],
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
        ],
        borderWidth: 1,
      },
    ],
  };
  
  // Opciones para gráficos
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Resumen de Ventas',
      },
    },
  };
  
  // Manejador de cambio de rango de fechas
  const handleDateRangeChange = (e) => {
    setDateRange(e.target.value);
  };
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"></div>
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
      <h1 className="text-3xl font-bold mb-6">Panel de Administración</h1>
      
      {/* Filtros */}
      <div className="mb-6 bg-white p-4 rounded-lg shadow">
        <div className="flex flex-wrap items-center">
          <div className="mr-4 mb-2">
            <label htmlFor="dateRange" className="block text-sm font-medium text-gray-700">Rango de fechas:</label>
            <select
              id="dateRange"
              value={dateRange}
              onChange={handleDateRangeChange}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="day">Hoy</option>
              <option value="week">Esta semana</option>
              <option value="month">Este mes</option>
              <option value="year">Este año</option>
            </select>
          </div>
        </div>
      </div>
      
      {/* Tarjetas de resumen */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700">Ventas Totales</h3>
          <p className="text-3xl font-bold text-green-600">${stats.salesSummary.totalSales?.toLocaleString() || '0'}</p>
          <p className="text-sm text-gray-500">
            {stats.salesSummary.salesGrowth > 0 ? '+' : ''}{stats.salesSummary.salesGrowth || '0'}% vs. período anterior
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700">Pedidos</h3>
          <p className="text-3xl font-bold text-blue-600">{stats.salesSummary.totalOrders?.toLocaleString() || '0'}</p>
          <p className="text-sm text-gray-500">
            {stats.salesSummary.ordersGrowth > 0 ? '+' : ''}{stats.salesSummary.ordersGrowth || '0'}% vs. período anterior
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700">Clientes Nuevos</h3>
          <p className="text-3xl font-bold text-purple-600">{stats.customerStats.newCustomers?.toLocaleString() || '0'}</p>
          <p className="text-sm text-gray-500">
            {stats.customerStats.customerGrowth > 0 ? '+' : ''}{stats.customerStats.customerGrowth || '0'}% vs. período anterior
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700">Ticket Promedio</h3>
          <p className="text-3xl font-bold text-amber-600">${stats.salesSummary.averageOrderValue?.toLocaleString() || '0'}</p>
          <p className="text-sm text-gray-500">
            {stats.salesSummary.aovGrowth > 0 ? '+' : ''}{stats.salesSummary.aovGrowth || '0'}% vs. período anterior
          </p>
        </div>
      </div>
      
      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Tendencia de Ventas</h3>
          <div className="h-80">
            <Line data={salesChartData} options={chartOptions} />
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Productos Más Vendidos</h3>
          <div className="h-80">
            <Bar 
              data={topProductsChartData} 
              options={{
                ...chartOptions,
                plugins: {
                  ...chartOptions.plugins,
                  title: {
                    ...chartOptions.plugins.title,
                    text: 'Top 5 Productos'
                  }
                }
              }} 
            />
          </div>
        </div>
      </div>
      
      {/* Pedidos recientes y alertas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Pedidos Recientes</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cliente</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {stats.recentOrders.map((order) => (
                  <tr key={order.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{order.id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{order.customer_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${order.total.toLocaleString()}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${order.status === 'completed' ? 'bg-green-100 text-green-800' : 
                          order.status === 'processing' ? 'bg-blue-100 text-blue-800' : 
                          order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 
                          'bg-red-100 text-red-800'}`}>
                        {order.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 text-right">
            <a href="/admin/orders" className="text-indigo-600 hover:text-indigo-900">Ver todos los pedidos →</a>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Alertas de Inventario</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Producto</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SKU</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {stats.inventoryAlerts.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.sku}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.stock}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${item.stock === 0 ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                        {item.stock === 0 ? 'Agotado' : 'Stock bajo'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 text-right">
            <a href="/admin/inventory" className="text-indigo-600 hover:text-indigo-900">Gestionar inventario →</a>
          </div>
        </div>
      </div>
      
      {/* Distribución de clientes */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow lg:col-span-1">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Distribución de Clientes</h3>
          <div className="h-64">
            <Pie 
              data={customerChartData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom',
                  }
                }
              }} 
            />
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow lg:col-span-2">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Acciones Rápidas</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a href="/admin/products/new" className="bg-indigo-600 hover:bg-indigo-700 text-white p-4 rounded-lg text-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              <span>Nuevo Producto</span>
            </a>
            <a href="/admin/orders" className="bg-green-600 hover:bg-green-700 text-white p-4 rounded-lg text-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              </svg>
              <span>Gestionar Pedidos</span>
            </a>
            <a href="/admin/reports" className="bg-amber-600 hover:bg-amber-700 text-white p-4 rounded-lg text-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <span>Ver Reportes</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;


import React, { useState, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts';
import { 
  TrendingUp, 
  Users, 
  Package, 
  ShoppingCart, 
  DollarSign,
  Eye,
  Calendar,
  Activity
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import apiService from '../../lib/api';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    total_sales: 0,
    total_orders: 0,
    total_customers: 0,
    total_products: 0,
    sales_growth: 0,
    orders_growth: 0,
  });
  const [salesData, setSalesData] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [recentOrders, setRecentOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load stats
      const statsResponse = await apiService.getStats().catch(() => ({
        total_sales: 125000,
        total_orders: 45,
        total_customers: 23,
        total_products: 4,
        sales_growth: 12.5,
        orders_growth: 8.3,
      }));
      
      setStats(statsResponse);

      // Mock sales data for chart
      setSalesData([
        { name: 'Ene', ventas: 12000, pedidos: 8 },
        { name: 'Feb', ventas: 19000, pedidos: 12 },
        { name: 'Mar', ventas: 15000, pedidos: 10 },
        { name: 'Abr', ventas: 25000, pedidos: 15 },
        { name: 'May', ventas: 22000, pedidos: 14 },
        { name: 'Jun', ventas: 32000, pedidos: 18 },
      ]);

      // Mock category data
      setCategoryData([
        { name: 'Smartphones', value: 45, color: '#8884d8' },
        { name: 'Laptops', value: 30, color: '#82ca9d' },
        { name: 'Ropa', value: 15, color: '#ffc658' },
        { name: 'Otros', value: 10, color: '#ff7300' },
      ]);

      // Mock recent orders
      setRecentOrders([
        { id: 1, customer: 'Juan Pérez', total: 45000, status: 'Completado', date: '2024-01-15' },
        { id: 2, customer: 'María García', total: 32000, status: 'Procesando', date: '2024-01-14' },
        { id: 3, customer: 'Carlos López', total: 28000, status: 'Enviado', date: '2024-01-13' },
      ]);

    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const StatCard = ({ title, value, icon: Icon, growth, color = 'blue' }) => (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            {growth !== undefined && (
              <p className={`text-sm ${growth >= 0 ? 'text-green-600' : 'text-red-600'} flex items-center mt-1`}>
                <TrendingUp className="h-4 w-4 mr-1" />
                {growth >= 0 ? '+' : ''}{growth}%
              </p>
            )}
          </div>
          <div className={`p-3 bg-${color}-100 rounded-full`}>
            <Icon className={`h-6 w-6 text-${color}-600`} />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Panel Administrativo</h1>
          <p className="text-gray-600">Resumen general de tu tienda online</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Ventas Totales"
            value={formatPrice(stats.total_sales)}
            icon={DollarSign}
            growth={stats.sales_growth}
            color="green"
          />
          <StatCard
            title="Pedidos"
            value={stats.total_orders}
            icon={ShoppingCart}
            growth={stats.orders_growth}
            color="blue"
          />
          <StatCard
            title="Clientes"
            value={stats.total_customers}
            icon={Users}
            color="purple"
          />
          <StatCard
            title="Productos"
            value={stats.total_products}
            icon={Package}
            color="orange"
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Sales Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart className="h-5 w-5 mr-2" />
                Ventas por Mes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={salesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value, name) => [
                      name === 'ventas' ? formatPrice(value) : value,
                      name === 'ventas' ? 'Ventas' : 'Pedidos'
                    ]}
                  />
                  <Bar dataKey="ventas" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Category Distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <PieChart className="h-5 w-5 mr-2" />
                Ventas por Categoría
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Recent Orders and Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Orders */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center">
                  <Activity className="h-5 w-5 mr-2" />
                  Pedidos Recientes
                </span>
                <Button variant="outline" size="sm">
                  Ver Todos
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentOrders.map((order) => (
                  <div key={order.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">#{order.id} - {order.customer}</p>
                      <p className="text-sm text-gray-600">{order.date}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">{formatPrice(order.total)}</p>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        order.status === 'Completado' ? 'bg-green-100 text-green-800' :
                        order.status === 'Procesando' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {order.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Acciones Rápidas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full justify-start" variant="outline">
                <Package className="h-4 w-4 mr-2" />
                Agregar Producto
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <Users className="h-4 w-4 mr-2" />
                Ver Clientes
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <ShoppingCart className="h-4 w-4 mr-2" />
                Gestionar Pedidos
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <Eye className="h-4 w-4 mr-2" />
                Ver Reportes
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <Calendar className="h-4 w-4 mr-2" />
                Programar Promoción
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Performance Metrics */}
        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="h-5 w-5 mr-2" />
                Métricas de Rendimiento
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">98.5%</p>
                  <p className="text-sm text-gray-600">Tiempo de Actividad</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">1.2s</p>
                  <p className="text-sm text-gray-600">Tiempo de Carga</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-600">4.8/5</p>
                  <p className="text-sm text-gray-600">Satisfacción Cliente</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;


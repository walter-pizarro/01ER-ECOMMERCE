import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Star, ShoppingCart, TrendingUp, Users, Package } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import apiService from '../lib/api';
import { useCart } from '../contexts/CartContext';
import { useToast } from '../contexts/ToastContext';

const Home = () => {
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const { addToCart } = useCart();
  const { showSuccess, showError } = useToast();

  useEffect(() => {
    loadHomeData();
  }, []);

  const loadHomeData = async () => {
    try {
      setLoading(true);
      
      // Load featured products and stats in parallel
      const [productsResponse, statsResponse] = await Promise.all([
        apiService.getProducts({ limit: 4 }),
        apiService.getStats().catch(() => ({ total_products: 4, total_customers: 3, total_orders: 1 }))
      ]);
      
      setFeaturedProducts(productsResponse.products || []);
      setStats(statsResponse);
    } catch (error) {
      console.error('Error loading home data:', error);
      showError('Error cargando datos de la página');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async (product) => {
    try {
      await addToCart(product);
      showSuccess(`${product.name} agregado al carrito`);
    } catch (error) {
      showError('Error agregando producto al carrito');
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
    }).format(price);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Bienvenido a eCommerce Moderno
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-blue-100">
              Descubre productos increíbles con la mejor experiencia de compra
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/products">
                <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100">
                  Explorar Productos
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600">
                Ver Ofertas
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card>
              <CardContent className="flex items-center p-6">
                <div className="p-3 bg-blue-100 rounded-full mr-4">
                  <Package className="h-8 w-8 text-blue-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_products || 0}</p>
                  <p className="text-gray-600">Productos Disponibles</p>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="flex items-center p-6">
                <div className="p-3 bg-green-100 rounded-full mr-4">
                  <Users className="h-8 w-8 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_customers || 0}</p>
                  <p className="text-gray-600">Clientes Satisfechos</p>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="flex items-center p-6">
                <div className="p-3 bg-purple-100 rounded-full mr-4">
                  <TrendingUp className="h-8 w-8 text-purple-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_orders || 0}</p>
                  <p className="text-gray-600">Órdenes Completadas</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Productos Destacados</h2>
            <p className="text-lg text-gray-600">Descubre nuestros productos más populares</p>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuredProducts.map((product) => (
              <Card key={product.id} className="group hover:shadow-lg transition-shadow">
                <CardContent className="p-0">
                  <div className="aspect-square bg-gray-200 rounded-t-lg flex items-center justify-center">
                    <Package className="h-16 w-16 text-gray-400" />
                  </div>
                  <div className="p-4">
                    <h3 className="font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                      {product.name}
                    </h3>
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                      {product.description}
                    </p>
                    
                    {/* Rating */}
                    <div className="flex items-center mb-3">
                      <div className="flex text-yellow-400">
                        {Array(5).fill().map((_, i) => (
                          <Star 
                            key={i} 
                            className={`h-4 w-4 ${i < Math.floor(product.rating) ? 'fill-current' : ''}`} 
                          />
                        ))}
                      </div>
                      <span className="text-sm text-gray-500 ml-2">
                        ({product.review_count || 0})
                      </span>
                    </div>
                    
                    {/* Price */}
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        {product.sale_price && product.sale_price !== product.price ? (
                          <>
                            <span className="text-lg font-bold text-green-600">
                              {formatPrice(product.sale_price)}
                            </span>
                            <span className="text-sm text-gray-500 line-through ml-2">
                              {formatPrice(product.price)}
                            </span>
                          </>
                        ) : (
                          <span className="text-lg font-bold text-gray-900">
                            {formatPrice(product.price)}
                          </span>
                        )}
                      </div>
                      <span className="text-sm text-gray-500">
                        {product.stock_quantity} disponibles
                      </span>
                    </div>
                    
                    {/* Actions */}
                    <div className="flex gap-2">
                      <Link to={`/products/${product.id}`} className="flex-1">
                        <Button variant="outline" className="w-full">
                          Ver Detalles
                        </Button>
                      </Link>
                      <Button 
                        onClick={() => handleAddToCart(product)}
                        className="flex-1"
                      >
                        <ShoppingCart className="h-4 w-4 mr-2" />
                        Agregar
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          
          <div className="text-center mt-12">
            <Link to="/products">
              <Button size="lg">
                Ver Todos los Productos
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">¿Por qué elegirnos?</h2>
            <p className="text-lg text-gray-600">Ofrecemos la mejor experiencia de compra online</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <ShoppingCart className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Compra Fácil</h3>
              <p className="text-gray-600">
                Proceso de compra simple y seguro con múltiples métodos de pago
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Package className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Envío Rápido</h3>
              <p className="text-gray-600">
                Entrega rápida y segura en todo el país con tracking en tiempo real
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Star className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Calidad Garantizada</h3>
              <p className="text-gray-600">
                Productos de alta calidad con garantía y soporte post-venta
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;


import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Search, Filter, Grid, List, Star, ShoppingCart, Package } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import apiService from '../lib/api';
import { useCart } from '../contexts/CartContext';
import { useToast } from '../contexts/ToastContext';

const ProductCatalog = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('grid');
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    category: searchParams.get('category') || '',
    sortBy: searchParams.get('sortBy') || 'name',
    minPrice: searchParams.get('minPrice') || '',
    maxPrice: searchParams.get('maxPrice') || '',
  });
  const [pagination, setPagination] = useState({
    page: 1,
    pages: 1,
    total: 0,
    per_page: 12,
  });

  const { addToCart } = useCart();
  const { showSuccess, showError } = useToast();

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    loadProducts();
  }, [filters, pagination.page]);

  useEffect(() => {
    // Update URL params when filters change
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    setSearchParams(params);
  }, [filters, setSearchParams]);

  const loadCategories = async () => {
    try {
      const response = await apiService.getCategories();
      setCategories(response.categories || []);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const loadProducts = async () => {
    try {
      setLoading(true);
      
      const params = {
        page: pagination.page,
        per_page: pagination.per_page,
        ...filters,
      };

      // Remove empty filters
      Object.keys(params).forEach(key => {
        if (!params[key]) delete params[key];
      });

      let response;
      if (filters.search) {
        response = await apiService.searchProducts(filters.search);
      } else {
        response = await apiService.getProducts(params);
      }
      
      setProducts(response.products || []);
      setPagination(prev => ({
        ...prev,
        ...response.pagination,
      }));
    } catch (error) {
      console.error('Error loading products:', error);
      showError('Error cargando productos');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }));
    setPagination(prev => ({ ...prev, page: 1 }));
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

  const ProductCard = ({ product, isListView = false }) => (
    <Card className={`group hover:shadow-lg transition-shadow ${isListView ? 'flex' : ''}`}>
      <CardContent className={`p-0 ${isListView ? 'flex w-full' : ''}`}>
        <div className={`bg-gray-200 flex items-center justify-center ${
          isListView ? 'w-48 h-32' : 'aspect-square'
        } ${isListView ? '' : 'rounded-t-lg'}`}>
          <Package className="h-16 w-16 text-gray-400" />
        </div>
        
        <div className={`p-4 ${isListView ? 'flex-1 flex flex-col justify-between' : ''}`}>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
              {product.name}
            </h3>
            <p className={`text-sm text-gray-600 mb-3 ${isListView ? '' : 'line-clamp-2'}`}>
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
          </div>
          
          <div>
            {/* Price */}
            <div className={`flex items-center ${isListView ? 'justify-between' : 'justify-between'} mb-4`}>
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
            <div className={`flex gap-2 ${isListView ? 'w-48' : ''}`}>
              <Link to={`/products/${product.id}`} className="flex-1">
                <Button variant="outline" className="w-full" size={isListView ? 'sm' : 'default'}>
                  Ver Detalles
                </Button>
              </Link>
              <Button 
                onClick={() => handleAddToCart(product)}
                className="flex-1"
                size={isListView ? 'sm' : 'default'}
              >
                <ShoppingCart className="h-4 w-4 mr-2" />
                Agregar
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Catálogo de Productos</h1>
          
          {/* Search and Filters */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              {/* Search */}
              <div className="relative">
                <Input
                  type="text"
                  placeholder="Buscar productos..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  className="pl-10"
                />
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              </div>
              
              {/* Category Filter */}
              <Select value={filters.category} onValueChange={(value) => handleFilterChange('category', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Todas las categorías" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todas las categorías</SelectItem>
                  {categories.map((category) => (
                    <SelectItem key={category.id} value={category.id.toString()}>
                      {category.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              {/* Sort */}
              <Select value={filters.sortBy} onValueChange={(value) => handleFilterChange('sortBy', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Ordenar por" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="name">Nombre</SelectItem>
                  <SelectItem value="price_asc">Precio: Menor a Mayor</SelectItem>
                  <SelectItem value="price_desc">Precio: Mayor a Menor</SelectItem>
                  <SelectItem value="rating">Mejor Valorados</SelectItem>
                  <SelectItem value="newest">Más Recientes</SelectItem>
                </SelectContent>
              </Select>
              
              {/* View Mode */}
              <div className="flex gap-2">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'outline'}
                  size="icon"
                  onClick={() => setViewMode('grid')}
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'outline'}
                  size="icon"
                  onClick={() => setViewMode('list')}
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>
            </div>
            
            {/* Price Range */}
            <div className="flex gap-4">
              <Input
                type="number"
                placeholder="Precio mínimo"
                value={filters.minPrice}
                onChange={(e) => handleFilterChange('minPrice', e.target.value)}
                className="w-32"
              />
              <Input
                type="number"
                placeholder="Precio máximo"
                value={filters.maxPrice}
                onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
                className="w-32"
              />
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="mb-6">
          <p className="text-gray-600">
            Mostrando {products.length} de {pagination.total} productos
          </p>
        </div>

        {/* Products Grid/List */}
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-16">
            <Package className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No se encontraron productos</h3>
            <p className="text-gray-500">Intenta ajustar los filtros de búsqueda</p>
          </div>
        ) : (
          <div className={
            viewMode === 'grid' 
              ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
              : 'space-y-4'
          }>
            {products.map((product) => (
              <ProductCard 
                key={product.id} 
                product={product} 
                isListView={viewMode === 'list'} 
              />
            ))}
          </div>
        )}

        {/* Pagination */}
        {pagination.pages > 1 && (
          <div className="flex justify-center mt-8">
            <div className="flex gap-2">
              <Button
                variant="outline"
                disabled={pagination.page === 1}
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
              >
                Anterior
              </Button>
              
              {Array.from({ length: pagination.pages }, (_, i) => i + 1).map((page) => (
                <Button
                  key={page}
                  variant={page === pagination.page ? 'default' : 'outline'}
                  onClick={() => setPagination(prev => ({ ...prev, page }))}
                >
                  {page}
                </Button>
              ))}
              
              <Button
                variant="outline"
                disabled={pagination.page === pagination.pages}
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
              >
                Siguiente
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductCatalog;


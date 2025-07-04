import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient } from '../../services/api';
import { useCart } from '../../contexts/CartContext';
import { useToast } from '../../contexts/ToastContext';

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [selectedImage, setSelectedImage] = useState(0);
  const [selectedVariant, setSelectedVariant] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reviewsLoading, setReviewsLoading] = useState(false);
  
  const { addItem, isInCart, getCartItem } = useCart();
  const { success, error } = useToast();

  useEffect(() => {
    if (id) {
      loadProduct();
      loadReviews();
    }
  }, [id]);

  const loadProduct = async () => {
    try {
      const response = await apiClient.get(`/products/${id}`);
      if (response.data.success) {
        setProduct(response.data.product);
        // Set default variant if available
        if (response.data.product.variants?.length > 0) {
          setSelectedVariant(response.data.product.variants[0]);
        }
      } else {
        error('Producto no encontrado');
        navigate('/products');
      }
    } catch (err) {
      console.error('Error loading product:', err);
      error('Error al cargar el producto');
      navigate('/products');
    } finally {
      setLoading(false);
    }
  };

  const loadReviews = async () => {
    setReviewsLoading(true);
    try {
      const response = await apiClient.get(`/products/${id}/reviews`);
      if (response.data.success) {
        setReviews(response.data.reviews || []);
      }
    } catch (err) {
      console.error('Error loading reviews:', err);
    } finally {
      setReviewsLoading(false);
    }
  };

  const handleAddToCart = () => {
    if (!product) return;

    // Check inventory
    const availableStock = selectedVariant ? selectedVariant.inventory_quantity : product.inventory_quantity;
    const cartItem = getCartItem(product.id, selectedVariant);
    const currentCartQuantity = cartItem ? cartItem.quantity : 0;

    if (currentCartQuantity + quantity > availableStock) {
      error(`Solo hay ${availableStock} unidades disponibles`);
      return;
    }

    addItem(product, quantity, selectedVariant);
    success(`${quantity} ${product.name} agregado${quantity > 1 ? 's' : ''} al carrito`);
  };

  const handleBuyNow = () => {
    handleAddToCart();
    navigate('/checkout');
  };

  const getPrice = () => {
    if (selectedVariant && selectedVariant.price) {
      return parseFloat(selectedVariant.price);
    }
    return parseFloat(product?.price || 0);
  };

  const getStock = () => {
    if (selectedVariant) {
      return selectedVariant.inventory_quantity || 0;
    }
    return product?.inventory_quantity || 0;
  };

  const renderStars = (rating) => {
    return [...Array(5)].map((_, i) => (
      <svg
        key={i}
        className={`w-5 h-5 ${i < Math.floor(rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
        viewBox="0 0 20 20"
      >
        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
      </svg>
    ));
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="space-y-4">
              <div className="w-full h-96 bg-gray-300 rounded-lg"></div>
              <div className="grid grid-cols-4 gap-2">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="w-full h-20 bg-gray-300 rounded"></div>
                ))}
              </div>
            </div>
            <div className="space-y-4">
              <div className="h-8 bg-gray-300 rounded w-3/4"></div>
              <div className="h-6 bg-gray-300 rounded w-1/2"></div>
              <div className="h-4 bg-gray-300 rounded w-full"></div>
              <div className="h-4 bg-gray-300 rounded w-full"></div>
              <div className="h-4 bg-gray-300 rounded w-2/3"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900">Producto no encontrado</h1>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <nav className="flex mb-8" aria-label="Breadcrumb">
        <ol className="flex items-center space-x-4">
          <li>
            <button onClick={() => navigate('/')} className="text-gray-400 hover:text-gray-500">
              Inicio
            </button>
          </li>
          <li>
            <svg className="flex-shrink-0 h-5 w-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          </li>
          <li>
            <button onClick={() => navigate('/products')} className="text-gray-400 hover:text-gray-500">
              Productos
            </button>
          </li>
          <li>
            <svg className="flex-shrink-0 h-5 w-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          </li>
          <li>
            <span className="text-gray-500 truncate">{product.name}</span>
          </li>
        </ol>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Product Images */}
        <div className="space-y-4">
          {/* Main Image */}
          <div className="aspect-w-1 aspect-h-1">
            <img
              src={product.images?.[selectedImage]?.image_url || '/api/placeholder/600/600'}
              alt={product.name}
              className="w-full h-96 object-cover rounded-lg"
            />
          </div>
          
          {/* Thumbnail Images */}
          {product.images && product.images.length > 1 && (
            <div className="grid grid-cols-4 gap-2">
              {product.images.map((image, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedImage(index)}
                  className={`aspect-w-1 aspect-h-1 rounded-lg overflow-hidden ${
                    selectedImage === index ? 'ring-2 ring-blue-500' : ''
                  }`}
                >
                  <img
                    src={image.image_url}
                    alt={`${product.name} ${index + 1}`}
                    className="w-full h-20 object-cover hover:opacity-75 transition-opacity"
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{product.name}</h1>
            
            {/* Rating */}
            {product.average_rating && (
              <div className="flex items-center mt-2">
                <div className="flex">
                  {renderStars(product.average_rating)}
                </div>
                <span className="ml-2 text-sm text-gray-600">
                  {product.average_rating.toFixed(1)} ({product.review_count || 0} reseñas)
                </span>
              </div>
            )}
          </div>

          {/* Price */}
          <div className="text-3xl font-bold text-blue-600">
            ${getPrice().toFixed(2)}
          </div>

          {/* Description */}
          <div className="prose prose-sm text-gray-600">
            <p>{product.description}</p>
          </div>

          {/* Variants */}
          {product.variants && product.variants.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Opciones:</h3>
              <div className="grid grid-cols-2 gap-2">
                {product.variants.map((variant) => (
                  <button
                    key={variant.id}
                    onClick={() => setSelectedVariant(variant)}
                    className={`p-3 border rounded-lg text-sm ${
                      selectedVariant?.id === variant.id
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <div className="font-medium">{variant.size} - {variant.color}</div>
                    <div className="text-xs text-gray-500">
                      ${parseFloat(variant.price || product.price).toFixed(2)}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Quantity */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cantidad:
            </label>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-50"
              >
                -
              </button>
              <span className="text-lg font-medium w-8 text-center">{quantity}</span>
              <button
                onClick={() => setQuantity(Math.min(getStock(), quantity + 1))}
                className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-50"
              >
                +
              </button>
            </div>
            <p className="text-sm text-gray-500 mt-1">
              {getStock()} unidades disponibles
            </p>
          </div>

          {/* Add to Cart Buttons */}
          <div className="space-y-3">
            <button
              onClick={handleAddToCart}
              disabled={getStock() === 0}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {getStock() === 0 ? 'Sin Stock' : 'Agregar al Carrito'}
            </button>
            
            <button
              onClick={handleBuyNow}
              disabled={getStock() === 0}
              className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              Comprar Ahora
            </button>
          </div>

          {/* Product Details */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Detalles del Producto</h3>
            <dl className="space-y-2">
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">SKU:</dt>
                <dd className="text-sm font-medium text-gray-900">{product.sku}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Categoría:</dt>
                <dd className="text-sm font-medium text-gray-900">{product.category?.name}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-600">Peso:</dt>
                <dd className="text-sm font-medium text-gray-900">{product.weight || 'N/A'}</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      {/* Reviews Section */}
      <div className="mt-16 border-t pt-16">
        <h2 className="text-2xl font-bold text-gray-900 mb-8">Reseñas de Clientes</h2>
        
        {reviewsLoading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="animate-pulse border rounded-lg p-6">
                <div className="flex items-center space-x-4 mb-4">
                  <div className="w-10 h-10 bg-gray-300 rounded-full"></div>
                  <div className="space-y-2">
                    <div className="h-4 bg-gray-300 rounded w-24"></div>
                    <div className="h-3 bg-gray-300 rounded w-16"></div>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-300 rounded w-full"></div>
                  <div className="h-4 bg-gray-300 rounded w-3/4"></div>
                </div>
              </div>
            ))}
          </div>
        ) : reviews.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">No hay reseñas aún. ¡Sé el primero en dejar una reseña!</p>
          </div>
        ) : (
          <div className="space-y-6">
            {reviews.map((review) => (
              <div key={review.id} className="border rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-medium">
                        {review.user?.first_name?.charAt(0) || 'U'}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">
                        {review.user?.first_name || 'Usuario'} {review.user?.last_name || ''}
                      </p>
                      <div className="flex items-center">
                        {renderStars(review.rating)}
                      </div>
                    </div>
                  </div>
                  <span className="text-sm text-gray-500">
                    {new Date(review.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-gray-700">{review.comment}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductDetail;


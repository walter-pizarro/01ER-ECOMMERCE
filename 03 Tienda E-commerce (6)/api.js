/**
 * Configuración y cliente API para comunicación con el backend
 * Maneja autenticación, interceptores y manejo de errores
 */

// Configuración base de la API
const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
};

/**
 * Cliente HTTP personalizado con interceptores
 */
class ApiClient {
  constructor() {
    this.baseURL = API_CONFIG.baseURL;
    this.timeout = API_CONFIG.timeout;
    this.defaultHeaders = API_CONFIG.headers;
  }

  /**
   * Realiza una petición HTTP
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      method: 'GET',
      headers: { ...this.defaultHeaders },
      ...options,
    };

    // Agregar token de autenticación si existe
    const token = this.getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Agregar timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    config.signal = controller.signal;

    try {
      const response = await fetch(url, config);
      clearTimeout(timeoutId);

      // Manejar respuestas no exitosas
      if (!response.ok) {
        await this.handleErrorResponse(response);
      }

      // Intentar parsear JSON
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }

      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      this.handleRequestError(error);
      throw error;
    }
  }

  /**
   * Métodos HTTP de conveniencia
   */
  get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(url);
  }

  post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  patch(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }

  /**
   * Subida de archivos
   */
  upload(endpoint, formData) {
    const headers = { ...this.defaultHeaders };
    delete headers['Content-Type']; // Dejar que el browser establezca el boundary

    return this.request(endpoint, {
      method: 'POST',
      headers,
      body: formData,
    });
  }

  /**
   * Manejo de token de autenticación
   */
  getAuthToken() {
    return localStorage.getItem('auth_token');
  }

  setAuthToken(token) {
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  /**
   * Manejo de errores de respuesta
   */
  async handleErrorResponse(response) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { message: 'Error de servidor' };
    }

    const error = new Error(errorData.message || `HTTP ${response.status}`);
    error.status = response.status;
    error.data = errorData;

    // Manejar errores específicos
    switch (response.status) {
      case 401:
        this.handleUnauthorized();
        break;
      case 403:
        error.message = 'No tienes permisos para realizar esta acción';
        break;
      case 404:
        error.message = 'Recurso no encontrado';
        break;
      case 422:
        error.message = 'Datos de entrada inválidos';
        break;
      case 429:
        error.message = 'Demasiadas peticiones, intenta más tarde';
        break;
      case 500:
        error.message = 'Error interno del servidor';
        break;
    }

    throw error;
  }

  /**
   * Manejo de errores de petición
   */
  handleRequestError(error) {
    if (error.name === 'AbortError') {
      error.message = 'La petición ha tardado demasiado';
    } else if (!navigator.onLine) {
      error.message = 'Sin conexión a internet';
    } else {
      error.message = error.message || 'Error de conexión';
    }
  }

  /**
   * Manejo de no autorizado
   */
  handleUnauthorized() {
    this.setAuthToken(null);
    // Redirigir a login si no estamos ya ahí
    if (window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
  }
}

// Instancia global del cliente API
export const apiClient = new ApiClient();

/**
 * Servicios específicos de la API
 */
export const authAPI = {
  login: (credentials) => apiClient.post('/auth/login', credentials),
  register: (userData) => apiClient.post('/auth/register', userData),
  logout: () => apiClient.post('/auth/logout'),
  refreshToken: () => apiClient.post('/auth/refresh'),
  forgotPassword: (email) => apiClient.post('/auth/forgot-password', { email }),
  resetPassword: (data) => apiClient.post('/auth/reset-password', data),
  verifyEmail: (token) => apiClient.post('/auth/verify-email', { token }),
  getProfile: () => apiClient.get('/auth/profile'),
  updateProfile: (data) => apiClient.put('/auth/profile', data),
};

export const productsAPI = {
  getAll: (params) => apiClient.get('/products', params),
  getById: (id) => apiClient.get(`/products/${id}`),
  getByCategory: (categoryId, params) => apiClient.get(`/categories/${categoryId}/products`, params),
  search: (query, params) => apiClient.get('/products/search', { q: query, ...params }),
  getFeatured: () => apiClient.get('/products/featured'),
  getRelated: (id) => apiClient.get(`/products/${id}/related`),
};

export const categoriesAPI = {
  getAll: () => apiClient.get('/categories'),
  getById: (id) => apiClient.get(`/categories/${id}`),
  getTree: () => apiClient.get('/categories/tree'),
};

export const cartAPI = {
  get: () => apiClient.get('/cart'),
  add: (productId, quantity, options) => apiClient.post('/cart/items', { 
    product_id: productId, 
    quantity, 
    options 
  }),
  update: (itemId, quantity) => apiClient.put(`/cart/items/${itemId}`, { quantity }),
  remove: (itemId) => apiClient.delete(`/cart/items/${itemId}`),
  clear: () => apiClient.delete('/cart'),
  applyCoupon: (code) => apiClient.post('/cart/coupon', { code }),
  removeCoupon: () => apiClient.delete('/cart/coupon'),
};

export const ordersAPI = {
  create: (orderData) => apiClient.post('/orders', orderData),
  getAll: (params) => apiClient.get('/orders', params),
  getById: (id) => apiClient.get(`/orders/${id}`),
  cancel: (id) => apiClient.post(`/orders/${id}/cancel`),
  track: (id) => apiClient.get(`/orders/${id}/tracking`),
};

export const paymentsAPI = {
  createIntent: (orderData) => apiClient.post('/payments/intent', orderData),
  confirm: (paymentId, data) => apiClient.post(`/payments/${paymentId}/confirm`, data),
  getMethods: () => apiClient.get('/payments/methods'),
};

export const reviewsAPI = {
  getByProduct: (productId, params) => apiClient.get(`/products/${productId}/reviews`, params),
  create: (productId, reviewData) => apiClient.post(`/products/${productId}/reviews`, reviewData),
  update: (reviewId, reviewData) => apiClient.put(`/reviews/${reviewId}`, reviewData),
  delete: (reviewId) => apiClient.delete(`/reviews/${reviewId}`),
};

export const wishlistAPI = {
  get: () => apiClient.get('/wishlist'),
  add: (productId) => apiClient.post('/wishlist/items', { product_id: productId }),
  remove: (productId) => apiClient.delete(`/wishlist/items/${productId}`),
  clear: () => apiClient.delete('/wishlist'),
};

export const addressesAPI = {
  getAll: () => apiClient.get('/addresses'),
  create: (addressData) => apiClient.post('/addresses', addressData),
  update: (id, addressData) => apiClient.put(`/addresses/${id}`, addressData),
  delete: (id) => apiClient.delete(`/addresses/${id}`),
  setDefault: (id) => apiClient.post(`/addresses/${id}/default`),
};

// Configuración de interceptores globales
export const setupInterceptors = () => {
  // Interceptor para refresh token automático
  const originalRequest = apiClient.request.bind(apiClient);
  
  apiClient.request = async function(endpoint, options = {}) {
    try {
      return await originalRequest(endpoint, options);
    } catch (error) {
      if (error.status === 401 && !options._retry) {
        options._retry = true;
        
        try {
          const response = await authAPI.refreshToken();
          apiClient.setAuthToken(response.access_token);
          return await originalRequest(endpoint, options);
        } catch (refreshError) {
          apiClient.handleUnauthorized();
          throw refreshError;
        }
      }
      throw error;
    }
  };
};

// Configurar interceptores al cargar el módulo
setupInterceptors();

export default apiClient;


import React, { createContext, useContext, useReducer, useEffect } from 'react';
import apiService from '../lib/api';

// Cart Context
const CartContext = createContext();

// Cart Actions
const CART_ACTIONS = {
  SET_CART: 'SET_CART',
  ADD_ITEM: 'ADD_ITEM',
  UPDATE_ITEM: 'UPDATE_ITEM',
  REMOVE_ITEM: 'REMOVE_ITEM',
  CLEAR_CART: 'CLEAR_CART',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
};

// Cart Reducer
const cartReducer = (state, action) => {
  switch (action.type) {
    case CART_ACTIONS.SET_CART:
      return {
        ...state,
        items: action.payload.items || [],
        total: action.payload.total || 0,
        loading: false,
        error: null,
      };
    case CART_ACTIONS.ADD_ITEM:
      const existingItemIndex = state.items.findIndex(
        item => item.product_id === action.payload.product_id
      );
      
      if (existingItemIndex >= 0) {
        const updatedItems = [...state.items];
        updatedItems[existingItemIndex].quantity += action.payload.quantity;
        return {
          ...state,
          items: updatedItems,
        };
      } else {
        return {
          ...state,
          items: [...state.items, action.payload],
        };
      }
    case CART_ACTIONS.UPDATE_ITEM:
      return {
        ...state,
        items: state.items.map(item =>
          item.id === action.payload.id
            ? { ...item, quantity: action.payload.quantity }
            : item
        ),
      };
    case CART_ACTIONS.REMOVE_ITEM:
      return {
        ...state,
        items: state.items.filter(item => item.id !== action.payload),
      };
    case CART_ACTIONS.CLEAR_CART:
      return {
        ...state,
        items: [],
        total: 0,
      };
    case CART_ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
      };
    case CART_ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        loading: false,
      };
    default:
      return state;
  }
};

// Initial state
const initialState = {
  items: [],
  total: 0,
  loading: false,
  error: null,
};

// Cart Provider Component
export const CartProvider = ({ children }) => {
  const [state, dispatch] = useReducer(cartReducer, initialState);

  // Load cart on mount
  useEffect(() => {
    loadCart();
  }, []);

  // Calculate totals when items change
  useEffect(() => {
    const total = state.items.reduce((sum, item) => {
      const price = parseFloat(item.sale_price || item.price || 0);
      return sum + (price * item.quantity);
    }, 0);
    
    if (total !== state.total) {
      dispatch({
        type: CART_ACTIONS.SET_CART,
        payload: { items: state.items, total },
      });
    }
  }, [state.items]);

  // Load cart from API
  const loadCart = async () => {
    try {
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: true });
      const cartData = await apiService.getCart();
      dispatch({
        type: CART_ACTIONS.SET_CART,
        payload: cartData,
      });
    } catch (error) {
      // If cart API fails, use local storage as fallback
      const localCart = JSON.parse(localStorage.getItem('cart') || '{"items": [], "total": 0}');
      dispatch({
        type: CART_ACTIONS.SET_CART,
        payload: localCart,
      });
    }
  };

  // Add item to cart
  const addToCart = async (product, quantity = 1) => {
    try {
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: true });
      
      // Try to add to server cart
      try {
        await apiService.addToCart(product.id, quantity);
      } catch (error) {
        console.warn('Failed to add to server cart, using local cart');
      }
      
      // Add to local state
      const cartItem = {
        id: `local_${product.id}_${Date.now()}`,
        product_id: product.id,
        product_name: product.name,
        price: product.price,
        sale_price: product.sale_price,
        image_url: product.image_url,
        quantity,
      };
      
      dispatch({
        type: CART_ACTIONS.ADD_ITEM,
        payload: cartItem,
      });
      
      // Save to localStorage as backup
      const updatedCart = {
        items: [...state.items, cartItem],
        total: state.total,
      };
      localStorage.setItem('cart', JSON.stringify(updatedCart));
      
    } catch (error) {
      dispatch({
        type: CART_ACTIONS.SET_ERROR,
        payload: error.message,
      });
    }
  };

  // Update item quantity
  const updateCartItem = async (itemId, quantity) => {
    try {
      if (quantity <= 0) {
        return removeFromCart(itemId);
      }
      
      // Try to update on server
      try {
        await apiService.updateCartItem(itemId, quantity);
      } catch (error) {
        console.warn('Failed to update server cart, using local cart');
      }
      
      dispatch({
        type: CART_ACTIONS.UPDATE_ITEM,
        payload: { id: itemId, quantity },
      });
      
      // Update localStorage
      const updatedItems = state.items.map(item =>
        item.id === itemId ? { ...item, quantity } : item
      );
      localStorage.setItem('cart', JSON.stringify({ items: updatedItems, total: state.total }));
      
    } catch (error) {
      dispatch({
        type: CART_ACTIONS.SET_ERROR,
        payload: error.message,
      });
    }
  };

  // Remove item from cart
  const removeFromCart = async (itemId) => {
    try {
      // Try to remove from server
      try {
        await apiService.removeFromCart(itemId);
      } catch (error) {
        console.warn('Failed to remove from server cart, using local cart');
      }
      
      dispatch({
        type: CART_ACTIONS.REMOVE_ITEM,
        payload: itemId,
      });
      
      // Update localStorage
      const updatedItems = state.items.filter(item => item.id !== itemId);
      localStorage.setItem('cart', JSON.stringify({ items: updatedItems, total: state.total }));
      
    } catch (error) {
      dispatch({
        type: CART_ACTIONS.SET_ERROR,
        payload: error.message,
      });
    }
  };

  // Clear cart
  const clearCart = () => {
    dispatch({ type: CART_ACTIONS.CLEAR_CART });
    localStorage.removeItem('cart');
  };

  // Get cart item count
  const getItemCount = () => {
    return state.items.reduce((count, item) => count + item.quantity, 0);
  };

  // Context value
  const value = {
    ...state,
    addToCart,
    updateCartItem,
    removeFromCart,
    clearCart,
    getItemCount,
    loadCart,
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};

// Custom hook to use cart context
export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};


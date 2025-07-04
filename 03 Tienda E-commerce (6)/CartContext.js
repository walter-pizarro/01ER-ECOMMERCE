import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const CartContext = createContext();

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

export const CartProvider = ({ children }) => {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);

  // Load cart from localStorage on mount
  useEffect(() => {
    loadCartFromStorage();
  }, [user]);

  // Save cart to localStorage whenever items change
  useEffect(() => {
    saveCartToStorage();
  }, [items, user]);

  const getStorageKey = () => {
    return user ? `cart_${user.id}` : 'cart_guest';
  };

  const loadCartFromStorage = () => {
    try {
      const storageKey = getStorageKey();
      const savedCart = localStorage.getItem(storageKey);
      
      if (savedCart) {
        const parsedCart = JSON.parse(savedCart);
        setItems(parsedCart || []);
      } else {
        setItems([]);
      }
    } catch (error) {
      console.error('Error loading cart from storage:', error);
      setItems([]);
    }
  };

  const saveCartToStorage = () => {
    try {
      const storageKey = getStorageKey();
      localStorage.setItem(storageKey, JSON.stringify(items));
    } catch (error) {
      console.error('Error saving cart to storage:', error);
    }
  };

  const addItem = (product, quantity = 1, selectedVariant = null) => {
    setItems(currentItems => {
      const existingItemIndex = currentItems.findIndex(item => 
        item.product.id === product.id && 
        JSON.stringify(item.selectedVariant) === JSON.stringify(selectedVariant)
      );

      if (existingItemIndex >= 0) {
        // Update quantity of existing item
        const updatedItems = [...currentItems];
        updatedItems[existingItemIndex] = {
          ...updatedItems[existingItemIndex],
          quantity: updatedItems[existingItemIndex].quantity + quantity
        };
        return updatedItems;
      } else {
        // Add new item
        const newItem = {
          id: `${product.id}_${Date.now()}`, // Unique ID for cart item
          product,
          quantity,
          selectedVariant,
          addedAt: new Date().toISOString()
        };
        return [...currentItems, newItem];
      }
    });
  };

  const removeItem = (itemId) => {
    setItems(currentItems => 
      currentItems.filter(item => item.id !== itemId)
    );
  };

  const updateQuantity = (itemId, newQuantity) => {
    if (newQuantity <= 0) {
      removeItem(itemId);
      return;
    }

    setItems(currentItems =>
      currentItems.map(item =>
        item.id === itemId
          ? { ...item, quantity: newQuantity }
          : item
      )
    );
  };

  const clearCart = () => {
    setItems([]);
  };

  const getItemPrice = (item) => {
    // Use variant price if available, otherwise use product price
    if (item.selectedVariant && item.selectedVariant.price) {
      return parseFloat(item.selectedVariant.price);
    }
    return parseFloat(item.product.price || 0);
  };

  const getItemTotal = (item) => {
    return getItemPrice(item) * item.quantity;
  };

  const getSubtotal = () => {
    return items.reduce((total, item) => total + getItemTotal(item), 0);
  };

  const getTaxAmount = (taxRate = 0.1) => {
    return getSubtotal() * taxRate;
  };

  const getShippingAmount = () => {
    const subtotal = getSubtotal();
    // Free shipping over $100, otherwise $10
    return subtotal >= 100 ? 0 : 10;
  };

  const getTotal = (taxRate = 0.1) => {
    return getSubtotal() + getTaxAmount(taxRate) + getShippingAmount();
  };

  const getItemCount = () => {
    return items.reduce((count, item) => count + item.quantity, 0);
  };

  const getUniqueItemCount = () => {
    return items.length;
  };

  const isInCart = (productId, variant = null) => {
    return items.some(item => 
      item.product.id === productId && 
      JSON.stringify(item.selectedVariant) === JSON.stringify(variant)
    );
  };

  const getCartItem = (productId, variant = null) => {
    return items.find(item => 
      item.product.id === productId && 
      JSON.stringify(item.selectedVariant) === JSON.stringify(variant)
    );
  };

  // Validate cart items against current product data
  const validateCart = async () => {
    setLoading(true);
    try {
      // This would typically make API calls to validate product availability and prices
      // For now, we'll just simulate validation
      const validatedItems = items.filter(item => {
        // Check if product is still available
        if (!item.product.is_active) {
          return false;
        }
        
        // Check if there's enough inventory
        if (item.product.inventory_quantity < item.quantity) {
          // Update quantity to available amount
          item.quantity = Math.max(0, item.product.inventory_quantity);
          return item.quantity > 0;
        }
        
        return true;
      });

      setItems(validatedItems);
      return {
        success: true,
        removedItems: items.length - validatedItems.length
      };
    } catch (error) {
      console.error('Cart validation error:', error);
      return {
        success: false,
        error: 'Failed to validate cart'
      };
    } finally {
      setLoading(false);
    }
  };

  // Merge guest cart with user cart on login
  const mergeGuestCart = () => {
    try {
      const guestCart = localStorage.getItem('cart_guest');
      const userCart = localStorage.getItem(`cart_${user.id}`);
      
      if (guestCart && user) {
        const guestItems = JSON.parse(guestCart) || [];
        const userItems = JSON.parse(userCart) || [];
        
        // Merge items, avoiding duplicates
        const mergedItems = [...userItems];
        
        guestItems.forEach(guestItem => {
          const existingIndex = mergedItems.findIndex(userItem =>
            userItem.product.id === guestItem.product.id &&
            JSON.stringify(userItem.selectedVariant) === JSON.stringify(guestItem.selectedVariant)
          );
          
          if (existingIndex >= 0) {
            // Combine quantities
            mergedItems[existingIndex].quantity += guestItem.quantity;
          } else {
            // Add new item
            mergedItems.push(guestItem);
          }
        });
        
        setItems(mergedItems);
        
        // Clear guest cart
        localStorage.removeItem('cart_guest');
      }
    } catch (error) {
      console.error('Error merging guest cart:', error);
    }
  };

  // Call merge when user logs in
  useEffect(() => {
    if (user) {
      mergeGuestCart();
    }
  }, [user]);

  const value = {
    items,
    loading,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    getItemPrice,
    getItemTotal,
    getSubtotal,
    getTaxAmount,
    getShippingAmount,
    getTotal,
    getItemCount,
    getUniqueItemCount,
    isInCart,
    getCartItem,
    validateCart,
    mergeGuestCart
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};


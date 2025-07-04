import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../../contexts/CartContext';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import { apiClient } from '../../services/api';

const Checkout = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { items, getSubtotal, getTax, getShipping, getTotal, clearCart } = useCart();
  const { success, error } = useToast();
  
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [addresses, setAddresses] = useState([]);
  const [selectedAddress, setSelectedAddress] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('credit_card');
  const [cardDetails, setCardDetails] = useState({
    number: '',
    name: '',
    expiry: '',
    cvc: ''
  });
  const [newAddress, setNewAddress] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'Chile',
    phone: ''
  });
  const [addingNewAddress, setAddingNewAddress] = useState(false);
  const [orderComplete, setOrderComplete] = useState(false);
  const [orderId, setOrderId] = useState(null);

  useEffect(() => {
    // Redirect if not logged in
    if (!user) {
      navigate('/login?redirect=/checkout');
      return;
    }

    // Redirect if cart is empty
    if (items.length === 0 && !orderComplete) {
      navigate('/cart');
      return;
    }

    // Load user addresses
    loadAddresses();
  }, [user, items.length, navigate]);

  const loadAddresses = async () => {
    try {
      const response = await apiClient.get('/user/addresses');
      if (response.data.success) {
        setAddresses(response.data.addresses || []);
        if (response.data.addresses?.length > 0) {
          // Select default address
          const defaultAddress = response.data.addresses.find(addr => addr.is_default) || response.data.addresses[0];
          setSelectedAddress(defaultAddress.id);
        }
      }
    } catch (err) {
      console.error('Error loading addresses:', err);
      error('Error al cargar direcciones');
    }
  };

  const handleAddressChange = (addressId) => {
    setSelectedAddress(addressId);
  };

  const handleNewAddressChange = (e) => {
    const { name, value } = e.target;
    setNewAddress(prev => ({ ...prev, [name]: value }));
  };

  const handleAddNewAddress = async () => {
    // Validate address
    const requiredFields = ['first_name', 'last_name', 'address_line1', 'city', 'state', 'postal_code', 'country', 'phone'];
    const missingFields = requiredFields.filter(field => !newAddress[field]);
    
    if (missingFields.length > 0) {
      error('Por favor completa todos los campos obligatorios');
      return;
    }

    try {
      setLoading(true);
      const response = await apiClient.post('/user/addresses', newAddress);
      if (response.data.success) {
        success('Dirección agregada correctamente');
        setAddresses([...addresses, response.data.address]);
        setSelectedAddress(response.data.address.id);
        setAddingNewAddress(false);
      } else {
        error('Error al agregar dirección');
      }
    } catch (err) {
      console.error('Error adding address:', err);
      error('Error al agregar dirección');
    } finally {
      setLoading(false);
    }
  };

  const handleCardDetailsChange = (e) => {
    const { name, value } = e.target;
    setCardDetails(prev => ({ ...prev, [name]: value }));
  };

  const validateStep1 = () => {
    if (!selectedAddress && !addingNewAddress) {
      error('Por favor selecciona una dirección de envío');
      return false;
    }
    
    if (addingNewAddress) {
      const requiredFields = ['first_name', 'last_name', 'address_line1', 'city', 'state', 'postal_code', 'country', 'phone'];
      const missingFields = requiredFields.filter(field => !newAddress[field]);
      
      if (missingFields.length > 0) {
        error('Por favor completa todos los campos obligatorios');
        return false;
      }
    }
    
    return true;
  };

  const validateStep2 = () => {
    if (paymentMethod === 'credit_card') {
      const { number, name, expiry, cvc } = cardDetails;
      
      if (!number || !name || !expiry || !cvc) {
        error('Por favor completa todos los campos de la tarjeta');
        return false;
      }
      
      // Basic validation
      if (number.replace(/\s/g, '').length !== 16) {
        error('Número de tarjeta inválido');
        return false;
      }
      
      if (!/^\d{2}\/\d{2}$/.test(expiry)) {
        error('Fecha de expiración inválida (MM/YY)');
        return false;
      }
      
      if (!/^\d{3,4}$/.test(cvc)) {
        error('Código CVC inválido');
        return false;
      }
    }
    
    return true;
  };

  const nextStep = () => {
    if (step === 1 && validateStep1()) {
      setStep(2);
    } else if (step === 2 && validateStep2()) {
      setStep(3);
    }
  };

  const prevStep = () => {
    setStep(step - 1);
  };

  const placeOrder = async () => {
    try {
      setLoading(true);
      
      // Get the selected address
      const address = addresses.find(addr => addr.id === selectedAddress);
      
      // Prepare order data
      const orderData = {
        items: items.map(item => ({
          product_id: item.product.id,
          variant_id: item.variant?.id,
          quantity: item.quantity,
          price: item.price
        })),
        shipping_address_id: selectedAddress,
        payment_method: paymentMethod,
        subtotal: getSubtotal(),
        tax: getTax(),
        shipping: getShipping(),
        total: getTotal()
      };
      
      // Add payment details if credit card
      if (paymentMethod === 'credit_card') {
        orderData.payment_details = {
          card_number: cardDetails.number.replace(/\s/g, '').slice(-4), // Only store last 4 digits
          card_holder: cardDetails.name,
          card_expiry: cardDetails.expiry
        };
      }
      
      // Place order
      const response = await apiClient.post('/orders', orderData);
      
      if (response.data.success) {
        setOrderId(response.data.order.id);
        setOrderComplete(true);
        clearCart(); // Clear the cart after successful order
        success('¡Pedido realizado con éxito!');
      } else {
        error('Error al procesar el pedido');
      }
    } catch (err) {
      console.error('Error placing order:', err);
      error('Error al procesar el pedido');
    } finally {
      setLoading(false);
    }
  };

  // Order success screen
  if (orderComplete) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">¡Gracias por tu compra!</h1>
          <p className="text-lg text-gray-600 mb-8">
            Tu pedido #{orderId} ha sido recibido y está siendo procesado.
          </p>
          <p className="text-gray-600 mb-8">
            Te hemos enviado un correo electrónico con los detalles de tu pedido.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <button
              onClick={() => navigate(`/account/orders/${orderId}`)}
              className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Ver Detalles del Pedido
            </button>
            <button
              onClick={() => navigate('/')}
              className="px-6 py-3 bg-gray-200 text-gray-800 font-medium rounded-lg hover:bg-gray-300 transition-colors"
            >
              Volver a la Tienda
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Checkout</h1>
        
        {/* Progress Steps */}
        <div className="mt-8">
          <div className="flex items-center justify-between">
            <div className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
              }`}>
                1
              </div>
              <span className="text-sm mt-2">Envío</span>
            </div>
            <div className={`flex-1 h-1 mx-4 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
            <div className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
              }`}>
                2
              </div>
              <span className="text-sm mt-2">Pago</span>
            </div>
            <div className={`flex-1 h-1 mx-4 ${step >= 3 ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
            <div className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
              }`}>
                3
              </div>
              <span className="text-sm mt-2">Confirmación</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            {/* Step 1: Shipping */}
            {step === 1 && (
              <div className="p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Dirección de Envío</h2>
                
                {/* Existing Addresses */}
                {addresses.length > 0 && !addingNewAddress && (
                  <div className="space-y-4 mb-6">
                    {addresses.map((address) => (
                      <div
                        key={address.id}
                        className={`border rounded-lg p-4 cursor-pointer ${
                          selectedAddress === address.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => handleAddressChange(address.id)}
                      >
                        <div className="flex items-start">
                          <input
                            type="radio"
                            checked={selectedAddress === address.id}
                            onChange={() => handleAddressChange(address.id)}
                            className="mt-1 h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                          />
                          <div className="ml-3">
                            <p className="font-medium text-gray-900">
                              {address.first_name} {address.last_name}
                            </p>
                            <p className="text-gray-600">
                              {address.address_line1}
                              {address.address_line2 && `, ${address.address_line2}`}
                            </p>
                            <p className="text-gray-600">
                              {address.city}, {address.state} {address.postal_code}
                            </p>
                            <p className="text-gray-600">{address.country}</p>
                            <p className="text-gray-600">{address.phone}</p>
                            {address.is_default && (
                              <span className="inline-flex items-center mt-1 px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                Predeterminada
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Add New Address Button */}
                {!addingNewAddress && (
                  <button
                    onClick={() => setAddingNewAddress(true)}
                    className="flex items-center text-blue-600 hover:text-blue-800 font-medium"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Agregar Nueva Dirección
                  </button>
                )}

                {/* New Address Form */}
                {addingNewAddress && (
                  <div className="mt-6 border rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Nueva Dirección</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Nombre *
                        </label>
                        <input
                          type="text"
                          name="first_name"
                          value={newAddress.first_name}
                          onChange={handleNewAddressChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Apellido *
                        </label>
                        <input
                          type="text"
                          name="last_name"
                          value={newAddress.last_name}
                          onChange={handleNewAddressChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Dirección Línea 1 *
                        </label>
                        <input
                          type="text"
                          name="address_line1"
                          value={newAddress.address_line1}
                          onChange={handleNewAddressChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Dirección Línea 2
                        </label>
                        <input
                          type="text"
                          name="address_line2"
                          value={newAddress.address_line2}
                          onChange={handleNewAddressChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Ciudad *
                        </label>
                        <input
                          type="text"
                          name="city"
                          value={newAddress.city}
                          onChange={handleNewAddressChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Región/Estado *
                        </label>
                        <input
                          type="text"
                          name="state"
                          value={newAddress.state}
                          onChange={handleNewAddressChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Código Postal *
                        </label>
                        <input
                          type="text"
                          name="postal_code"
                          value={newAddress.postal_code}
                          onChange={handleNewAddressChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          País *
                        </label>
                        <select
                          name="country"
                          value={newAddress.country}
                          onChange={handleNewAddressChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          required
                        >
                          <option value="Chile">Chile</option>
                          <option value="Argentina">Argentina</option>
                          <option value="Perú">Perú</option>
                          <option value="Colombia">Colombia</option>
                          <option value="México">México</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Teléfono *
                        </label>
                        <input
                          type="tel"
                          name="phone"
                          value={newAddress.phone}
                          onChange={handleNewAddressChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          required
                        />
                      </div>
                    </div>

                    <div className="mt-6 flex justify-end space-x-4">
                      <button
                        onClick={() => setAddingNewAddress(false)}
                        className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
                      >
                        Cancelar
                      </button>
                      <button
                        onClick={handleAddNewAddress}
                        disabled={loading}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-blue-300"
                      >
                        {loading ? 'Guardando...' : 'Guardar Dirección'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Step 2: Payment */}
            {step === 2 && (
              <div className="p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Método de Pago</h2>
                
                <div className="space-y-4">
                  {/* Payment Method Selection */}
                  <div className="space-y-4">
                    <div
                      className={`border rounded-lg p-4 cursor-pointer ${
                        paymentMethod === 'credit_card' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setPaymentMethod('credit_card')}
                    >
                      <div className="flex items-center">
                        <input
                          type="radio"
                          checked={paymentMethod === 'credit_card'}
                          onChange={() => setPaymentMethod('credit_card')}
                          className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                        />
                        <div className="ml-3">
                          <span className="font-medium text-gray-900">Tarjeta de Crédito/Débito</span>
                        </div>
                        <div className="ml-auto flex space-x-2">
                          <img src="/api/placeholder/40/25" alt="Visa" className="h-6" />
                          <img src="/api/placeholder/40/25" alt="Mastercard" className="h-6" />
                          <img src="/api/placeholder/40/25" alt="Amex" className="h-6" />
                        </div>
                      </div>
                    </div>

                    <div
                      className={`border rounded-lg p-4 cursor-pointer ${
                        paymentMethod === 'paypal' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setPaymentMethod('paypal')}
                    >
                      <div className="flex items-center">
                        <input
                          type="radio"
                          checked={paymentMethod === 'paypal'}
                          onChange={() => setPaymentMethod('paypal')}
                          className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                        />
                        <div className="ml-3">
                          <span className="font-medium text-gray-900">PayPal</span>
                        </div>
                        <div className="ml-auto">
                          <img src="/api/placeholder/60/25" alt="PayPal" className="h-6" />
                        </div>
                      </div>
                    </div>

                    <div
                      className={`border rounded-lg p-4 cursor-pointer ${
                        paymentMethod === 'bank_transfer' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setPaymentMethod('bank_transfer')}
                    >
                      <div className="flex items-center">
                        <input
                          type="radio"
                          checked={paymentMethod === 'bank_transfer'}
                          onChange={() => setPaymentMethod('bank_transfer')}
                          className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                        />
                        <div className="ml-3">
                          <span className="font-medium text-gray-900">Transferencia Bancaria</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Credit Card Form */}
                  {paymentMethod === 'credit_card' && (
                    <div className="mt-6 border rounded-lg p-6">
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Detalles de la Tarjeta</h3>
                      
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Número de Tarjeta
                          </label>
                          <input
                            type="text"
                            name="number"
                            value={cardDetails.number}
                            onChange={handleCardDetailsChange}
                            placeholder="1234 5678 9012 3456"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            maxLength="19"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Nombre en la Tarjeta
                          </label>
                          <input
                            type="text"
                            name="name"
                            value={cardDetails.name}
                            onChange={handleCardDetailsChange}
                            placeholder="JUAN PEREZ"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Fecha de Expiración
                            </label>
                            <input
                              type="text"
                              name="expiry"
                              value={cardDetails.expiry}
                              onChange={handleCardDetailsChange}
                              placeholder="MM/YY"
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                              maxLength="5"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              CVC
                            </label>
                            <input
                              type="text"
                              name="cvc"
                              value={cardDetails.cvc}
                              onChange={handleCardDetailsChange}
                              placeholder="123"
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                              maxLength="4"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* PayPal Instructions */}
                  {paymentMethod === 'paypal' && (
                    <div className="mt-6 border rounded-lg p-6">
                      <p className="text-gray-600">
                        Serás redirigido a PayPal para completar tu pago después de revisar tu pedido.
                      </p>
                    </div>
                  )}

                  {/* Bank Transfer Instructions */}
                  {paymentMethod === 'bank_transfer' && (
                    <div className="mt-6 border rounded-lg p-6">
                      <p className="text-gray-600 mb-4">
                        Realiza una transferencia bancaria a la siguiente cuenta:
                      </p>
                      <div className="bg-gray-50 p-4 rounded-md">
                        <p className="font-medium">Banco: Banco de Chile</p>
                        <p>Titular: eCommerce Modular SpA</p>
                        <p>RUT: 76.123.456-7</p>
                        <p>Cuenta Corriente: 123-456-789</p>
                        <p>Email: pagos@ecommercemodular.com</p>
                      </div>
                      <p className="text-sm text-gray-500 mt-4">
                        Tu pedido será procesado una vez que confirmemos el pago.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Step 3: Review */}
            {step === 3 && (
              <div className="p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Revisar y Confirmar</h2>
                
                {/* Shipping Address */}
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900">Dirección de Envío</h3>
                    <button
                      onClick={() => setStep(1)}
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      Editar
                    </button>
                  </div>
                  
                  {selectedAddress && (
                    <div className="bg-gray-50 p-4 rounded-md">
                      {addresses.map((address) => {
                        if (address.id === selectedAddress) {
                          return (
                            <div key={address.id}>
                              <p className="font-medium">
                                {address.first_name} {address.last_name}
                              </p>
                              <p>
                                {address.address_line1}
                                {address.address_line2 && `, ${address.address_line2}`}
                              </p>
                              <p>
                                {address.city}, {address.state} {address.postal_code}
                              </p>
                              <p>{address.country}</p>
                              <p>{address.phone}</p>
                            </div>
                          );
                        }
                        return null;
                      })}
                    </div>
                  )}
                </div>
                
                {/* Payment Method */}
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900">Método de Pago</h3>
                    <button
                      onClick={() => setStep(2)}
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      Editar
                    </button>
                  </div>
                  
                  <div className="bg-gray-50 p-4 rounded-md">
                    {paymentMethod === 'credit_card' && (
                      <div>
                        <p className="font-medium">Tarjeta de Crédito/Débito</p>
                        <p>**** **** **** {cardDetails.number.slice(-4)}</p>
                        <p>{cardDetails.name}</p>
                        <p>Expira: {cardDetails.expiry}</p>
                      </div>
                    )}
                    
                    {paymentMethod === 'paypal' && (
                      <p className="font-medium">PayPal</p>
                    )}
                    
                    {paymentMethod === 'bank_transfer' && (
                      <p className="font-medium">Transferencia Bancaria</p>
                    )}
                  </div>
                </div>
                
                {/* Order Items */}
                <div className="mb-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Productos</h3>
                  
                  <div className="border rounded-md overflow-hidden">
                    <div className="divide-y divide-gray-200">
                      {items.map((item) => (
                        <div key={`${item.product.id}-${item.variant?.id || 'default'}`} className="p-4 flex items-center">
                          <div className="flex-shrink-0">
                            <img
                              src={item.product.images?.[0]?.image_url || '/api/placeholder/60/60'}
                              alt={item.product.name}
                              className="w-16 h-16 object-cover rounded-md"
                            />
                          </div>
                          <div className="ml-4 flex-1">
                            <h4 className="font-medium text-gray-900">{item.product.name}</h4>
                            {item.variant && (
                              <p className="text-sm text-gray-600">
                                {item.variant.size} - {item.variant.color}
                              </p>
                            )}
                            <p className="text-sm text-gray-500">Cantidad: {item.quantity}</p>
                          </div>
                          <div className="ml-4">
                            <p className="font-medium text-gray-900">
                              ${(parseFloat(item.price) * item.quantity).toFixed(2)}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Navigation Buttons */}
          <div className="mt-6 flex justify-between">
            {step > 1 && (
              <button
                onClick={prevStep}
                className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors"
              >
                Anterior
              </button>
            )}
            
            {step < 3 ? (
              <button
                onClick={nextStep}
                className="ml-auto px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                Siguiente
              </button>
            ) : (
              <button
                onClick={placeOrder}
                disabled={loading}
                className="ml-auto px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors disabled:bg-green-400"
              >
                {loading ? 'Procesando...' : 'Confirmar Pedido'}
              </button>
            )}
          </div>
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6 sticky top-24">
            <h2 className="text-lg font-medium text-gray-900 mb-6">Resumen del Pedido</h2>
            
            <div className="space-y-4">
              {/* Items Count */}
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Productos ({items.length})</span>
                <span className="font-medium">${getSubtotal().toFixed(2)}</span>
              </div>

              {/* Shipping */}
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Envío</span>
                <span className="font-medium">
                  {getShipping() === 0 ? 'Gratis' : `$${getShipping().toFixed(2)}`}
                </span>
              </div>

              {/* Tax */}
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Impuestos</span>
                <span className="font-medium">${getTax().toFixed(2)}</span>
              </div>

              {/* Divider */}
              <div className="border-t border-gray-200 pt-4">
                <div className="flex justify-between">
                  <span className="text-lg font-bold text-gray-900">Total</span>
                  <span className="text-lg font-bold text-blue-600">${getTotal().toFixed(2)}</span>
                </div>
              </div>
            </div>

            {/* Order Items */}
            <div className="mt-6">
              <h3 className="text-sm font-medium text-gray-900 mb-4">Productos en tu Carrito</h3>
              
              <div className="space-y-4">
                {items.map((item) => (
                  <div key={`${item.product.id}-${item.variant?.id || 'default'}`} className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <img
                        src={item.product.images?.[0]?.image_url || '/api/placeholder/40/40'}
                        alt={item.product.name}
                        className="w-10 h-10 object-cover rounded-md"
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {item.product.name}
                      </p>
                      {item.variant && (
                        <p className="text-xs text-gray-500">
                          {item.variant.size} - {item.variant.color}
                        </p>
                      )}
                      <p className="text-xs text-gray-500">
                        Cantidad: {item.quantity}
                      </p>
                    </div>
                    <div className="flex-shrink-0">
                      <p className="text-sm font-medium text-gray-900">
                        ${(parseFloat(item.price) * item.quantity).toFixed(2)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Security Badge */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <span className="text-sm font-medium text-gray-900">
                  Pago 100% Seguro
                </span>
              </div>
              <p className="text-xs text-gray-600 mt-2">
                Todas las transacciones están protegidas con encriptación SSL.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;


/**
 * allyClient.js - Consumer for allied/external services
 * 
 * Demonstrates consumption of external service API (e.g., competitor pricing,
 * weather, availability, etc.) from the frontend and backend.
 * 
 * Backend integration: call adapter in ProductService to fetch external data.
 * Frontend integration: display external product info alongside our catalog.
 */

export const allyServiceConfig = {
  baseUrl: process.env.REACT_APP_ALLY_SERVICE_URL || 'https://api.ally-service.local/v1',
  apiKey: process.env.REACT_APP_ALLY_API_KEY || '',
  timeout: 5000,
};

/**
 * Fetch products from allied service via our backend adapter.
 * Backend exposes: GET /api/v1/products/external/?query=...
 */
export const fetchExternalProducts = async (query = '') => {
  try {
    const endpoint = `/api/v1/products/external/?query=${encodeURIComponent(query)}`;
    const response = await fetch(endpoint, {
      headers: {
        'Content-Type': 'application/json',
        'Accept-Language': localStorage.getItem('language') || 'en',
      },
      timeout: allyServiceConfig.timeout,
    });
    
    if (!response.ok) {
      console.error(`Failed to fetch external products: ${response.statusText}`);
      return [];
    }
    
    const data = await response.json();
    return data.products || [];
  } catch (error) {
    console.error('Error fetching external products:', error);
    return [];
  }
};

/**
 * Fetch pricing from allied service for a specific product.
 * Backend exposes: GET /api/v1/products/:id/external-pricing/
 */
export const fetchExternalPricing = async (externalProductId) => {
  try {
    const endpoint = `/api/v1/products/external-pricing/${externalProductId}/`;
    const response = await fetch(endpoint, {
      headers: {
        'Content-Type': 'application/json',
        'Accept-Language': localStorage.getItem('language') || 'en',
      },
    });
    
    if (!response.ok) {
      console.error(`Failed to fetch external pricing: ${response.statusText}`);
      return null;
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching external pricing:', error);
    return null;
  }
};

/**
 * Submit order to allied service for fulfillment.
 * Backend exposes: POST /api/v1/orders/submit-to-ally/
 */
export const submitOrderToAlly = async (orderData) => {
  try {
    const response = await fetch('/api/v1/orders/submit-to-ally/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Accept-Language': localStorage.getItem('language') || 'en',
      },
      body: JSON.stringify(orderData),
    });
    
    if (!response.ok) {
      console.error(`Failed to submit order to ally: ${response.statusText}`);
      return { status: 'error' };
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error submitting order to ally:', error);
    return { status: 'error', message: error.message };
  }
};

/**
 * Sync inventory with allied service.
 * Backend exposes: POST /api/v1/inventory/sync-ally/
 */
export const syncInventoryWithAlly = async () => {
  try {
    const response = await fetch('/api/v1/inventory/sync-ally/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    
    if (!response.ok) {
      console.error(`Inventory sync failed: ${response.statusText}`);
      return { status: 'error' };
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error syncing inventory:', error);
    return { status: 'error', message: error.message };
  }
};

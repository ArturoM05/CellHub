import React, { useState, useEffect } from 'react';
import { fetchExternalProducts, fetchExternalPricing } from '../services/allyClient';

/**
 * AllyProductFeed - Component to display allied service products
 * Shows external/competitor products alongside our catalog
 * Demonstrates service integration pattern
 */
const AllyProductFeed = ({ query = '' }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadExternalProducts = async () => {
      setLoading(true);
      setError(null);
      try {
        const externalProducts = await fetchExternalProducts(query);
        setProducts(externalProducts);
      } catch (err) {
        setError('Failed to load external products');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (query) {
      loadExternalProducts();
    }
  }, [query]);

  const handlePricingClick = async (productId) => {
    try {
      const pricing = await fetchExternalPricing(productId);
      if (pricing) {
        alert(`Price: ${pricing.price} | Stock: ${pricing.quantity}`);
      }
    } catch (err) {
      alert('Failed to fetch pricing');
    }
  };

  if (loading) {
    return <div className="ally-feed loading">Loading external products...</div>;
  }

  if (error) {
    return <div className="ally-feed error">{error}</div>;
  }

  if (!products.length) {
    return <div className="ally-feed empty">No external products found</div>;
  }

  return (
    <div className="ally-feed">
      <h3>🔗 Allied Service Products</h3>
      <div className="products-grid">
        {products.map((product) => (
          <div key={product.external_id} className="product-card">
            <h4>{product.name}</h4>
            <p>Price: ${product.price}</p>
            <p>Stock: {product.in_stock ? 'Available' : 'Out of Stock'}</p>
            <button onClick={() => handlePricingClick(product.external_id)}>
              View Details
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AllyProductFeed;

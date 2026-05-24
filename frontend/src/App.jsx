import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Page,
  FooterHelp,
  Link,
  Button,
  InlineStack,
  Text,
  Box,
  Divider,
  Banner,
} from '@shopify/polaris';
import ProductCatalog from './components/ProductCatalog';
import AuthModal from './components/AuthModal';
import CartModal from './components/CartModal';
import CheckoutModal from './components/CheckoutModal';
import AllyServiceDashboard from './components/AllyServiceDashboard_proxy';
import { useToast } from './hooks/useToast';
import {
  apiFetch,
  loadStoredAuth,
  saveAuth,
  clearAuth,
  FILTER_MAP,
} from './utils';

export default function App() {
  const { toast, showToast, dismissToast } = useToast();

  const [token, setToken] = useState(() => loadStoredAuth().token);
  const [user, setUser] = useState(() => loadStoredAuth().user);

  const [allProducts, setAllProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);

  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  const [cartItems, setCartItems] = useState([]);
  const [addingId, setAddingId] = useState(null);

  const [authOpen, setAuthOpen] = useState(false);
  const [cartOpen, setCartOpen] = useState(false);
  const [checkoutOpen, setCheckoutOpen] = useState(false);

  const safeCartItems = Array.isArray(cartItems) ? cartItems : [];
  const cartCount = safeCartItems.reduce((s, i) => s + (i.quantity || 0), 0);

  const handleAuthSuccess = useCallback((newToken, newUser) => {
    setToken(newToken);
    setUser(newUser);
    saveAuth(newToken, newUser);
  }, []);

  const handleLogout = useCallback(() => {
    setToken(null);
    setUser(null);
    setCartItems([]);
    clearAuth();
  }, []);

  const syncCart = useCallback(
    async (authToken = token) => {
      if (!authToken) return;
      const { ok, data } = await apiFetch('/cart/summary/', {}, authToken);
      if (ok) setCartItems(Array.isArray(data.items) ? data.items : []);
    },
    [token],
  );

  const loadProducts = useCallback(async () => {
    setLoading(true);
    setLoadError(false);
    try {
      const res = await fetch('/api/v1/products/');
      const data = await res.json();
      setAllProducts(data.results || data);
    } catch {
      setLoadError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  useEffect(() => {
    if (token) syncCart();
  }, [token, syncCart]);

  const filteredProducts = useMemo(() => {
    const query = search.toLowerCase();
    let filtered = allProducts.filter(
      (p) =>
        !query ||
        p.brand.toLowerCase().includes(query) ||
        p.model_name.toLowerCase().includes(query),
    );
    if (FILTER_MAP[filter]) {
      filtered = filtered.filter(FILTER_MAP[filter]);
    }
    return filtered;
  }, [allProducts, search, filter]);

  const handleAddToCart = async (productId, name) => {
    if (!token) {
      showToast('Inicia sesión para agregar al carrito', true);
      setAuthOpen(true);
      return;
    }

    setAddingId(productId);
    const { ok, data } = await apiFetch(
      '/cart/add/',
      {
        method: 'POST',
        body: JSON.stringify({ product_id: productId, quantity: 1 }),
      },
      token,
    );
    setAddingId(null);

    if (!ok) {
      showToast(data.error || 'Error al agregar', true);
      return;
    }

    const items = data.cart?.items;
    setCartItems(Array.isArray(items) ? items : []);
    showToast('✓ ' + name + ' agregado');
  };

  const handleRemoveItem = async (itemId) => {
    const { ok } = await apiFetch(`/cart/remove/${itemId}/`, { method: 'DELETE' }, token);
    if (ok) {
      setCartItems((items) => items.filter((i) => i.id !== itemId));
    }
  };

  const handleCheckout = () => {
    if (!token) {
      setAuthOpen(true);
      return;
    }
    if (!safeCartItems.length) {
      showToast('Tu carrito está vacío', true);
      return;
    }
    setCartOpen(false);
    setCheckoutOpen(true);
  };

  const toastMarkup = toast ? (
    <Banner
      tone={toast.error ? 'critical' : 'success'}
      onDismiss={dismissToast}
    >
      {toast.content}
    </Banner>
  ) : null;

  return (
    <Page fullWidth>
      {toastMarkup && (
        <Box paddingBlockEnd="400">{toastMarkup}</Box>
      )}

      <Box paddingBlockEnd="400">
        <InlineStack align="space-between" blockAlign="center">
          <Text variant="headingLg" as="h1" fontWeight="bold">
            CellHub
          </Text>
          <InlineStack gap="300" blockAlign="center">
            {user && (
              <Text as="span" tone="subdued">
                👤 {user.username}
              </Text>
            )}
            <Button onClick={() => setCartOpen(true)}>
              🛒 Carrito
              {cartCount > 0 ? ` (${cartCount})` : ''}
            </Button>
            {user ? (
              <Button onClick={handleLogout}>Salir</Button>
            ) : (
              <Button variant="primary" onClick={() => setAuthOpen(true)}>
                Iniciar sesión
              </Button>
            )}
          </InlineStack>
        </InlineStack>
      </Box>

      <Divider />

      <Box paddingBlockStart="500">
        <ProductCatalog
          products={filteredProducts}
          loading={loading}
          error={loadError}
          search={search}
          onSearchChange={setSearch}
          filter={filter}
          onFilterChange={setFilter}
          onAddToCart={handleAddToCart}
          addingId={addingId}
        />
      </Box>

      <Box paddingBlockStart="600">
        <Text variant="headingMd" as="h2" fontWeight="medium">
          Servicio Aliado — UniversalGamePass
        </Text>
        <Box paddingBlockStart="300">
          <AllyServiceDashboard />
        </Box>
      </Box>

      <Box paddingBlockStart="800">
        <FooterHelp>
          📱 <strong>CellHub</strong> ·{' '}
          <Link url="/api/docs/">API Docs</Link> ·{' '}
          <Link url="/admin/">Admin</Link>
        </FooterHelp>
      </Box>

      <AuthModal
        open={authOpen}
        onClose={() => setAuthOpen(false)}
        onAuthSuccess={(t, u) => {
          handleAuthSuccess(t, u);
          syncCart(t);
        }}
        showToast={showToast}
      />

      <CartModal
        open={cartOpen}
        onClose={() => setCartOpen(false)}
        items={safeCartItems}
        onRemove={handleRemoveItem}
        onCheckout={handleCheckout}
      />

      <CheckoutModal
        open={checkoutOpen}
        onClose={() => setCheckoutOpen(false)}
        items={safeCartItems}
        token={token}
        user={user}
        showToast={showToast}
        onOrderSuccess={() => setCartItems([])}
      />

    </Page>
  );
}

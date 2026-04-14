/* ═══════════════════════════════════════════════════════════
   static/js/cellhub.js
   CellHub — Lógica del frontend
   Módulos:
     1. Configuración y estado global
     2. Helpers (formato, emojis, headers)
     3. Autenticación
     4. Productos y filtros
     5. Carrito
     6. Checkout
     7. Toast
     8. Inicialización
═══════════════════════════════════════════════════════════ */


/* ─────────────────────────────────────────────────────────
   1. CONFIGURACIÓN Y ESTADO GLOBAL
───────────────────────────────────────────────────────── */
const API = '/api/v1';

const state = {
  allProducts:  [],
  currentFilter: 'all',
  cartItems:    [],
  authToken:    localStorage.getItem('cellhub_token') || null,
  currentUser:  JSON.parse(localStorage.getItem('cellhub_user') || 'null'),
};


/* ─────────────────────────────────────────────────────────
   2. HELPERS
───────────────────────────────────────────────────────── */
const BRAND_EMOJI = {
  samsung:  '🌌',
  apple:    '🍎',
  xiaomi:   '⚡',
  motorola: '〽️',
  huawei:   '🔷',
  oppo:     '🟢',
};

function getBrandEmoji(brand) {
  return BRAND_EMOJI[brand.toLowerCase()] || '📱';
}

function formatPrice(price) {
  return '$' + Number(price).toLocaleString('es-CO');
}

function authHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  if (state.authToken) headers['Authorization'] = 'Bearer ' + state.authToken;
  return headers;
}


/* ─────────────────────────────────────────────────────────
   3. AUTENTICACIÓN
───────────────────────────────────────────────────────── */
function setUser(token, user) {
  state.authToken   = token;
  state.currentUser = user;
  localStorage.setItem('cellhub_token', token);
  localStorage.setItem('cellhub_user', JSON.stringify(user));
  updateNavUser();
}

function logout() {
  state.authToken   = null;
  state.currentUser = null;
  state.cartItems   = [];
  localStorage.removeItem('cellhub_token');
  localStorage.removeItem('cellhub_user');
  updateNavUser();
  renderCart();
}

function updateNavUser() {
  const display = document.getElementById('userDisplay');
  const btn     = document.getElementById('authBtn');

  if (state.currentUser) {
    display.textContent = '👤 ' + state.currentUser.username;
    btn.textContent     = 'Salir';
    btn.onclick         = logout;
  } else {
    display.textContent = '';
    btn.textContent     = 'Iniciar sesión';
    btn.onclick         = openAuthModal;
  }
}

function openAuthModal() {
  document.getElementById('authModal').classList.add('open');
}

function closeModal(id) {
  document.getElementById(id).classList.remove('open');
  if (id === 'checkoutModal') resetCheckoutForm();
}

function switchTab(tab) {
  const isLogin = tab === 'login';
  document.getElementById('loginForm').style.display    = isLogin ? '' : 'none';
  document.getElementById('registerForm').style.display = isLogin ? 'none' : '';
  document.getElementById('tabLogin').classList.toggle('active', isLogin);
  document.getElementById('tabRegister').classList.toggle('active', !isLogin);
  document.getElementById('authSubmitBtn').textContent  = isLogin ? 'Iniciar sesión' : 'Crear cuenta';
  document.getElementById('authTitle').textContent      = isLogin ? 'Acceder a CellHub' : 'Crear cuenta';
  document.getElementById('authNote').innerHTML         = isLogin
    ? '¿No tienes cuenta? <a onclick="switchTab(\'register\')">Regístrate gratis</a>'
    : '¿Ya tienes cuenta? <a onclick="switchTab(\'login\')">Inicia sesión</a>';
}

async function submitAuth() {
  const isLogin = document.getElementById('loginForm').style.display !== 'none';
  const btn     = document.getElementById('authSubmitBtn');
  btn.textContent = '⏳ Cargando...';
  btn.disabled    = true;

  try {
    if (isLogin) {
      await handleLogin();
    } else {
      await handleRegister();
    }
  } catch (e) {
    showToast('Error de conexión', false);
  }

  btn.textContent = isLogin ? 'Iniciar sesión' : 'Crear cuenta';
  btn.disabled    = false;
}

async function handleLogin() {
  const res = await fetch(`${API}/users/guest-login/`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: document.getElementById('loginUser').value,
      password: document.getElementById('loginPass').value,
    }),
  });
  const data = await res.json();

  if (!res.ok) {
    showToast(data.error || 'Credenciales incorrectas', false);
    return;
  }

  setUser(data.access, data.user);
  closeModal('authModal');
  showToast('¡Bienvenido, ' + data.user.username + '! 👋');
  await syncCart();
}

async function handleRegister() {
  const res = await fetch(`${API}/users/register/`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username:   document.getElementById('regUser').value,
      email:      document.getElementById('regEmail').value,
      first_name: document.getElementById('regFirst').value,
      last_name:  document.getElementById('regLast').value,
      phone:      document.getElementById('regPhone').value,
      password:   document.getElementById('regPass').value,
      password2:  document.getElementById('regPass2').value,
    }),
  });
  const data = await res.json();

  if (!res.ok) {
    const errors = Object.values(data).flat().join(' ');
    showToast(errors, false);
    return;
  }

  // Auto-login tras registro exitoso
  const loginRes = await fetch(`${API}/users/guest-login/`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: document.getElementById('regUser').value,
      password: document.getElementById('regPass').value,
    }),
  });
  const loginData = await loginRes.json();

  if (loginRes.ok) {
    setUser(loginData.access, loginData.user);
    closeModal('authModal');
    showToast('¡Cuenta creada! Bienvenido 🎉');
  }
}


/* ─────────────────────────────────────────────────────────
   4. PRODUCTOS Y FILTROS
───────────────────────────────────────────────────────── */
async function loadProducts() {
  try {
    const res  = await fetch(`${API}/products/`);
    const data = await res.json();
    state.allProducts = data.results || data;
    renderGrid(state.allProducts);
    if (state.currentUser) await syncCart();
  } catch (e) {
    document.getElementById('grid').innerHTML = `
      <div class="empty-grid">
        ⚠️ No se pudo conectar con la API.<br>
        <small>Corre python seed_data.py primero</small>
      </div>`;
  }
}

function renderGrid(products) {
  if (!products.length) {
    document.getElementById('grid').innerHTML = '<div class="empty-grid">🔍 Sin resultados</div>';
    return;
  }

  document.getElementById('grid').innerHTML = products.map((p, i) => `
    <div class="card" style="animation-delay:${i * .06}s">
      <div class="card-img">
        <span class="os-badge ${p.os === 'ios' ? 'os-ios' : 'os-android'}">
          ${p.os === 'ios' ? 'iOS' : 'Android'}
        </span>
        <span style="filter:drop-shadow(0 0 12px rgba(255,255,255,.1))">
          ${getBrandEmoji(p.brand)}
        </span>
      </div>
      <div class="card-body">
        <div class="card-brand">${p.brand}</div>
        <div class="card-name">${p.model_name}</div>
        <div class="chips">
          <span class="chip">${p.ram_gb}GB RAM</span>
          <span class="chip">${p.storage_gb}GB</span>
          <span class="chip">${p.camera_mp}MP</span>
          <span class="chip">${p.battery_mah}mAh</span>
        </div>
        <div class="card-footer">
          <div class="card-price">
            ${formatPrice(p.price)}
            <small>IVA incluido</small>
          </div>
          <button
            class="add-btn"
            id="addbtn-${p.id}"
            onclick="addToCart(${p.id}, '${p.brand} ${p.model_name}', ${p.price})"
          >+</button>
        </div>
      </div>
    </div>
  `).join('');
}

function setFilter(filter, btn) {
  state.currentFilter = filter;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  applyFilters();
}

function applyFilters() {
  const query = document.getElementById('searchInput').value.toLowerCase();

  let filtered = state.allProducts.filter(p =>
    !query ||
    p.brand.toLowerCase().includes(query) ||
    p.model_name.toLowerCase().includes(query)
  );

  const filterMap = {
    android: p => p.os === 'android',
    ios:     p => p.os === 'ios',
    cheap:   p => p.price <= 2000000,
    premium: p => p.price > 3000000,
  };

  if (filterMap[state.currentFilter]) {
    filtered = filtered.filter(filterMap[state.currentFilter]);
  }

  renderGrid(filtered);
}


/* ─────────────────────────────────────────────────────────
   5. CARRITO
───────────────────────────────────────────────────────── */
async function addToCart(productId, name, price) {
  if (!state.authToken) {
    showToast('Inicia sesión para agregar al carrito', false);
    openAuthModal();
    return;
  }

  const btn = document.getElementById('addbtn-' + productId);
  btn.textContent = '⏳';
  btn.disabled    = true;

  try {
    const res  = await fetch(`${API}/cart/add/`, {
      method:  'POST',
      headers: authHeaders(),
      body:    JSON.stringify({ product_id: productId, quantity: 1 }),
    });
    const data = await res.json();

    if (!res.ok) {
      showToast(data.error || 'Error al agregar', false);
    } else {
      state.cartItems = data.cart.items;
      renderCart();
      showToast('✓ ' + name + ' agregado');
      btn.textContent       = '✓';
      btn.style.background  = 'var(--accent3)';
      setTimeout(() => {
        btn.textContent      = '+';
        btn.style.background = '';
        btn.disabled         = false;
      }, 1500);
      return;
    }
  } catch (e) {
    showToast('Error de conexión', false);
  }

  btn.textContent = '+';
  btn.disabled    = false;
}

async function syncCart() {
  if (!state.authToken) return;
  try {
    const res = await fetch(`${API}/cart/summary/`, { headers: authHeaders() });
    if (res.ok) {
      const data      = await res.json();
      state.cartItems = data.items;
      renderCart();
    }
  } catch (e) { /* silencioso */ }
}

async function removeItem(itemId) {
  try {
    const res = await fetch(`${API}/cart/remove/${itemId}/`, {
      method:  'DELETE',
      headers: authHeaders(),
    });
    if (res.ok) {
      state.cartItems = state.cartItems.filter(i => i.id !== itemId);
      renderCart();
    }
  } catch (e) { /* silencioso */ }
}

function renderCart() {
  const total = state.cartItems.reduce((s, i) => s + i.subtotal, 0);
  const count = state.cartItems.reduce((s, i) => s + i.quantity, 0);

  document.getElementById('cartCount').textContent   = count;
  document.getElementById('cartTotal').textContent   = formatPrice(total);
  document.getElementById('checkoutBtn').disabled    = state.cartItems.length === 0;

  const container = document.getElementById('cartItems');

  if (!state.cartItems.length) {
    container.innerHTML = `
      <div class="cart-empty">
        <div class="cart-empty-icon">🛍️</div>
        <p>Tu carrito está vacío</p>
      </div>`;
    return;
  }

  container.innerHTML = state.cartItems.map(item => `
    <div class="ci">
      <div class="ci-emoji">${getBrandEmoji(item.name.split(' ')[0])}</div>
      <div class="ci-info">
        <div class="ci-name">${item.name}</div>
        <div class="ci-price">
          ${item.quantity}x ${formatPrice(item.price)} =
          <strong>${formatPrice(item.subtotal)}</strong>
        </div>
      </div>
      <button class="ci-remove" onclick="removeItem(${item.id})" title="Eliminar">🗑</button>
    </div>
  `).join('');
}

function openCart() {
  document.getElementById('cartOverlay').classList.add('open');
}

function closeCart() {
  document.getElementById('cartOverlay').classList.remove('open');
}

function closeCartOnBg(event) {
  if (event.target === document.getElementById('cartOverlay')) closeCart();
}


/* ─────────────────────────────────────────────────────────
   6. CHECKOUT
───────────────────────────────────────────────────────── */
function resetCheckoutForm() {
  document.getElementById('checkoutBody').innerHTML = `
    <div class="order-summary" id="orderSummary"></div>
    <div class="form-group">
      <label>Nombre completo</label>
      <input id="chkName" type="text" placeholder="Juan Pérez">
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Ciudad</label>
        <input id="chkCity" type="text" placeholder="Bogotá">
      </div>
      <div class="form-group">
        <label>Teléfono</label>
        <input id="chkPhone" type="text" placeholder="3001234567">
      </div>
    </div>
    <div class="form-group">
      <label>Dirección</label>
      <input id="chkStreet" type="text" placeholder="Cra 7 # 32-16, Apto 301">
    </div>
    <div class="form-group">
      <label>Método de pago (demo)</label>
      <select id="chkPayment">
        <option value="credit_card">💳 Tarjeta de Crédito</option>
        <option value="debit_card">🏧 Tarjeta Débito</option>
        <option value="pse">🏦 PSE</option>
        <option value="nequi">📱 Nequi</option>
        <option value="davivienda">🔷 Davivienda</option>
      </select>
    </div>`;

  document.getElementById('checkoutModalInner').querySelector('.modal-head h2').textContent = '📦 Datos de envío';
  const placeBtn      = document.getElementById('placeOrderBtn');
  placeBtn.style.display = '';
  placeBtn.textContent   = '✅ Confirmar compra';
  placeBtn.disabled      = false;
}

function startCheckout() {
  if (!state.authToken)      { openAuthModal(); return; }
  if (!state.cartItems.length) { showToast('Tu carrito está vacío', false); return; }

  resetCheckoutForm();

  // Resumen de la orden
  const rows  = state.cartItems
    .map(i => `
      <div class="order-summary-row">
        <span>${i.name} x${i.quantity}</span>
        <span>${formatPrice(i.subtotal)}</span>
      </div>`)
    .join('');
  const total = state.cartItems.reduce((s, i) => s + i.subtotal, 0);

  document.getElementById('orderSummary').innerHTML =
    rows + `<div class="order-summary-row total"><span>Total</span><span>${formatPrice(total)}</span></div>`;

  if (state.currentUser) {
    document.getElementById('chkName').value = state.currentUser.username;
  }

  closeCart();
  document.getElementById('checkoutModal').classList.add('open');
}

async function placeOrder() {
  const name    = document.getElementById('chkName').value.trim();
  const city    = document.getElementById('chkCity').value.trim();
  const phone   = document.getElementById('chkPhone').value.trim();
  const street  = document.getElementById('chkStreet').value.trim();
  const payment = document.getElementById('chkPayment').value;

  if (!name || !city || !phone || !street) {
    showToast('Completa todos los campos', false);
    return;
  }

  const btn = document.getElementById('placeOrderBtn');
  btn.textContent = '⏳ Procesando...';
  btn.disabled    = true;

  try {
    const res  = await fetch(`${API}/orders/quick-checkout/`, {
      method:  'POST',
      headers: authHeaders(),
      body:    JSON.stringify({ full_name: name, city, phone, street, payment_method: payment }),
    });
    const data = await res.json();

    if (!res.ok) {
      showToast(data.error || 'Error al procesar la orden', false);
    } else {
      showOrderSuccess(data);
      state.cartItems = [];
      renderCart();
      setTimeout(() => closeModal('checkoutModal'), 2500);
    }
  } catch (e) {
    showToast('Error de conexión', false);
  }

  btn.textContent = '✅ Confirmar compra';
  btn.disabled    = false;
}

function showOrderSuccess(data) {
  document.getElementById('checkoutBody').innerHTML = `
    <div class="success-screen">
      <div class="success-icon">🎉</div>
      <div class="success-title">¡Orden creada!</div>
      <div class="success-sub">Tu pedido fue registrado exitosamente</div>
      <div class="order-badge">Orden #${data.order_id}</div>
      <p style="color:var(--muted);font-size:.85rem;margin-bottom:1.5rem">
        Total: <strong style="color:var(--text)">${formatPrice(data.total)}</strong>
      </p>
      <p style="color:var(--muted);font-size:.8rem">
        Puedes ver el detalle completo en el
        <a href="/admin/orders/order/" style="color:var(--accent)">panel de administración →</a>
      </p>
    </div>`;

  document.getElementById('checkoutModalInner').querySelector('.modal-head h2').textContent = '✅ Compra confirmada';
  document.getElementById('placeOrderBtn').style.display = 'none';
}


/* ─────────────────────────────────────────────────────────
   7. TOAST
───────────────────────────────────────────────────────── */
function showToast(message, success = true) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className   = 'toast show' + (success ? '' : ' error');
  setTimeout(() => { toast.className = 'toast'; }, 2800);
}


/* ─────────────────────────────────────────────────────────
   8. INICIALIZACIÓN
───────────────────────────────────────────────────────── */

// Cerrar modales con Escape
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    closeCart();
    closeModal('authModal');
    closeModal('checkoutModal');
  }
});

// Arranque
updateNavUser();
loadProducts();
if (state.currentUser) syncCart();

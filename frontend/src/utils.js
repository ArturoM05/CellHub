export const API = '/api/v1';

export const BRAND_EMOJI = {
  samsung: '🌌',
  apple: '🍎',
  xiaomi: '⚡',
  motorola: '〽️',
  huawei: '🔷',
  oppo: '🟢',
};

export function getBrandEmoji(brand) {
  return BRAND_EMOJI[brand?.toLowerCase()] || '📱';
}

export function formatPrice(price) {
  return '$' + Number(price).toLocaleString('es-CO');
}

export function authHeaders(token) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = 'Bearer ' + token;
  return headers;
}

export async function apiFetch(path, options = {}, token = null) {
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: { ...authHeaders(token), ...options.headers },
  });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

export const FILTER_OPTIONS = [
  { id: 'all', label: 'Todos' },
  { id: 'android', label: 'Android' },
  { id: 'ios', label: 'iOS' },
  { id: 'cheap', label: 'Hasta $2M' },
  { id: 'premium', label: 'Premium' },
];

export const FILTER_MAP = {
  android: (p) => p.os === 'android',
  ios: (p) => p.os === 'ios',
  cheap: (p) => p.price <= 2000000,
  premium: (p) => p.price > 3000000,
};

export const PAYMENT_OPTIONS = [
  { label: '💳 Tarjeta de Crédito', value: 'credit_card' },
  { label: '🏧 Tarjeta Débito', value: 'debit_card' },
  { label: '🏦 PSE', value: 'pse' },
  { label: '📱 Nequi', value: 'nequi' },
  { label: '🔷 Davivienda', value: 'davivienda' },
];

export function loadStoredAuth() {
  try {
    const token = localStorage.getItem('cellhub_token');
    const user = JSON.parse(localStorage.getItem('cellhub_user') || 'null');
    return { token, user };
  } catch {
    return { token: null, user: null };
  }
}

export function saveAuth(token, user) {
  localStorage.setItem('cellhub_token', token);
  localStorage.setItem('cellhub_user', JSON.stringify(user));
}

export function clearAuth() {
  localStorage.removeItem('cellhub_token');
  localStorage.removeItem('cellhub_user');
}

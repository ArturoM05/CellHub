/**
 * AllyServiceDashboard.jsx  — versión proxy
 * ──────────────────────────────────────────
 * Consume /api/v1/ally/info/ en el PROPIO backend Django (proxy),
 * que a su vez llama al servicio del equipo aliado.
 *
 * Ventaja: sin problemas de CORS, sin exponer la IP del aliado
 * directamente en el frontend, y con latencia medida por Django.
 *
 * Úsalo así:
 *   import AllyServiceDashboard from '@/components/AllyServiceDashboard';
 *   <AllyServiceDashboard />
 *
 * En producción EC2, la URL base se toma de la variable de entorno
 * VITE_API_BASE_URL (o vacío = misma origin).
 */

import { useState, useEffect } from "react";

const API_BASE = import.meta.env?.VITE_API_BASE_URL ?? "";
const PROXY_ENDPOINT = `${API_BASE}/api/v1/ally/info/`;

// ── íconos SVG inline ─────────────────────────────────────────────────────
const icons = {
  gamepad: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="6" width="20" height="12" rx="4"/>
      <path d="M6 12h4M8 10v4M15 11h.01M17 13h.01"/>
    </svg>
  ),
  plan: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
      <rect x="9" y="3" width="6" height="4" rx="1"/>
      <path d="M9 12h6M9 16h4"/>
    </svg>
  ),
  sub: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
    </svg>
  ),
  users: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
      <circle cx="9" cy="7" r="4"/>
      <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
    </svg>
  ),
  refresh: (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="23 4 23 10 17 10"/>
      <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
    </svg>
  ),
  link: (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
      <polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
    </svg>
  ),
  warn: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.29 3.86 1.82 18h20.36L13.71 3.86a2 2 0 0 0-3.42 0z"/>
      <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
  ),
  clock: (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
    </svg>
  ),
};

// ── mapeo de campos del summary del aliado → metadata visual ─────────────
const FIELD_META = {
  videojuegos:   { label: "Videojuegos",    icon: "gamepad", color: "#7C6FFF" },
  planes:        { label: "Planes",          icon: "plan",    color: "#F59E0B" },
  suscripciones: { label: "Suscripciones",   icon: "sub",     color: "#10B981" },
  usuarios:      { label: "Usuarios",        icon: "users",   color: "#38BDF8" },
};

// fallback para campos no mapeados
const genericMeta = (key) => ({
  label: key.charAt(0).toUpperCase() + key.slice(1),
  icon: "plan",
  color: "#8B5CF6",
});

// ── componente ────────────────────────────────────────────────────────────
export default function AllyServiceDashboard() {
  const [state, setState] = useState({
    loading: true,
    error: null,
    status: null,      // "ok" | "unreachable" | "timeout" | "error"
    data: null,
    summary: {},
    latency: null,
    fetchedAt: null,
  });

  const fetchAlly = async () => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const res = await fetch(PROXY_ENDPOINT, { headers: { Accept: "application/json" } });
      const json = await res.json();

      setState({
        loading: false,
        error: json.status !== "ok" ? (json.error ?? "Error desconocido") : null,
        status: json.status,
        data: json.data,
        summary: json.summary ?? {},
        latency: json.latency_ms ?? null,
        fetchedAt: json.fetched_at ? new Date(json.fetched_at) : new Date(),
      });
    } catch (err) {
      setState({
        loading: false,
        error: "No se pudo contactar el proxy de Django.",
        status: "unreachable",
        data: null,
        summary: {},
        latency: null,
        fetchedAt: null,
      });
    }
  };

  useEffect(() => { fetchAlly(); }, []);

  const { loading, error, status, data, summary, latency, fetchedAt } = state;

  const summaryCards = Object.entries(summary).map(([key, val]) => ({
    key,
    value: val,
    ...(FIELD_META[key] ?? genericMeta(key)),
  }));

  // ── estilos ──────────────────────────────────────────────────────────────
  const s = {
    wrap: {
      fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
      background: "#0D0D12",
      borderRadius: "14px",
      padding: "22px",
      color: "#E2E8F0",
    },
    header: { display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "18px" },
    headLeft: {},
    titleRow: { display: "flex", alignItems: "center", gap: "8px" },
    pulse: {
      width: "8px", height: "8px", borderRadius: "50%",
      background: error ? "#EF4444" : loading ? "#F59E0B" : "#10B981",
      boxShadow: error ? "0 0 5px #EF4444" : loading ? "0 0 5px #F59E0B" : "0 0 5px #10B981",
      flexShrink: 0,
    },
    title: { margin: 0, fontSize: "15px", fontWeight: 600, color: "#F1F5F9" },
    meta: { display: "flex", alignItems: "center", gap: "12px", marginTop: "5px" },
    metaItem: { display: "flex", alignItems: "center", gap: "4px", fontSize: "11px", color: "#475569" },
    refreshBtn: {
      display: "flex", alignItems: "center", gap: "5px",
      fontSize: "12px", color: "#64748B",
      background: "#16161F", border: "1px solid #1E1E2E",
      borderRadius: "7px", padding: "5px 10px", cursor: "pointer",
      transition: "background 0.15s",
    },
    grid: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fill, minmax(130px, 1fr))",
      gap: "10px",
      marginBottom: "16px",
    },
    card: (color) => ({
      background: "#13131A",
      border: `1px solid ${color}2E`,
      borderRadius: "11px",
      padding: "14px",
      display: "flex",
      flexDirection: "column",
      gap: "10px",
      animation: "fadeUp 0.3s ease both",
      transition: "border-color 0.2s, transform 0.15s",
    }),
    iconWrap: (color) => ({
      width: "34px", height: "34px", borderRadius: "8px",
      background: `${color}18`,
      display: "flex", alignItems: "center", justifyContent: "center",
      color: color,
    }),
    val: { fontSize: "24px", fontWeight: 700, color: "#F1F5F9", lineHeight: 1 },
    lbl: { fontSize: "11px", color: "#64748B", marginTop: "3px" },
    skeleton: (i) => ({
      background: "#16161F",
      borderRadius: "11px",
      height: "96px",
      animation: `shimmer 1.5s ${i * 0.1}s infinite`,
    }),
    errorBox: {
      background: "#1A0D0D", border: "1px solid #7F1D1D",
      borderRadius: "10px", padding: "12px 14px",
      display: "flex", alignItems: "flex-start", gap: "10px",
      fontSize: "13px", color: "#FCA5A5",
    },
    errorTitle: { fontWeight: 600, marginBottom: "3px" },
    raw: {
      background: "#09090F", border: "1px solid #1A1A28",
      borderRadius: "10px", padding: "12px",
    },
    rawLabel: {
      fontSize: "10px", color: "#334155",
      textTransform: "uppercase", letterSpacing: "0.07em",
      marginBottom: "8px",
    },
    rawPre: {
      margin: 0, fontSize: "11px", color: "#637087",
      whiteSpace: "pre-wrap", wordBreak: "break-word",
      maxHeight: "200px", overflowY: "auto",
    },
    urlRow: {
      display: "flex", alignItems: "center", gap: "5px",
      fontSize: "11px", color: "#334155", marginTop: "12px",
    },
  };

  return (
    <div style={s.wrap}>
      <style>{`
        @keyframes shimmer {
          0%   { background: #16161F; }
          50%  { background: #1E1E2E; }
          100% { background: #16161F; }
        }
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(5px); }
          to   { opacity: 1; transform: translateY(0);   }
        }
        .ally-card:hover {
          transform: translateY(-2px) !important;
          border-color: rgba(255,255,255,0.08) !important;
        }
        .refresh-btn:hover { background: #1E1E2E !important; }
      `}</style>

      {/* ── Header ── */}
      <div style={s.header}>
        <div style={s.headLeft}>
          <div style={s.titleRow}>
            <div style={s.pulse} />
            <h3 style={s.title}>Servicio Aliado</h3>
          </div>
          <div style={s.meta}>
            {fetchedAt && (
              <span style={s.metaItem}>
                {icons.clock}
                {fetchedAt.toLocaleTimeString("es-CO")}
              </span>
            )}
            {latency !== null && (
              <span style={s.metaItem}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                {latency} ms
              </span>
            )}
            {status && status !== "ok" && (
              <span style={{ ...s.metaItem, color: "#EF4444" }}>
                {status}
              </span>
            )}
          </div>
        </div>
        <button
          className="refresh-btn"
          style={s.refreshBtn}
          onClick={fetchAlly}
          disabled={loading}
        >
          {icons.refresh}
          {loading ? "Cargando…" : "Actualizar"}
        </button>
      </div>

      {/* ── Skeletons ── */}
      {loading && (
        <div style={s.grid}>
          {[0, 1, 2, 3].map((i) => (
            <div key={i} style={s.skeleton(i)} />
          ))}
        </div>
      )}

      {/* ── Error ── */}
      {!loading && error && (
        <div style={s.errorBox}>
          <div style={{ color: "#F87171", marginTop: "1px" }}>{icons.warn}</div>
          <div>
            <div style={s.errorTitle}>Aliado no disponible</div>
            <div style={{ fontSize: "12px", color: "#F87171" }}>{error}</div>
          </div>
        </div>
      )}

      {/* ── Cards del summary (campos clave normalizados) ── */}
      {!loading && !error && summaryCards.length > 0 && (
        <div style={s.grid}>
          {summaryCards.map((c, i) => (
            <div
              key={c.key}
              className="ally-card"
              style={{ ...s.card(c.color), animationDelay: `${i * 0.07}s` }}
            >
              <div style={s.iconWrap(c.color)}>
                {icons[c.icon] ?? icons.plan}
              </div>
              <div>
                <div style={s.val}>{Number(c.value).toLocaleString("es-CO")}</div>
                <div style={s.lbl}>{c.label}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── JSON crudo (siempre visible cuando hay datos — útil en sustentación) ── */}
      {!loading && data && (
        <div style={s.raw}>
          <div style={s.rawLabel}>Respuesta completa del aliado</div>
          <pre style={s.rawPre}>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}

      {/* ── URL del proxy ── */}
      <div style={s.urlRow}>
        {icons.link}
        vía proxy: {PROXY_ENDPOINT}
      </div>
    </div>
  );
}

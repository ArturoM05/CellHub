import { useState, useEffect } from "react";

const ALLY_URL = "http://34.206.119.120/api/v1/sistema/info/";

// Iconos minimalistas SVG inline
const Icon = ({ name }) => {
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
    link: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
        <polyline points="15 3 21 3 21 9"/>
        <line x1="10" y1="14" x2="21" y2="3"/>
      </svg>
    ),
    refresh: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="23 4 23 10 17 10"/>
        <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
      </svg>
    ),
    warning: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <triangle points="10.29 3.86 1.82 18 22.18 18 13.71 3.86 10.29 3.86"/>
        <path d="M12 9v4M12 17h.01"/>
      </svg>
    ),
  };
  return icons[name] || null;
};

// Mapea las claves del JSON del aliado a cards visuales
// Ajusta los keys según lo que realmente devuelva el endpoint
function parseAllyData(data) {
  if (!data) return [];

  // Intentamos detectar automáticamente los campos numéricos relevantes
  const labelMap = {
    videojuegos: { label: "Videojuegos", icon: "gamepad", color: "#6C63FF" },
    games: { label: "Videojuegos", icon: "gamepad", color: "#6C63FF" },
    planes: { label: "Planes", icon: "plan", color: "#F59E0B" },
    plans: { label: "Planes", icon: "plan", color: "#F59E0B" },
    suscripciones: { label: "Suscripciones", icon: "sub", color: "#10B981" },
    subscriptions: { label: "Suscripciones", icon: "sub", color: "#10B981" },
    usuarios: { label: "Usuarios", icon: "users", color: "#3B82F6" },
    users: { label: "Usuarios", icon: "users", color: "#3B82F6" },
    clientes: { label: "Clientes", icon: "users", color: "#3B82F6" },
  };

  const cards = [];

  const scan = (obj, prefix = "") => {
    for (const [key, val] of Object.entries(obj)) {
      const fullKey = prefix ? `${prefix}.${key}` : key;
      const keyLower = key.toLowerCase();

      if (typeof val === "number") {
        const meta = labelMap[keyLower] || {
          label: key.charAt(0).toUpperCase() + key.slice(1),
          icon: "plan",
          color: "#8B5CF6",
        };
        cards.push({ key: fullKey, value: val, ...meta });
      } else if (typeof val === "object" && val !== null && !Array.isArray(val)) {
        scan(val, fullKey);
      }
    }
  };

  scan(data);
  return cards;
}

export default function AllyServiceDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(ALLY_URL, {
        headers: { Accept: "application/json" },
        // sin credentials para evitar CORS en la mayoría de casos
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const cards = parseAllyData(data);

  const styles = {
    wrapper: {
      fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
      background: "#0F0F13",
      borderRadius: "16px",
      padding: "24px",
      color: "#E2E8F0",
      minHeight: "220px",
    },
    header: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      marginBottom: "20px",
    },
    titleRow: { display: "flex", alignItems: "center", gap: "10px" },
    dot: {
      width: "8px",
      height: "8px",
      borderRadius: "50%",
      background: error ? "#EF4444" : loading ? "#F59E0B" : "#10B981",
      boxShadow: error ? "0 0 6px #EF4444" : loading ? "0 0 6px #F59E0B" : "0 0 6px #10B981",
    },
    title: { fontSize: "15px", fontWeight: "600", color: "#F1F5F9", margin: 0 },
    subtitle: { fontSize: "12px", color: "#64748B", margin: "2px 0 0" },
    badge: {
      fontSize: "11px",
      color: "#94A3B8",
      background: "#1E1E2E",
      border: "1px solid #2D2D3F",
      borderRadius: "6px",
      padding: "4px 8px",
      display: "flex",
      alignItems: "center",
      gap: "5px",
      cursor: "pointer",
    },
    grid: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))",
      gap: "12px",
    },
    card: (color) => ({
      background: "#16161F",
      border: `1px solid ${color}33`,
      borderRadius: "12px",
      padding: "16px",
      display: "flex",
      flexDirection: "column",
      gap: "10px",
      transition: "border-color 0.2s, transform 0.15s",
      cursor: "default",
    }),
    iconBox: (color) => ({
      width: "36px",
      height: "36px",
      borderRadius: "8px",
      background: `${color}20`,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      color: color,
    }),
    cardValue: { fontSize: "26px", fontWeight: "700", color: "#F1F5F9", lineHeight: 1 },
    cardLabel: { fontSize: "12px", color: "#64748B", marginTop: "2px" },
    skeleton: {
      background: "linear-gradient(90deg, #1E1E2E 25%, #252535 50%, #1E1E2E 75%)",
      backgroundSize: "200% 100%",
      animation: "shimmer 1.4s infinite",
      borderRadius: "12px",
      height: "100px",
    },
    errorBox: {
      background: "#1F0F0F",
      border: "1px solid #7F1D1D",
      borderRadius: "10px",
      padding: "14px 16px",
      display: "flex",
      alignItems: "center",
      gap: "10px",
      fontSize: "13px",
      color: "#FCA5A5",
    },
    rawSection: {
      marginTop: "16px",
      background: "#0A0A10",
      border: "1px solid #1E1E2E",
      borderRadius: "10px",
      padding: "12px",
    },
    rawLabel: { fontSize: "11px", color: "#475569", marginBottom: "8px", textTransform: "uppercase", letterSpacing: "0.05em" },
    rawPre: { fontSize: "11px", color: "#7C85A2", margin: 0, overflowX: "auto", whiteSpace: "pre-wrap", wordBreak: "break-word" },
    url: { fontSize: "11px", color: "#475569", marginTop: "12px", display: "flex", alignItems: "center", gap: "5px" },
  };

  return (
    <div style={styles.wrapper}>
      <style>{`
        @keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
        @keyframes fadeIn { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
        .ally-card:hover { border-color: inherit !important; transform: translateY(-2px); }
      `}</style>

      {/* Header */}
      <div style={styles.header}>
        <div>
          <div style={styles.titleRow}>
            <div style={styles.dot} />
            <p style={styles.title}>Servicio Aliado</p>
          </div>
          <p style={styles.subtitle}>
            {lastUpdated
              ? `Actualizado ${lastUpdated.toLocaleTimeString("es-CO")}`
              : "Conectando..."}
          </p>
        </div>
        <button style={styles.badge} onClick={fetchData} disabled={loading}>
          <Icon name="refresh" /> Actualizar
        </button>
      </div>

      {/* Loading skeletons */}
      {loading && (
        <div style={styles.grid}>
          {[1, 2, 3, 4].map((i) => (
            <div key={i} style={styles.skeleton} />
          ))}
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div style={styles.errorBox}>
          <Icon name="warning" />
          <div>
            <div style={{ fontWeight: 600, marginBottom: 2 }}>No se pudo conectar al aliado</div>
            <div style={{ fontSize: "12px", color: "#F87171" }}>{error} — ¿el servidor está encendido?</div>
          </div>
        </div>
      )}

      {/* Cards con datos numéricos detectados automáticamente */}
      {!loading && !error && cards.length > 0 && (
        <div style={styles.grid}>
          {cards.map((c, i) => (
            <div
              key={c.key}
              className="ally-card"
              style={{
                ...styles.card(c.color),
                animation: `fadeIn 0.3s ease ${i * 0.07}s both`,
              }}
            >
              <div style={styles.iconBox(c.color)}>
                <Icon name={c.icon} />
              </div>
              <div>
                <div style={styles.cardValue}>{c.value.toLocaleString("es-CO")}</div>
                <div style={styles.cardLabel}>{c.label}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* JSON crudo — siempre visible para debug y sustentación */}
      {!loading && data && (
        <div style={styles.rawSection}>
          <div style={styles.rawLabel}>Respuesta raw del aliado</div>
          <pre style={styles.rawPre}>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}

      {/* URL de referencia */}
      <div style={styles.url}>
        <Icon name="link" />
        {ALLY_URL}
      </div>
    </div>
  );
}
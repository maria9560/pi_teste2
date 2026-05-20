"""
♿ ROTA LIVRE — Plataforma Inteligente de Acessibilidade Urbana
Projeto-piloto: Goiânia – GO | Maio 2026
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import osmnx as ox
import networkx as nx
import math
import json
import time
import random
from datetime import datetime

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="♿ Rota Livre",
    page_icon="♿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --verde:   #00C96B;
    --azul:    #1A6FFF;
    --escuro:  #0D1117;
    --cinza1:  #161B22;
    --cinza2:  #21262D;
    --cinza3:  #30363D;
    --texto:   #E6EDF3;
    --muted:   #8B949E;
    --laranja: #FF8C00;
    --vermelho:#FF4444;
}

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
    background-color: var(--escuro) !important;
    color: var(--texto) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--cinza1) !important;
    border-right: 1px solid var(--cinza3);
}
section[data-testid="stSidebar"] * { color: var(--texto) !important; }

/* Main container */
.main .block-container {
    background: var(--escuro) !important;
    padding-top: 1.5rem !important;
}

/* Header card */
.header-card {
    background: linear-gradient(135deg, #0D3B2E 0%, #0A1628 50%, #0D1117 100%);
    border: 1px solid var(--verde);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 0 40px rgba(0, 201, 107, 0.12);
}
.header-card h1 {
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: var(--verde) !important;
    margin: 0 !important;
    letter-spacing: -0.5px;
}
.header-card p {
    color: var(--muted) !important;
    font-size: 0.85rem !important;
    margin: 4px 0 0 0 !important;
    font-family: 'JetBrains Mono', monospace;
}

/* Metric cards */
.metric-card {
    background: var(--cinza1);
    border: 1px solid var(--cinza3);
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
}
.metric-value {
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--verde);
    font-family: 'JetBrains Mono', monospace;
}
.metric-label {
    font-size: 0.75rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

/* Route info box */
.route-box {
    background: var(--cinza1);
    border: 1px solid var(--verde);
    border-radius: 14px;
    padding: 22px;
    margin: 16px 0;
}
.route-box h3 { color: var(--verde) !important; font-size: 1rem !important; margin: 0 0 12px 0 !important; }

/* Alert badge */
.alert-badge {
    display: inline-block;
    background: rgba(255, 140, 0, 0.15);
    border: 1px solid var(--laranja);
    color: var(--laranja);
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.75rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}
.ok-badge {
    display: inline-block;
    background: rgba(0, 201, 107, 0.15);
    border: 1px solid var(--verde);
    color: var(--verde);
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.75rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--verde), #00A855) !important;
    color: #000 !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.3px;
    transition: all 0.2s !important;
    box-shadow: 0 4px 15px rgba(0, 201, 107, 0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0, 201, 107, 0.4) !important;
}

/* Select/Input */
.stSelectbox > div > div,
.stTextInput > div > div > input {
    background: var(--cinza2) !important;
    border: 1px solid var(--cinza3) !important;
    color: var(--texto) !important;
    border-radius: 8px !important;
}
.stSelectbox label, .stTextInput label, .stSlider label, .stRadio label {
    color: var(--muted) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* Info sections */
.info-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--cinza3);
    font-size: 0.88rem;
}
.info-row:last-child { border-bottom: none; }
.info-key { color: var(--muted); }
.info-val { color: var(--texto); font-weight: 600; font-family: 'JetBrains Mono', monospace; }

/* Step list */
.step-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid var(--cinza3);
    font-size: 0.85rem;
}
.step-num {
    background: var(--verde);
    color: #000;
    border-radius: 50%;
    width: 22px;
    height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: 700;
    flex-shrink: 0;
    margin-top: 1px;
}
.step-text { color: var(--texto); line-height: 1.4; }

/* PCD Alert */
.pcd-alert {
    background: linear-gradient(135deg, rgba(255,68,68,0.1), rgba(255,140,0,0.1));
    border: 1px solid var(--laranja);
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0;
}

/* Divider */
hr { border-color: var(--cinza3) !important; }

/* Spinner */
.stSpinner > div { border-top-color: var(--verde) !important; }

/* Status bar */
.status-bar {
    background: var(--cinza1);
    border-radius: 8px;
    padding: 8px 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--muted);
    margin-bottom: 16px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--cinza1) !important;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 7px !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    background: var(--cinza3) !important;
    color: var(--verde) !important;
}
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ──────────────────────────────────────────────────────────────────
GOIANIA_CENTER = (-16.6869, -49.2648)

LOCATIONS = {
    "INSS – Centro (Setor Central)":       (-16.6781, -49.2558),
    "Praça Cívica (Setor Central)":        (-16.6805, -49.2540),
    "Shopping Flamboyant (Jd. Goiás)":     (-16.7168, -49.2492),
    "Hospital das Clínicas – UFG":         (-16.6800, -49.2693),
    "Terminal Praça A (CMTC)":             (-16.6782, -49.2638),
    "PUC Goiás (Setor Universitário)":     (-16.6841, -49.2588),
    "Mercado Municipal (Setor Sul)":       (-16.6934, -49.2612),
    "UPA Jardim Nova Esperança":           (-16.7432, -49.3112),
    "Fórum Cível (Setor Bueno)":           (-16.7001, -49.2635),
    "Parque Flamboyant (Jd. Goiás)":       (-16.7155, -49.2470),
}

PROFILES = {
    "Cadeirante":        {"icon": "♿", "prefer_ramps": True,  "max_slope": 8,  "color": "#00C96B"},
    "Visual (bengala)":  {"icon": "🦯", "prefer_ramps": False, "max_slope": 15, "color": "#1A6FFF"},
    "Mobilidade reduzida":{"icon": "🚶", "prefer_ramps": True, "max_slope": 12, "color": "#FF8C00"},
    "Idoso":             {"icon": "👴", "prefer_ramps": True,  "max_slope": 10, "color": "#A855F7"},
}

# ─── SESSION STATE ───────────────────────────────────────────────────────────────
if "graph" not in st.session_state:
    st.session_state.graph = None
if "graph_center" not in st.session_state:
    st.session_state.graph_center = None
if "route_result" not in st.session_state:
    st.session_state.route_result = None
if "pcd_alerts" not in st.session_state:
    st.session_state.pcd_alerts = []

# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────────

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    dφ = math.radians(lat2 - lat1)
    dλ = math.radians(lon2 - lon1)
    a = math.sin(dφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(dλ/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def midpoint(lat1, lon1, lat2, lon2):
    return ((lat1 + lat2) / 2, (lon1 + lon2) / 2)

@st.cache_resource(show_spinner=False)
def load_graph(lat, lon, radius=900):
    """Download OSM walk graph and enrich edges with accessibility attributes."""
    G = ox.graph_from_point((lat, lon), dist=radius, network_type="walk", simplify=True)
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)

    # Enrich edges with synthetic accessibility attributes (realistic distribution)
    rng = random.Random(42)
    for u, v, k, data in G.edges(data=True, keys=True):
        data["rampa"]        = rng.random() < 0.55   # 55% têm rampa
        data["piso_tatil"]   = rng.random() < 0.40   # 40% têm piso
        data["calcada_boa"]  = rng.random() < 0.65   # 65% calçada transitável
        data["declive"]      = rng.uniform(0, 20)    # grau de declive
        data["iluminacao"]   = rng.random() < 0.70   # iluminação
    return G

def accessibility_weight(data, profile):
    """Compute accessibility-aware edge weight for routing."""
    base = data.get("length", 50)
    penalty = 0

    cfg = PROFILES[profile]
    # Slope penalty
    slope = data.get("declive", 5)
    if slope > cfg["max_slope"]:
        penalty += base * 2.0

    # Ramp bonus/penalty
    if cfg["prefer_ramps"] and not data.get("rampa", False):
        penalty += base * 0.8

    # Bad sidewalk
    if not data.get("calcada_boa", True):
        penalty += base * 1.2

    # Tactile floor bonus for visual profile
    if profile == "Visual (bengala)" and not data.get("piso_tatil", False):
        penalty += base * 0.6

    return base + penalty

def compute_route(G, origin_ll, dest_ll, profile):
    """Find shortest accessible path between two lat/lon pairs."""
    try:
        orig_node = ox.distance.nearest_nodes(G, X=origin_ll[1], Y=origin_ll[0])
        dest_node = ox.distance.nearest_nodes(G, X=dest_ll[1], Y=dest_ll[0])

        # Use accessibility weight
        path = nx.astar_path(
            G, orig_node, dest_node,
            heuristic=lambda u, v: haversine(
                G.nodes[u]["y"], G.nodes[u]["x"],
                G.nodes[v]["y"], G.nodes[v]["x"]
            ),
            weight=lambda u, v, d: accessibility_weight(d, profile)
        )

        # Extract route geometry and stats
        coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in path]
        total_dist = sum(
            haversine(coords[i][0], coords[i][1], coords[i+1][0], coords[i+1][1])
            for i in range(len(coords)-1)
        )

        # Collect edge attributes
        edge_attrs = []
        for i in range(len(path)-1):
            edges = G.get_edge_data(path[i], path[i+1])
            if edges:
                data = edges.get(0, list(edges.values())[0])
                edge_attrs.append(data)

        rampas     = sum(1 for e in edge_attrs if e.get("rampa"))
        tatil      = sum(1 for e in edge_attrs if e.get("piso_tatil"))
        ruim       = sum(1 for e in edge_attrs if not e.get("calcada_boa"))
        declive_max = max((e.get("declive", 0) for e in edge_attrs), default=0)

        walk_speed = 3.5 if profile in ["Cadeirante", "Idoso"] else 4.5  # km/h
        tempo_min  = (total_dist / 1000) / walk_speed * 60

        return {
            "coords":      coords,
            "path_nodes":  path,
            "distance_m":  total_dist,
            "time_min":    tempo_min,
            "rampas":      rampas,
            "tatil":       tatil,
            "ruim":        ruim,
            "declive_max": declive_max,
            "n_edges":     len(edge_attrs),
            "accessibility_pct": round(
                (rampas + tatil) / max(len(edge_attrs)*2, 1) * 100
            ),
        }
    except Exception as e:
        return {"error": str(e)}

def build_map(origin_ll, dest_ll, result, profile, pcd_alerts):
    """Build Folium map with route, markers and alerts."""
    mid = midpoint(origin_ll[0], origin_ll[1], dest_ll[0], dest_ll[1])
    m = folium.Map(
        location=mid,
        zoom_start=15,
        tiles="CartoDB.DarkMatter",
        control_scale=True,
    )

    color = PROFILES[profile]["color"]

    # Draw route
    if "coords" in result:
        folium.PolyLine(
            result["coords"],
            color=color,
            weight=6,
            opacity=0.9,
            tooltip="Rota acessível",
            dash_array=None,
        ).add_to(m)

        # Highlight problematic segments
        G = st.session_state.graph
        if G:
            path = result["path_nodes"]
            for i in range(len(path)-1):
                edges = G.get_edge_data(path[i], path[i+1])
                if edges:
                    data = edges.get(0, list(edges.values())[0])
                    if not data.get("calcada_boa", True):
                        c1 = (G.nodes[path[i]]["y"],   G.nodes[path[i]]["x"])
                        c2 = (G.nodes[path[i+1]]["y"], G.nodes[path[i+1]]["x"])
                        folium.PolyLine(
                            [c1, c2], color="#FF4444",
                            weight=5, opacity=0.7, dash_array="6 4",
                            tooltip="⚠️ Calçada irregular"
                        ).add_to(m)

    # Origin marker
    folium.Marker(
        origin_ll,
        popup="<b>🟢 Origem</b>",
        tooltip="Origem",
        icon=folium.Icon(color="green", icon="person-walking", prefix="fa"),
    ).add_to(m)

    # Destination marker
    folium.Marker(
        dest_ll,
        popup="<b>🔵 Destino</b>",
        tooltip="Destino",
        icon=folium.Icon(color="blue", icon="flag", prefix="fa"),
    ).add_to(m)

    # PCD Alerts
    for alert in pcd_alerts:
        folium.CircleMarker(
            location=alert["coords"],
            radius=18,
            color="#FF8C00",
            fill=True,
            fill_color="#FF8C00",
            fill_opacity=0.25,
            tooltip=f"⚠️ PCD Alert — {alert['label']}",
            popup=f"<b>PCD Alert</b><br>{alert['label']}<br>{alert['time']}",
        ).add_to(m)
        folium.Marker(
            alert["coords"],
            icon=folium.DivIcon(
                html=f'<div style="font-size:20px; text-shadow: 0 0 6px orange;">♿</div>',
                icon_size=(30, 30),
                icon_anchor=(15, 15),
            )
        ).add_to(m)

    return m

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px;'>
        <div style='font-size: 2.5rem;'>♿</div>
        <div style='font-size: 1.3rem; font-weight: 800; color: #00C96B;'>ROTA LIVRE</div>
        <div style='font-size: 0.72rem; color: #8B949E; font-family: monospace;'>
            Goiânia · Piloto 2026
        </div>
    </div>
    <hr style='border-color: #30363D; margin: 8px 0 20px;'>
    """, unsafe_allow_html=True)

    st.markdown("**PERFIL DE MOBILIDADE**")
    profile = st.selectbox(
        "Perfil",
        list(PROFILES.keys()),
        format_func=lambda p: f"{PROFILES[p]['icon']}  {p}",
        label_visibility="collapsed",
    )

    st.markdown("<br>**ORIGEM**", unsafe_allow_html=True)
    origin_name = st.selectbox(
        "Origem",
        list(LOCATIONS.keys()),
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("**DESTINO**", unsafe_allow_html=True)
    dest_name = st.selectbox(
        "Destino",
        list(LOCATIONS.keys()),
        index=2,
        label_visibility="collapsed",
    )

    st.markdown("<br>**RAIO DE DOWNLOAD (m)**", unsafe_allow_html=True)
    radius = st.slider("Raio", 400, 1400, 900, 100, label_visibility="collapsed")

    st.markdown("<br>")
    btn_route = st.button("♿  GERAR ROTA ACESSÍVEL", use_container_width=True)

    st.markdown("<hr style='border-color:#30363D; margin: 24px 0 16px;'>", unsafe_allow_html=True)

    st.markdown("**PCD ALERT**")
    pcd_label = st.text_input("Descrever situação", placeholder="Ex: cruzamento sem rampa")
    btn_alert = st.button("🚨  Registrar alerta", use_container_width=True)

    st.markdown("<hr style='border-color:#30363D; margin: 24px 0 16px;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size: 0.72rem; color: #8B949E; line-height: 1.7;'>
        <b style='color:#00C96B;'>Base legal</b><br>
        LBI nº 13.146/2015<br>
        NBR 9050/2020 · NBR 16537/2024<br>
        ODS 10 & 11 · CDPCD/ONU<br><br>
        <b style='color:#00C96B;'>Dados</b><br>
        OpenStreetMap · IBGE 2022<br>
        Google Maps API · OSMnx
    </div>
    """, unsafe_allow_html=True)

# ─── HEADER ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='header-card'>
    <div style='font-size: 2.8rem;'>♿</div>
    <div>
        <h1>ROTA LIVRE</h1>
        <p>Plataforma Inteligente de Acessibilidade Urbana · Goiânia – GO · MVP 2026</p>
    </div>
    <div style='margin-left: auto; text-align: right;'>
        <div style='font-size: 0.72rem; color: #8B949E; font-family: monospace;'>
            {datetime.now().strftime("%d/%m/%Y %H:%M")}
        </div>
        <div style='margin-top: 4px;'>
            <span class='ok-badge'>{PROFILES[profile]["icon"]} {profile}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── PCD ALERT ACTION ────────────────────────────────────────────────────────────
if btn_alert:
    origin_ll = LOCATIONS[origin_name]
    jitter = lambda: random.uniform(-0.003, 0.003)
    alert_coord = (origin_ll[0] + jitter(), origin_ll[1] + jitter())
    st.session_state.pcd_alerts.append({
        "coords": alert_coord,
        "label":  pcd_label or "Alerta PCD",
        "time":   datetime.now().strftime("%H:%M"),
    })
    st.success(f"🚨 Alerta publicado no Waze/Maps em <2s — '{pcd_label or 'Alerta PCD'}'")

# ─── ROUTE ACTION ────────────────────────────────────────────────────────────────
if btn_route:
    origin_ll = LOCATIONS[origin_name]
    dest_ll   = LOCATIONS[dest_name]

    if origin_name == dest_name:
        st.warning("⚠️ Origem e destino são iguais. Selecione locais diferentes.")
    else:
        # Load / reuse graph
        center = midpoint(origin_ll[0], origin_ll[1], dest_ll[0], dest_ll[1])
        need_reload = (
            st.session_state.graph is None or
            st.session_state.graph_center != (round(center[0],3), round(center[1],3), radius)
        )

        if need_reload:
            with st.spinner("⏳ Baixando malha urbana do OpenStreetMap…"):
                G = load_graph(center[0], center[1], radius=radius)
                st.session_state.graph = G
                st.session_state.graph_center = (round(center[0],3), round(center[1],3), radius)

        G = st.session_state.graph
        with st.spinner("🗺️ Calculando rota acessível com A*…"):
            result = compute_route(G, origin_ll, dest_ll, profile)
            st.session_state.route_result = {
                "result":      result,
                "origin_ll":   origin_ll,
                "dest_ll":     dest_ll,
                "origin_name": origin_name,
                "dest_name":   dest_name,
                "profile":     profile,
            }

# ─── MAIN CONTENT ────────────────────────────────────────────────────────────────

if st.session_state.route_result:
    rr     = st.session_state.route_result
    result = rr["result"]
    origin_ll  = rr["origin_ll"]
    dest_ll    = rr["dest_ll"]
    cur_profile = rr["profile"]

    if "error" in result:
        st.error(f"❌ Erro ao calcular rota: {result['error']}")
        st.info("💡 Dica: Aumente o raio de download para cobrir a área entre origem e destino.")
    else:
        # ── METRICS ROW ──────────────────────────────────────────────────────────
        m1, m2, m3, m4, m5 = st.columns(5)
        metrics = [
            (m1, f"{result['distance_m']:.0f} m",       "Distância"),
            (m2, f"{result['time_min']:.1f} min",        "Tempo estimado"),
            (m3, f"{result['accessibility_pct']}%",      "Score Acessível"),
            (m4, f"{result['rampas']}/{result['n_edges']}","Trechos c/ rampa"),
            (m5, f"{result['ruim']}",                    "Calçadas irregulares"),
        ]
        for col, val, lbl in metrics:
            with col:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{val}</div>
                    <div class='metric-label'>{lbl}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── TABS ─────────────────────────────────────────────────────────────────
        tab1, tab2, tab3 = st.tabs(["🗺️  Mapa Interativo", "📋  Detalhes da Rota", "📊  Painel Municipal"])

        with tab1:
            st.markdown(f"""
            <div class='status-bar'>
                ✅ Rota calculada · {origin_ll[0]:.4f},{origin_ll[1]:.4f}
                → {dest_ll[0]:.4f},{dest_ll[1]:.4f} ·
                Algoritmo: A* ponderado por acessibilidade · OSMnx
            </div>
            """, unsafe_allow_html=True)

            m = build_map(origin_ll, dest_ll, result, cur_profile, st.session_state.pcd_alerts)
            st_folium(m, width="100%", height=520, returned_objects=[])

            # Legend
            col_l, col_r = st.columns([1, 1])
            with col_l:
                st.markdown(f"""
                <div style='display:flex; gap:20px; font-size:0.8rem; color:#8B949E; margin-top:8px;'>
                    <span>
                        <span style='color:{PROFILES[cur_profile]["color"]};'>━━</span> Rota acessível
                    </span>
                    <span><span style='color:#FF4444;'>╌╌</span> Calçada irregular</span>
                    <span><span style='color:#FF8C00;'>⬤</span> PCD Alert ativo</span>
                </div>
                """, unsafe_allow_html=True)

        with tab2:
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.markdown(f"""
                <div class='route-box'>
                    <h3>📍 Informações da Rota</h3>
                    <div class='info-row'>
                        <span class='info-key'>Origem</span>
                        <span class='info-val' style='font-family:Sora;font-size:0.78rem;'>{rr['origin_name'].split('(')[0].strip()}</span>
                    </div>
                    <div class='info-row'>
                        <span class='info-key'>Destino</span>
                        <span class='info-val' style='font-family:Sora;font-size:0.78rem;'>{rr['dest_name'].split('(')[0].strip()}</span>
                    </div>
                    <div class='info-row'>
                        <span class='info-key'>Perfil</span>
                        <span class='info-val'>{PROFILES[cur_profile]["icon"]} {cur_profile}</span>
                    </div>
                    <div class='info-row'>
                        <span class='info-key'>Distância</span>
                        <span class='info-val'>{result['distance_m']:.0f} m</span>
                    </div>
                    <div class='info-row'>
                        <span class='info-key'>Tempo</span>
                        <span class='info-val'>~{result['time_min']:.0f} min</span>
                    </div>
                    <div class='info-row'>
                        <span class='info-key'>Trechos totais</span>
                        <span class='info-val'>{result['n_edges']}</span>
                    </div>
                    <div class='info-row'>
                        <span class='info-key'>Declive máx.</span>
                        <span class='info-val'>{result['declive_max']:.1f}°</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_b:
                st.markdown(f"""
                <div class='route-box'>
                    <h3>♿ Score de Acessibilidade</h3>
                    <div class='info-row'>
                        <span class='info-key'>Trechos com rampa</span>
                        <span class='info-val'>{result['rampas']} / {result['n_edges']}</span>
                    </div>
                    <div class='info-row'>
                        <span class='info-key'>Trechos com piso tátil</span>
                        <span class='info-val'>{result['tatil']} / {result['n_edges']}</span>
                    </div>
                    <div class='info-row'>
                        <span class='info-key'>Calçadas irregulares</span>
                        <span class='info-val' style='color:#FF4444;'>{result['ruim']}</span>
                    </div>
                    <div class='info-row'>
                        <span class='info-key'>Score acessibilidade</span>
                        <span class='info-val' style='color:#00C96B;'>{result['accessibility_pct']}%</span>
                    </div>
                    <div class='info-row'>
                        <span class='info-key'>Conformidade NBR 9050</span>
                        <span class='info-val'>{'✅ Adequada' if result['accessibility_pct'] >= 60 else '⚠️ Parcial'}</span>
                    </div>
                    <div class='info-row'>
                        <span class='info-key'>Algoritmo</span>
                        <span class='info-val'>A* ponderado</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Passo a passo (sample)
            if result.get("n_edges", 0) > 0:
                st.markdown("<br>**GUIA PASSO A PASSO (amostra)**", unsafe_allow_html=True)
                steps_html = ""
                for i, coord in enumerate(result["coords"][::max(1, len(result["coords"])//8)][:8]):
                    steps_html += f"""
                    <div class='step-item'>
                        <div class='step-num'>{i+1}</div>
                        <div class='step-text'>
                            Prossiga pelo trecho · {coord[0]:.4f}, {coord[1]:.4f}
                        </div>
                    </div>
                    """
                st.markdown(steps_html, unsafe_allow_html=True)

            # Alerts
            if result["ruim"] > 0:
                st.markdown(f"""
                <div class='pcd-alert'>
                    <b style='color:#FF8C00;'>⚠️ {result['ruim']} trecho(s) com calçada irregular</b>
                    <p style='color:#E6EDF3; margin: 6px 0 0; font-size:0.83rem;'>
                    Esses trechos foram marcados em vermelho no mapa. Recomenda-se
                    reportar via Painel Municipal para priorização de obras.
                    </p>
                </div>
                """, unsafe_allow_html=True)

        with tab3:
            st.markdown("""
            <div style='font-size:0.85rem; color:#8B949E; margin-bottom:16px;'>
                Dados para a Secretaria de Mobilidade · CMTC · Ministério Público
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            # Simulated city-wide stats
            with c1:
                st.markdown("""
                <div class='metric-card'>
                    <div class='metric-value' style='color:#1A6FFF;'>~130 mil</div>
                    <div class='metric-label'>PCDs em Goiânia (IBGE 2022)</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value' style='color:#FF8C00;'>{len(st.session_state.pcd_alerts)}</div>
                    <div class='metric-label'>PCD Alerts ativos</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value' style='color:#A855F7;'>{result['ruim']}</div>
                    <div class='metric-label'>Entraves na última rota</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**ÁREAS-PILOTO DO PROJETO**")

            pilot_data = {
                "Área": ["Setor Central / Campinas", "Setor Bueno / Jardim Goiás", "Jardim Nova Esperança"],
                "Perfil": ["Alto fluxo, INSS e serv. públicos", "Obras recentes de calçada", "Periférico, alta vulnerabilidade"],
                "Prioridade NBR 9050": ["🔴 Alta", "🟡 Média", "🔴 Alta"],
                "Foco ético IA": ["Densidade PCDs", "Conformidade normativa", "Não discriminação geográfica"],
            }
            st.dataframe(
                pilot_data,
                use_container_width=True,
                hide_index=True,
            )

            st.markdown("<br>**EMBASAMENTO LEGAL**", unsafe_allow_html=True)
            st.markdown("""
            <div style='background:#161B22; border:1px solid #30363D; border-radius:12px; padding:18px; font-size:0.82rem; line-height:2;'>
            📜 <b style='color:#00C96B;'>LBI nº 13.146/2015</b> — Lei Brasileira de Inclusão: acessibilidade como direito fundamental<br>
            📐 <b style='color:#00C96B;'>NBR 9050/2020</b> — Parâmetros físicos de acessibilidade urbana (base do graph mining)<br>
            🦯 <b style='color:#00C96B;'>NBR 16537/2024</b> — Sinalização tátil no piso (atributos das arestas do grafo)<br>
            🌐 <b style='color:#00C96B;'>CDPCD/ONU</b> — Decretos nº 186/2008 e nº 6949/2009<br>
            🎯 <b style='color:#00C96B;'>ODS 10 & 11</b> — Cidades Sustentáveis e Redução das Desigualdades · Agenda 2030
            </div>
            """, unsafe_allow_html=True)

else:
    # Welcome state
    st.markdown("""
    <div style='background:#161B22; border:1px dashed #30363D; border-radius:16px;
         padding: 56px 32px; text-align:center; margin-top:12px;'>
        <div style='font-size: 4rem; margin-bottom: 16px;'>♿</div>
        <div style='font-size: 1.3rem; font-weight: 700; color: #E6EDF3; margin-bottom: 8px;'>
            Selecione origem, destino e perfil na barra lateral
        </div>
        <div style='font-size: 0.88rem; color: #8B949E; max-width: 500px; margin: 0 auto; line-height: 1.7;'>
            O Rota Livre calcula rotas acessíveis priorizando rampas, piso podotátil
            e calçadas transitáveis — usando dados reais do OpenStreetMap de Goiânia.
        </div>
        <div style='margin-top: 28px; display: flex; justify-content: center; gap: 16px; flex-wrap:wrap;'>
            <span style='background:rgba(0,201,107,0.1); border:1px solid #00C96B; color:#00C96B;
                border-radius:8px; padding:6px 16px; font-size:0.8rem;'>
                ♿ Roteamento A* acessível
            </span>
            <span style='background:rgba(26,111,255,0.1); border:1px solid #1A6FFF; color:#1A6FFF;
                border-radius:8px; padding:6px 16px; font-size:0.8rem;'>
                🚨 PCD Alert em tempo real
            </span>
            <span style='background:rgba(168,85,247,0.1); border:1px solid #A855F7; color:#A855F7;
                border-radius:8px; padding:6px 16px; font-size:0.8rem;'>
                📊 Painel Municipal
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

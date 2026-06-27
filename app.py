import time
import streamlit as st
from relic_ring import RelicRingProtocol

# Page Configuration
st.set_page_config(page_title="Relic Ring Protocol", page_icon="🪐", layout="wide")

# Splash screen plays once per session, on first load only
if "splash_shown" not in st.session_state:
    st.session_state.splash_shown = False

# ──────────────────────────────────────────────────────────────────────────
# CONSOLE THEME — injected CSS
# ──────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

:root {
    --void:        #05070A;
    --panel:       #0B0F14;
    --panel-2:     #0E141B;
    --line:        rgba(94, 234, 212, 0.18);
    --line-strong: rgba(94, 234, 212, 0.45);
    --cyan:        #5EEAD4;
    --cyan-dim:     rgba(94, 234, 212, 0.55);
    --amber:       #F0B429;
    --danger:      #FF5470;
    --green:       #34D399;
    --text:        #C8D6E5;
    --text-dim:    #5A6B7A;
    --text-bright: #EAF6F4;
}

/* ---------- base ---------- */
html, body, [class*="css"]  { font-family: 'JetBrains Mono', monospace; }

.stApp {
    background: var(--void);
    color: var(--text);
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(94,234,212,0.07), transparent),
        repeating-linear-gradient(0deg, rgba(255,255,255,0.012) 0px, rgba(255,255,255,0.012) 1px, transparent 1px, transparent 3px);
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 9999;
    background: linear-gradient(180deg, transparent 0%, rgba(94,234,212,0.035) 50%, transparent 100%);
    background-size: 100% 6px;
    animation: scan 9s linear infinite;
    opacity: 0.5;
}
@keyframes scan { 0% { background-position: 0 0; } 100% { background-position: 0 600px; } }

/* ---------- header / title ---------- */
h1 {
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 800 !important;
    letter-spacing: 0.02em;
    color: var(--text-bright) !important;
    text-shadow: 0 0 18px rgba(94,234,212,0.45), 0 0 2px rgba(94,234,212,0.8);
}

.console-tag {
    display: inline-block;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    color: var(--cyan);
    background: rgba(94,234,212,0.06);
    border: 1px solid var(--line-strong);
    padding: 3px 10px;
    border-radius: 2px;
    margin-bottom: 10px;
    text-transform: uppercase;
}

.console-sub {
    font-size: 0.95rem;
    color: var(--text-dim);
    letter-spacing: 0.04em;
    margin-top: -6px;
}

.signal-rule {
    height: 1px;
    width: 100%;
    margin: 18px 0 22px 0;
    background: linear-gradient(90deg, transparent, var(--cyan-dim) 20%, var(--cyan) 50%, var(--cyan-dim) 80%, transparent);
    background-size: 200% 100%;
    animation: sweep 4.5s linear infinite;
    opacity: 0.8;
}
@keyframes sweep { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

/* ---------- status strip ---------- */
.status-strip {
    display: flex;
    gap: 22px;
    flex-wrap: wrap;
    font-size: 0.74rem;
    letter-spacing: 0.08em;
    color: var(--text-dim);
    margin-bottom: 4px;
    text-transform: uppercase;
}
.status-strip span.live { color: var(--cyan); }
.status-strip .dot {
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--cyan);
    box-shadow: 0 0 8px var(--cyan);
    margin-right: 6px;
    animation: pulse 1.6s ease-in-out infinite;
}
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.35; } }

/* ---------- module headers ---------- */
.module-header {
    font-size: 0.78rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--cyan);
    border-left: 3px solid var(--cyan);
    padding: 4px 10px;
    margin-bottom: 14px;
    background: linear-gradient(90deg, rgba(94,234,212,0.08), transparent);
    animation: fadeSlideIn 0.4s ease;
}
.module-header.amber { color: var(--amber); border-left-color: var(--amber); background: linear-gradient(90deg, rgba(240,180,41,0.09), transparent); }

@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateX(-8px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes popIn {
    0%   { opacity: 0; transform: scale(0.92) translateY(6px); }
    100% { opacity: 1; transform: scale(1) translateY(0); }
}

/* ---------- wizard step indicator ---------- */
.wizard-track {
    display: flex;
    align-items: center;
    gap: 0;
    margin-bottom: 28px;
    animation: fadeIn 0.5s ease;
}
.wizard-step {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
}
.wizard-node {
    width: 30px; height: 30px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
    border: 1px solid var(--line);
    color: var(--text-dim);
    background: var(--panel-2);
    flex-shrink: 0;
    transition: all 0.3s ease;
}
.wizard-node.active {
    border-color: var(--cyan);
    color: var(--void);
    background: var(--cyan);
    box-shadow: 0 0 16px rgba(94,234,212,0.55);
}
.wizard-node.done {
    border-color: var(--cyan);
    color: var(--cyan);
    background: rgba(94,234,212,0.1);
}
.wizard-label {
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-dim);
}
.wizard-label.active { color: var(--text-bright); }
.wizard-connector {
    flex: 1;
    height: 1px;
    background: var(--line);
    margin: 0 4px;
}
.wizard-connector.done { background: var(--cyan); }

/* ---------- streamlit widget overrides ---------- */
div[data-testid="stSelectbox"] label, .stTextInput label {
    color: var(--text-dim) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}
div[data-baseweb="select"] > div {
    background: var(--panel-2) !important;
    border: 1px solid var(--line) !important;
    border-radius: 2px !important;
    color: var(--text-bright) !important;
    font-family: 'JetBrains Mono', monospace !important;
    transition: border-color 0.2s ease;
}
div[data-baseweb="select"] > div:hover { border-color: var(--cyan-dim) !important; }

.stTextInput input {
    background: var(--panel-2) !important;
    border: 1px solid var(--line) !important;
    border-radius: 2px !important;
    color: var(--text-bright) !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stTextInput input:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 1px var(--cyan-dim) !important;
}

/* buttons */
.stButton button {
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-size: 0.78rem !important;
    border-radius: 2px !important;
    border: 1px solid var(--line-strong) !important;
    background: rgba(94,234,212,0.05) !important;
    color: var(--cyan) !important;
    transition: all 0.15s ease;
}
.stButton button:hover {
    background: rgba(94,234,212,0.14) !important;
    border-color: var(--cyan) !important;
    box-shadow: 0 0 14px rgba(94,234,212,0.25);
    color: var(--text-bright) !important;
}
.stButton button[kind="primary"] {
    background: rgba(94,234,212,0.12) !important;
    border-color: var(--cyan) !important;
    color: var(--text-bright) !important;
    box-shadow: 0 0 16px rgba(94,234,212,0.3);
}
.stButton button[kind="primary"]:hover { box-shadow: 0 0 24px rgba(94,234,212,0.5); }

/* ---------- metrics ---------- */
div[data-testid="stMetric"] {
    background: var(--panel-2);
    border: 1px solid var(--line);
    border-radius: 2px;
    padding: 12px 16px;
    animation: popIn 0.35s ease;
}
div[data-testid="stMetricLabel"] {
    color: var(--text-dim) !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}
div[data-testid="stMetricValue"] {
    color: var(--cyan) !important;
    font-family: 'JetBrains Mono', monospace !important;
    text-shadow: 0 0 10px rgba(94,234,212,0.4);
}

/* ---------- alerts ---------- */
div[data-testid="stAlert"] {
    border-radius: 2px !important;
    font-family: 'JetBrains Mono', monospace !important;
    border: 1px solid var(--line) !important;
    background: var(--panel-2) !important;
    animation: fadeSlideIn 0.3s ease;
}

/* ---------- expander ---------- */
div[data-testid="stExpander"] {
    background: var(--panel-2) !important;
    border: 1px solid var(--line) !important;
    border-radius: 2px !important;
    margin-bottom: 8px;
    animation: fadeSlideIn 0.3s ease;
}
div[data-testid="stExpander"] summary {
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--cyan) !important;
    letter-spacing: 0.04em;
}

/* terminal-style readout lines */
.term-line {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.84rem;
    color: var(--text);
    border-left: 2px solid var(--line);
    padding: 3px 10px;
    margin: 4px 0;
}
.term-line .key { color: var(--text-dim); }
.term-line .val { color: var(--cyan); }
.term-line .val.amber { color: var(--amber); }

hr { border-color: var(--line) !important; }
.block-container { padding-top: 2.2rem; }

.telemetry-footer {
    margin-top: 28px;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    color: var(--text-dim);
    text-transform: uppercase;
    text-align: right;
    opacity: 0.7;
}

/* ---------- dialog (popup) styling ---------- */
div[data-testid="stDialog"] div[role="dialog"] {
    background: var(--panel) !important;
    border: 1px solid var(--line-strong) !important;
    box-shadow: 0 0 40px rgba(94,234,212,0.18), 0 0 0 1px rgba(94,234,212,0.06) inset !important;
    animation: popIn 0.28s cubic-bezier(0.2, 0.8, 0.2, 1);
}
div[data-testid="stDialog"] h1,
div[data-testid="stDialog"] h2,
div[data-testid="stDialog"] h3 {
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--text-bright) !important;
    letter-spacing: 0.04em;
}

/* boot-sequence loader lines */
.boot-line {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: var(--cyan);
    padding: 2px 0;
    opacity: 0;
    animation: fadeIn 0.25s ease forwards;
}
.boot-line .ok { color: var(--green); }
.boot-cursor {
    display: inline-block;
    width: 7px; height: 14px;
    background: var(--cyan);
    margin-left: 4px;
    animation: blink 0.9s steps(1) infinite;
    vertical-align: middle;
}
@keyframes blink { 50% { opacity: 0; } }

/* sidebar */
section[data-testid="stSidebar"] {
    background: var(--panel) !important;
    border-right: 1px solid var(--line) !important;
}

/* ════════════════════════════════════════════════════════════════════
   LAUNCH SPLASH — plays once on first load, then reveals the UI
   ════════════════════════════════════════════════════════════════════ */
.launch-splash {
    position: fixed;
    inset: 0;
    z-index: 100000;
    background: var(--void);
    background-image:
        radial-gradient(ellipse 70% 60% at 50% 50%, rgba(94,234,212,0.08), transparent 70%);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    overflow: hidden;
    animation: splashExit 0.6s ease forwards;
    animation-delay: 4.0s;
}
@keyframes splashExit {
    0%   { opacity: 1; visibility: visible; }
    99%  { opacity: 0; visibility: visible; }
    100% { opacity: 0; visibility: hidden; pointer-events: none; }
}

.splash-boot {
    position: absolute;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: var(--cyan);
    text-align: left;
    width: 420px;
    max-width: 86vw;
    animation: bootFadeOut 0.5s ease forwards;
    animation-delay: 2.05s;
}
.splash-boot .line {
    opacity: 0;
    padding: 2px 0;
    letter-spacing: 0.02em;
    animation: lineIn 0.22s ease forwards;
}
.splash-boot .line .ok { color: var(--green); margin-right: 6px; }
.splash-boot .line:nth-child(1) { animation-delay: 0.05s; }
.splash-boot .line:nth-child(2) { animation-delay: 0.32s; }
.splash-boot .line:nth-child(3) { animation-delay: 0.59s; }
.splash-boot .line:nth-child(4) { animation-delay: 0.86s; }
.splash-boot .line:nth-child(5) { animation-delay: 1.13s; }
.splash-boot .line:nth-child(6) { animation-delay: 1.40s; }
.splash-boot .line:nth-child(7) { animation-delay: 1.67s; }
@keyframes lineIn {
    from { opacity: 0; transform: translateY(3px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes bootFadeOut {
    from { opacity: 1; }
    to   { opacity: 0; visibility: hidden; }
}

.splash-logo-wrap {
    position: absolute;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    opacity: 0;
    animation: logoReveal 1.1s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
    animation-delay: 2.1s;
}
.splash-logo-icon {
    font-size: 4.6rem;
    line-height: 1;
    filter: drop-shadow(0 0 26px rgba(94,234,212,0.65));
    animation: logoPulse 1.6s ease-in-out infinite;
    animation-delay: 3.1s;
}
.splash-logo-title {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 800;
    font-size: 1.3rem;
    letter-spacing: 0.16em;
    color: var(--text-bright);
    text-shadow: 0 0 18px rgba(94,234,212,0.5);
}
.splash-logo-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    letter-spacing: 0.22em;
    color: var(--cyan);
    opacity: 0.85;
}
@keyframes logoReveal {
    0%   { opacity: 0; transform: scale(0.7); }
    60%  { opacity: 1; transform: scale(1.04); }
    100% { opacity: 1; transform: scale(1); }
}
@keyframes logoPulse {
    0%, 100% { filter: drop-shadow(0 0 18px rgba(94,234,212,0.5)); transform: scale(1); }
    50%      { filter: drop-shadow(0 0 34px rgba(94,234,212,0.85)); transform: scale(1.05); }
}

.splash-progress-track {
    position: absolute;
    bottom: 14%;
    width: 220px;
    height: 2px;
    background: rgba(94,234,212,0.12);
    border-radius: 2px;
    overflow: hidden;
}
.splash-progress-fill {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, var(--cyan-dim), var(--cyan));
    box-shadow: 0 0 10px rgba(94,234,212,0.6);
    animation: progressFill 4.0s linear forwards;
}
@keyframes progressFill { from { width: 0%; } to { width: 100%; } }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# LAUNCH SPLASH — rendered once per session, before the rest of the UI
# ──────────────────────────────────────────────────────────────────────────
if not st.session_state.splash_shown:
    # Hide the sidebar for the duration of the splash, then reveal it
    # in sync with the splash's own fade-out (splashExit fires at 4.0s,
    # finishes at 4.6s) so it appears only once the splash is fully gone.
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        opacity: 0;
        pointer-events: none;
        animation: sidebarReveal 0.6s ease forwards;
        animation-delay: 4.1s;
    }
    @keyframes sidebarReveal {
        from { opacity: 0; pointer-events: none; }
        to   { opacity: 1; pointer-events: auto; }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="launch-splash">
        <div class="splash-boot">
            <div class="line"><span class="ok">[OK]</span>INITIALIZING RELIC RING KERNEL...</div>
            <div class="line"><span class="ok">[OK]</span>CALIBRATING VOID-DISTANCE SENSORS...</div>
            <div class="line"><span class="ok">[OK]</span>SYNCING ZETA-26 ORBITAL REGISTRY...</div>
            <div class="line"><span class="ok">[OK]</span>LOADING RELAY TOWER FIRMWARE...</div>
            <div class="line"><span class="ok">[OK]</span>VERIFYING CODEX ENCRYPTION TABLES...</div>
            <div class="line"><span class="ok">[OK]</span>ESTABLISHING SECTOR UPLINK...</div>
            <div class="line"><span class="ok">[OK]</span>ALL SYSTEMS NOMINAL.</div>
        </div>
        <div class="splash-logo-wrap">
            <div class="splash-logo-icon">🪐</div>
            <div class="splash-logo-title">THE RELIC RING PROTOCOL</div>
            <div class="splash-logo-sub">ZETA-26 STAR SYSTEM</div>
        </div>
        <div class="splash-progress-track"><div class="splash-progress-fill"></div></div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.splash_shown = True

# LOAD NETWORK
# ──────────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_network():
    return RelicRingProtocol('universe-config.json')

try:
    network = load_network()
except Exception:
    st.error("⚠ CONFIG LOAD FAILURE — check universe-config.json")
    st.stop()


# ──────────────────────────────────────────────────────────────────────────
# NETWORK GRAPH (SVG) — used in the Confirm Path popup
# ──────────────────────────────────────────────────────────────────────────
def build_network_svg(network, path, width=560, height=320, pad=46):
    """
    Renders all active planets at their real x/y positions as a constellation
    graph. Edges within max_void_hop are drawn faintly in the background; the
    computed path is drawn as a bright glowing line on top, with a pulsing
    dot animated along it from origin to destination.
    """
    active_ids = list(network.active_nodes)
    if not active_ids:
        return "<div class='term-line'>NO ACTIVE NODES TO PLOT.</div>"

    xs = [network.planets[pid].x for pid in active_ids]
    ys = [network.planets[pid].y for pid in active_ids]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = (max_x - min_x) or 1
    span_y = (max_y - min_y) or 1

    def project(px, py):
        nx = pad + (px - min_x) / span_x * (width - 2 * pad)
        ny = pad + (py - min_y) / span_y * (height - 2 * pad)
        return nx, ny

    coords = {pid: project(network.planets[pid].x, network.planets[pid].y) for pid in active_ids}
    path_set = set(path or [])
    path_edges = set()
    if path:
        for i in range(len(path) - 1):
            path_edges.add(frozenset((path[i], path[i + 1])))

    svg_parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;height:auto;display:block;">',
        '<defs>',
        '<filter id="nodeGlow" x="-100%" y="-100%" width="300%" height="300%">',
        '<feGaussianBlur stdDeviation="3.2" result="blur"/>',
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
        '</filter>',
        '<filter id="lineGlow" x="-50%" y="-50%" width="200%" height="200%">',
        '<feGaussianBlur stdDeviation="2.4" result="blur"/>',
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
        '</filter>',
        '</defs>',
    ]

    # ---- background constellation: every viable hop between active nodes ----
    for i, p1_id in enumerate(active_ids):
        for p2_id in active_ids[i + 1:]:
            p1, p2 = network.planets[p1_id], network.planets[p2_id]
            dist = network.calculate_void_distance(p1, p2)
            if dist > network.max_void_hop:
                continue
            if frozenset((p1_id, p2_id)) in path_edges:
                continue  # drawn later, on top, highlighted
            x1, y1 = coords[p1_id]
            x2, y2 = coords[p2_id]
            svg_parts.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="rgba(94,234,212,0.12)" stroke-width="1"/>'
            )

    # ---- highlighted path edges (drawn on top, glowing) ----
    path_point_str = ""
    if path and len(path) > 1:
        pts = [coords[pid] for pid in path]
        path_point_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        svg_parts.append(
            f'<polyline points="{path_point_str}" fill="none" stroke="#5EEAD4" '
            f'stroke-width="2.4" filter="url(#lineGlow)" stroke-linecap="round" '
            f'stroke-dasharray="6 5">'
            f'<animate attributeName="stroke-dashoffset" from="0" to="-22" dur="1.1s" repeatCount="indefinite"/>'
            f'</polyline>'
        )

    # ---- nodes ----
    for pid in active_ids:
        x, y = coords[pid]
        on_path = pid in path_set
        is_endpoint = path and (pid == path[0] or pid == path[-1])

        if is_endpoint:
            fill, r, label_color, label_weight = "#5EEAD4", 7, "#EAF6F4", "700"
        elif on_path:
            fill, r, label_color, label_weight = "#5EEAD4", 5.5, "#C8D6E5", "600"
        else:
            fill, r, label_color, label_weight = "rgba(94,234,212,0.30)", 4, "rgba(200,214,229,0.35)", "400"

        glow = ' filter="url(#nodeGlow)"' if on_path else ""
        svg_parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"{glow}/>')
        svg_parts.append(
            f'<text x="{x:.1f}" y="{y - r - 7:.1f}" text-anchor="middle" '
            f'font-family="JetBrains Mono, monospace" font-size="10.5" '
            f'font-weight="{label_weight}" fill="{label_color}" '
            f'letter-spacing="0.5">{pid.upper()}</text>'
        )

    # ---- traveling pulse dot, animated along the full path ----
    if path and len(path) > 1:
        svg_parts.append(
            f'<circle r="4.5" fill="#F0B429" filter="url(#nodeGlow)">'
            f'<animateMotion dur="{max(1.6, 0.9 * (len(path) - 1)):.2f}s" repeatCount="indefinite" '
            f'path="M {path_point_str.replace(" ", " L ")}"/>'
            f'</circle>'
        )

    svg_parts.append('</svg>')
    return "".join(svg_parts)


# ──────────────────────────────────────────────────────────────────────────
# SESSION STATE — WIZARD CONTROL
# ──────────────────────────────────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state.step = 1          # 1=select, 2=confirm, 3=transmit/result
if "draft" not in st.session_state:
    st.session_state.draft = {}        # holds origin/destination/payload during the wizard
if "computed_path" not in st.session_state:
    st.session_state.computed_path = None
if "computed_latency" not in st.session_state:
    st.session_state.computed_latency = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None  # holds the final transmission result for the popup
if "pending_action" not in st.session_state:
    st.session_state.pending_action = None


def reset_wizard():
    st.session_state.step = 1
    st.session_state.draft = {}
    st.session_state.computed_path = None
    st.session_state.computed_latency = None
    st.session_state.last_result = None


# ──────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────
st.markdown('<span class="console-tag">SECTOR: ZETA-26 // RELIC-RING-OPERATOR</span>', unsafe_allow_html=True)
st.title("🪐 THE RELIC RING PROTOCOL")
st.markdown('<div class="console-sub">Zeta-26 Star System — Network Routing Interface</div>', unsafe_allow_html=True)
st.markdown('<div class="signal-rule"></div>', unsafe_allow_html=True)

node_count = len(network.planets) if hasattr(network, "planets") else "—"
active_count = len(network.active_nodes) if hasattr(network, "active_nodes") else "—"
st.markdown(f"""
<div class="status-strip">
    <span><span class="dot"></span><span class="live">LINK: ONLINE</span></span>
    <span>NODES_TOTAL: {node_count}</span>
    <span>NODES_ACTIVE: {active_count}</span>
    <span>PROTOCOL: RELIC-RING v1</span>
    <span>WIZARD_STEP: {st.session_state.step}/3</span>
</div>
""", unsafe_allow_html=True)
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# SIDEBAR — NODE RECOVERY & CHAOS (admin actions, outside the wizard flow)
# ──────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="module-header amber">🛠️ NODE RECOVERY &amp; CHAOS</div>', unsafe_allow_html=True)

    node_to_kill = st.selectbox("DISABLE NODE", ["None"] + list(network.planets.keys()), key="kill_select")
    if st.button("💥 DISABLE NODE", use_container_width=True, key="kill_btn"):
        if node_to_kill != "None":
            st.session_state.pending_action = ("kill", node_to_kill)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    node_to_revive = st.selectbox("REVIVE NODE", ["None"] + list(network.planets.keys()), key="revive_select")
    if st.button("✅ REVIVE NODE", use_container_width=True, key="revive_btn"):
        if node_to_revive != "None":
            st.session_state.pending_action = ("revive", node_to_revive)

    st.markdown('<div class="signal-rule" style="margin:16px 0;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="module-header amber" style="font-size:0.7rem;">⚠️ NETWORK-WIDE OVERRIDE</div>', unsafe_allow_html=True)

    kill_all_col, revive_all_col = st.columns(2)
    with kill_all_col:
        if st.button("🔴 ALL OFFLINE", use_container_width=True, key="kill_all_btn"):
            st.session_state.pending_action = ("kill_all", None)
    with revive_all_col:
        if st.button("🟢 ALL ONLINE", use_container_width=True, key="revive_all_btn"):
            st.session_state.pending_action = ("revive_all", None)


# ──────────────────────────────────────────────────────────────────────────
# POPUP: NODE ACTION CONFIRMATION
# ──────────────────────────────────────────────────────────────────────────
@st.dialog("⚠ CONFIRM NETWORK ACTION")
def confirm_node_action(action, node_id):
    labels = {
        "kill": f"Disable node **{node_id}**?",
        "revive": f"Revive node **{node_id}**?",
        "kill_all": "Disable **ALL** nodes network-wide?",
        "revive_all": "Revive **ALL** nodes network-wide?",
    }
    st.markdown(f'<div class="term-line">{labels[action]}</div>', unsafe_allow_html=True)
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ CONFIRM", use_container_width=True, type="primary"):
            if action == "kill":
                network.kill_node(node_id)
            elif action == "revive":
                network.revive_node(node_id)
            elif action == "kill_all":
                for nid in list(network.planets.keys()):
                    network.kill_node(nid)
            elif action == "revive_all":
                for nid in list(network.planets.keys()):
                    network.revive_node(nid)
            st.session_state.pending_action = None
            st.rerun()
    with c2:
        if st.button("✖ CANCEL", use_container_width=True):
            st.session_state.pending_action = None
            st.rerun()


if st.session_state.pending_action:
    confirm_node_action(*st.session_state.pending_action)


# ──────────────────────────────────────────────────────────────────────────
# WIZARD STEP TRACK (visual indicator)
# ──────────────────────────────────────────────────────────────────────────
def step_node_classes(n):
    if st.session_state.step > n:
        return "wizard-node done", "wizard-label"
    elif st.session_state.step == n:
        return "wizard-node active", "wizard-label active"
    else:
        return "wizard-node", "wizard-label"

n1c, l1c = step_node_classes(1)
n2c, l2c = step_node_classes(2)
n3c, l3c = step_node_classes(3)
conn1 = "wizard-connector done" if st.session_state.step > 1 else "wizard-connector"
conn2 = "wizard-connector done" if st.session_state.step > 2 else "wizard-connector"

st.markdown(f"""
<div class="wizard-track">
    <div class="wizard-step">
        <div class="{n1c}">1</div>
        <div class="{l1c}">SELECT ROUTE</div>
    </div>
    <div class="{conn1}"></div>
    <div class="wizard-step">
        <div class="{n2c}">2</div>
        <div class="{l2c}">CONFIRM PATH</div>
    </div>
    <div class="{conn2}"></div>
    <div class="wizard-step">
        <div class="{n3c}">3</div>
        <div class="{l3c}">TRANSMIT</div>
    </div>
</div>
""", unsafe_allow_html=True)

planets = list(network.active_nodes)

if len(planets) < 2:
    st.error("❌ NOT ENOUGH ACTIVE NODES TO ROUTE A TRANSMISSION.")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────
# STEP 1 — SELECT ROUTE
# ──────────────────────────────────────────────────────────────────────────
if st.session_state.step == 1:
    st.markdown('<div class="module-header">📡 TRANSMISSION CONTROL</div>', unsafe_allow_html=True)

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        origin = st.selectbox("ORIGIN PLANET", planets, index=0, key="sel_origin")
    with row1_col2:
        destination = st.selectbox("DESTINATION PLANET", planets, index=len(planets) - 1, key="sel_destination")

    payload = st.text_input("MESSAGE PAYLOAD", "Hello world", key="sel_payload")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    next_btn = st.button("CALCULATE ROUTE →", use_container_width=True, type="primary")

    if next_btn:
        if origin == destination:
            st.warning("⚠ ORIGIN AND DESTINATION CANNOT MATCH.")
        else:
            path, total_latency = network.get_shortest_path(origin, destination)
            if not path:
                st.error("❌ ROUTE UNDELIVERABLE — no valid path found between these nodes.")
            else:
                st.session_state.draft = {"origin": origin, "destination": destination, "payload": payload}
                st.session_state.computed_path = path
                st.session_state.computed_latency = total_latency
                st.session_state.step = 2
                st.rerun()

# ──────────────────────────────────────────────────────────────────────────
# STEP 2 — CONFIRM PATH (popup)
# ──────────────────────────────────────────────────────────────────────────
@st.dialog("📊 CONFIRM TRANSMISSION ROUTE")
def confirm_route_dialog():
    draft = st.session_state.draft
    path = st.session_state.computed_path
    latency = st.session_state.computed_latency

    st.markdown(f'<div class="term-line"><span class="key">ROUTE:</span> <span class="val">{" ➔ ".join(path)}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="module-header" style="font-size:0.68rem;margin-top:14px;">🛰️ NETWORK TRACE</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="border:1px solid var(--line);border-radius:2px;background:var(--panel-2);padding:10px;">'
        f'{build_network_svg(network, path)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:0.65rem;color:var(--text-dim);letter-spacing:0.06em;margin:6px 0 14px 0;">'
        '● BRIGHT NODES = ACTIVE ROUTE &nbsp;&nbsp; ○ DIM NODES = OTHER ACTIVE PLANETS &nbsp;&nbsp; '
        '🟡 PULSE = PAYLOAD IN TRANSIT</div>',
        unsafe_allow_html=True,
    )

    mc1, mc2 = st.columns(2)
    mc1.metric("TOTAL LATENCY (S)", f"{latency:.4f}")
    mc2.metric("TOTAL HOPS", len(path) - 1)

    st.markdown(f'<div class="term-line"><span class="key">PAYLOAD:</span> <span class="val">\'{draft["payload"]}\'</span></div>', unsafe_allow_html=True)
    st.write("")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 PROCEED TO TRANSMIT", use_container_width=True, type="primary"):
            st.session_state.step = 3
            st.rerun()
    with c2:
        if st.button("← BACK TO SELECTION", use_container_width=True):
            st.session_state.step = 1
            st.session_state.computed_path = None
            st.session_state.computed_latency = None
            st.rerun()


if st.session_state.step == 2:
    confirm_route_dialog()
    st.info("Route calculated — use the buttons inside the popup to continue, or reopen it below.")
    if st.button("REOPEN CONFIRMATION"):
        st.rerun()

# ──────────────────────────────────────────────────────────────────────────
# STEP 3 — TRANSMIT (loading sequence → result popup)
# ──────────────────────────────────────────────────────────────────────────
@st.dialog("🎉 TRANSMISSION RESULT")
def result_dialog():
    result = st.session_state.last_result
    if result is None:
        st.error("No transmission result available.")
        if st.button("CLOSE"):
            reset_wizard()
            st.rerun()
        return

    st.success(f"✅ PAYLOAD DELIVERED TO {result['destination'].upper()}")

    mc1, mc2 = st.columns(2)
    mc1.metric("TOTAL LATENCY (S)", f"{result['latency']:.4f}")
    mc2.metric("TOTAL HOPS", len(result['path']) - 1)

    st.markdown(f'<div class="term-line"><span class="key">ROUTE:</span> <span class="val">{" ➔ ".join(result["path"])}</span></div>', unsafe_allow_html=True)
    st.write("")

    st.markdown("**🔍 HOP BREAKDOWN**")
    for i, hop in enumerate(result["hops"]):
        with st.expander(f"HOP {i+1:02d} :: {hop['from']} ➔ {hop['to']}", expanded=False):
            st.markdown(f"""
            <div class="term-line"><span class="key">INTERNAL ASCII ({hop['from']}):</span> <span class="val">{hop['ascii']}</span></div>
            <div class="term-line"><span class="key">NEXT HOP CODEX (BASE {hop['codex']}):</span> <span class="val amber">{hop['encoded']}</span></div>
            <div class="term-line"><span class="key">VOID DISTANCE:</span> <span class="val">{hop['dist']:,.2f} km</span></div>
            """, unsafe_allow_html=True)

    st.markdown(
        f'<div class="telemetry-footer">SECTOR_PORT: 0x{result["sector_port"]:03d} '
        f'· TELEMETRY_LATENCY: {result["latency"]*1000:.1f}ms · INTEGRITY: 100% SECURE</div>',
        unsafe_allow_html=True
    )
    st.write("")
    if st.button("✖ CLOSE & START NEW TRANSMISSION", use_container_width=True, type="primary"):
        reset_wizard()
        st.rerun()


if st.session_state.step == 3:
    draft = st.session_state.draft
    path = st.session_state.computed_path
    latency = st.session_state.computed_latency

    if st.session_state.last_result is None:
        # ---- Animated boot/loading sequence ----
        st.markdown('<div class="module-header">📡 UPLINK IN PROGRESS</div>', unsafe_allow_html=True)
        boot_box = st.empty()
        progress = st.progress(0)

        boot_messages = [
            "ESTABLISHING UPLINK TO RELIC RING...",
            f"LOCKING SIGNAL ON {draft['origin'].upper()}...",
            "ENCODING PAYLOAD FOR VOID TRANSIT...",
            "ROUTING THROUGH RELAY TOWERS...",
            "BEAMING ACROSS VOID DISTANCE...",
            f"DECODING AT {draft['destination'].upper()}...",
            "VERIFYING PACKET INTEGRITY...",
        ]

        lines_html = ""
        for idx, msg in enumerate(boot_messages):
            lines_html += f'<div class="boot-line ok">[OK] {msg}</div>'
            boot_box.markdown(lines_html + '<span class="boot-cursor"></span>', unsafe_allow_html=True)
            progress.progress(int((idx + 1) / len(boot_messages) * 100))
            time.sleep(0.35)

        # ---- Build the full result payload ----
        hops = []
        for i in range(len(path) - 1):
            current_id = path[i]
            next_id = path[i + 1]
            current_planet = network.planets[current_id]
            next_planet = network.planets[next_id]
            ascii_payload = [ord(c) for c in draft["payload"]]
            encoded_payload = network.encode_payload(draft["payload"], next_planet.codex)
            dist = network.calculate_void_distance(current_planet, next_planet)
            hops.append({
                "from": current_id, "to": next_id,
                "ascii": ascii_payload, "encoded": encoded_payload,
                "codex": next_planet.codex, "dist": dist,
            })

        st.session_state.last_result = {
            "path": path,
            "latency": latency,
            "destination": draft["destination"],
            "hops": hops,
            "sector_port": abs(hash(draft["origin"] + draft["destination"])) % 999,
        }
        st.rerun()
    else:
        result_dialog()
        st.info("Transmission complete — use the button inside the popup to start a new one, or reopen it below.")
        if st.button("REOPEN RESULT"):
            st.rerun()
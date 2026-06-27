# 🪐 The Relic Ring Protocol

A Streamlit network-routing simulator for the Zeta-26 star system. Plan a transmission between planets, watch Dijkstra's algorithm pick the lowest-latency route across the void, and stress-test the network by knocking nodes offline.

---

## Requirements

- Python 3.9+
- Streamlit **1.31 or newer** (required for `st.dialog`, used for the popup windows)

```bash
pip install streamlit
```

## Files

| File | Purpose |
|---|---|
| `app.py` | The UI — wizard flow, sidebar controls, popups, splash screen, graph |
| `relic_ring.py` | Your routing engine — `RelicRingProtocol`, Dijkstra, latency math, payload encoding |
| `universe-config.json` | Defines the planets (position, radius, codex base, atmosphere, etc.) |

`app.py` only talks to `relic_ring.py` through its existing public methods (`get_shortest_path`, `kill_node`, `revive_node`, `encode_payload`, `calculate_void_distance`). Nothing in the engine was changed.

## Running it

```bash
streamlit run app.py
```

Make sure `relic_ring.py` and `universe-config.json` are in the same folder as `app.py`.

---

## What's in the UI

### Launch splash
Plays once per session on first load (~4.5s): boot-sequence checks scroll in, then the 🪐 logo pulses in with a glowing halo, then everything fades out to reveal the app. The sidebar is hidden and unclickable for the duration and fades in right as the splash clears, so nothing is interactive before the intro finishes. It won't replay on later reruns within the same session — only on a fresh browser session.

### Step 1 — Select Route
Pick an origin planet, a destination planet, and a message payload. "Calculate Route" runs Dijkstra and validates the pair before moving on (rejects same-planet routes and unreachable destinations with an inline error).

### Step 2 — Confirm Path *(popup)*
Opens as a modal dialog showing:
- The computed route, total latency, and hop count
- A **live network graph** (SVG) — every active planet plotted at its real `x`/`y` position from `universe-config.json`. All reachable connections are drawn faintly in the background; your route glows bright cyan on top; an amber dot animates along the path to represent the payload in transit. Non-route planets are dimmed.

From here: **Proceed to Transmit** or **Back to Selection**.

### Step 3 — Transmit
An animated boot-style log plays out the transmission step by step (uplink, encoding, routing, beaming, decoding, verifying), then opens a **result popup** with the full hop-by-hop breakdown — internal ASCII, next-hop codex encoding, and void distance for every leg — plus a delivery confirmation and telemetry footer.

A step tracker at the top (`① → ② → ③`) always shows where you are in the flow.

### Sidebar — Node Recovery & Chaos
Admin/testing controls, separate from the wizard:
- Disable / revive a single node
- **All Offline / All Online** — toggle every node at once
- Every action opens a confirmation popup before it executes — nothing fires immediately

---

## Notes & things worth knowing

- **`st.dialog` version requirement**: if you're on an older Streamlit and see an `AttributeError` for `st.dialog`, upgrade Streamlit — there's no fallback built in for older versions.
- **Splash timing**: tuned to ~4.5s total via CSS `animation-delay` values. If you want it faster/slower, the delays are grouped near the top of the `<style>` block under `LAUNCH SPLASH`.
- **Graph scaling**: the network graph auto-fits to whatever bounding box your planets' coordinates form. Very lopsided coordinate spreads (e.g. one planet far off from the rest) will still render but may look stretched — worth a visual check if you add planets with extreme positions.
- All theming (colors, fonts, glow effects) lives in one CSS block near the top of `app.py` under `:root` — change the `--cyan` / `--amber` / `--void` variables there to retheme everything at once.
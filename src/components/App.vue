<template>
  <!-- Loading screen -->
  <div id="loading">
    <div class="loading-title">Japan Data Viz</div>
    <div class="loading-bar-wrap">
      <div class="loading-bar" id="loading-bar"></div>
    </div>
  </div>

  <!-- Map -->
  <div id="map-container"></div>

  <!-- Header -->
  <div id="header">
    <div class="logo">Japan Data Viz</div>
    <div class="separator"></div>
    <div class="subtitle">deck.gl · MapLibre GL · FlatGeobuf</div>
  </div>

  <!-- Stats -->
  <div id="stats">
    <div class="stat-card">
      <div class="stat-label">都道府県数</div>
      <div class="stat-value" id="stat-count">—</div>
    </div>
  </div>

  <!-- Tooltip -->
  <div id="tooltip"></div>
</template>

<style>
*,
*::before,
*::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

:root {
    --bg: #080c10;
    --panel: rgba(10, 15, 22, 0.85);
    --border: rgba(255, 255, 255, 0.07);
    --accent: #00e5ff;
    --text: #e8edf2;
    --muted: rgba(232, 237, 242, 0.45);
    --font-display: 'Syne', sans-serif;
    --font-mono: 'DM Mono', monospace;
}

html,
body {
    width: 100%;
    height: 100%;
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-display);
    overflow: hidden;
}

#map-container {
    position: fixed;
    inset: 0;
}

canvas {
    outline: none;
}

/* ── Header ─────────────────────────────────── */
#header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 56px;
    display: flex;
    align-items: center;
    padding: 0 24px;
    background: linear-gradient(to bottom, rgba(8, 12, 16, 0.95) 0%, transparent 100%);
    z-index: 100;
    pointer-events: none;
}

#header .logo {
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--accent);
}

#header .separator {
    width: 1px;
    height: 18px;
    background: var(--border);
    margin: 0 16px;
}

#header .subtitle {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 0.08em;
}

/* ── Tooltip ─────────────────────────────────── */
#tooltip {
    position: fixed;
    pointer-events: none;
    z-index: 200;
    background: rgba(8, 12, 16, 0.95);
    border: 1px solid rgba(0, 229, 255, 0.3);
    border-radius: 8px;
    padding: 10px 14px;
    line-height: 1.7;
    backdrop-filter: blur(10px);
    display: none;
}

#tooltip .tt-name {
    font-weight: 700;
    font-size: 13px;
    color: var(--accent);
    margin-bottom: 2px;
}

#tooltip .tt-row {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--muted);
}

/* ── Loading ─────────────────────────────────── */
#loading {
    position: fixed;
    inset: 0;
    background: var(--bg);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 999;
    transition: opacity 0.6s ease;
}

#loading.hidden {
    opacity: 0;
    pointer-events: none;
}

.loading-title {
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 24px;
}

.loading-bar-wrap {
    width: 180px;
    height: 2px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 2px;
    overflow: hidden;
}

.loading-bar {
    height: 100%;
    width: 0%;
    background: var(--accent);
    border-radius: 2px;
    transition: width 0.3s ease;
}

/* ── Stats ─────────────────────────────────── */
#stats {
    position: fixed;
    bottom: 36px;
    right: 20px;
    z-index: 100;
}

.stat-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    min-width: 140px;
}

.stat-label {
    font-family: var(--font-mono);
    font-size: 10px;
    letter-spacing: 0.1em;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 4px;
}

.stat-value {
    font-size: 22px;
    font-weight: 800;
    color: var(--text);
    line-height: 1;
}

.stat-value span {
    font-size: 11px;
    font-weight: 400;
    color: var(--muted);
    margin-left: 4px;
}
</style>

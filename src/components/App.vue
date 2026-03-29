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

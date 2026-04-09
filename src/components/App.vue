<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { geojson } from 'flatgeobuf';
import type { Feature, FeatureCollection } from 'geojson';
import { Deck } from '@deck.gl/core';
import { GeoJsonLayer, ScatterplotLayer } from '@deck.gl/layers';
import { HeatmapLayer } from '@deck.gl/aggregation-layers';
import prefLatLon from '../data/pref_lat_lon.json';
import prefectures from '../data/prefectures.json';
import populationCsv from '../data/total_population_2000_2020.csv?raw';

type PrefectureData = {
  pref_code: string;
  coordinates: [latitude: number, longitude: number]; // データは[lat, lon]順
  population: number; // 万人
};

// ─────────────────────────────────────────────
//  CSV パース → Map<pref_code, Map<year, population>>
// ─────────────────────────────────────────────
function parsePopulationCsv(csv: string): Map<string, Map<number, number>> {
  const lines = csv.trim().split('\n');
  const headers = lines[0].split(',');
  const years = headers.slice(1).map(Number);
  const result = new Map<string, Map<number, number>>();
  for (const line of lines.slice(1)) {
    const cols = line.split(',');
    const code = cols[0].trim();
    const byYear = new Map<number, number>();
    years.forEach((year, i) => byYear.set(year, parseFloat(cols[i + 1])));
    result.set(code, byYear);
  }
  return result;
}

const popData = parsePopulationCsv(populationCsv);

function buildScatterData(year: number): PrefectureData[] {
  return (prefLatLon as { pref_code: string; coordinates: [number, number] }[]).map(p => ({
    pref_code: p.pref_code,
    coordinates: p.coordinates,
    population: popData.get(p.pref_code)?.get(year) ?? 0,
  }));
}

const prefNameByCode = Object.fromEntries(prefectures.map(p => [p.code, p.name]));

// ─────────────────────────────────────────────
//  リアクティブな状態
// ─────────────────────────────────────────────
const loadingProgress = ref(0);
const loadingHidden = ref(false);
const errorMessage = ref('');
const featureCount = ref(0);
const selectedYear = ref(2020);
const tooltipPopulation = ref(0);
const layerMode = ref<'scatter' | 'heatmap'>('scatter');

const tooltipVisible = ref(false);
const tooltipX = ref(0);
const tooltipY = ref(0);
const tooltipName = ref('');

// ─────────────────────────────────────────────
//  FlatGeobuf を読み込み GeoJSON に変換
// ─────────────────────────────────────────────
async function loadFGB(
  url: string,
  onProgress?: (count: number) => void,
): Promise<FeatureCollection> {
  const res = await fetch(url);
  if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

  const features: Feature[] = [];
  let loaded = 0;

  for await (const feature of geojson.deserialize(res.body) as AsyncGenerator<Feature>) {
    features.push(feature);
    loaded++;
    onProgress?.(loaded);
  }

  return { type: 'FeatureCollection', features };
}

// ─────────────────────────────────────────────
//  deck.gl 初期化
// ─────────────────────────────────────────────
function initDeck(): Deck {
  return new Deck({
    initialViewState: {
      longitude: 137.0,
      latitude:  36.5,
      zoom:       5.0,
      pitch:      0,
      bearing:    0,
    },
    controller: true,
    layers: [],
    onHover: ({ object, x, y }) => {
      if (!object?.pref_code) {
        tooltipVisible.value = false;
        return;
      }
      tooltipName.value = prefNameByCode[object.pref_code] ?? object.pref_code;
      tooltipPopulation.value = object.population ?? 0;
      tooltipX.value = x + 14;
      tooltipY.value = y + 14;
      tooltipVisible.value = true;
    },
  });
}

// ─────────────────────────────────────────────
//  GeoJSON レイヤー生成
// ─────────────────────────────────────────────
function buildLayer(data: FeatureCollection): GeoJsonLayer {
  return new GeoJsonLayer({
    id: 'prefectures',
    data,
    filled: true,
    stroked: true,
    getFillColor: [20, 50, 80, 60],
    getLineColor: [0, 229, 255, 200],
    getLineWidth: 800,         // メートル単位
    lineWidthMinPixels: 1,
    lineWidthMaxPixels: 3,
    pickable: true,
    autoHighlight: true,
    highlightColor: [0, 229, 255, 60],
  });
}

function buildScatterLayer(data: PrefectureData[], year: number): ScatterplotLayer<PrefectureData> {
  return new ScatterplotLayer<PrefectureData>({
    id: 'population-scatter',
    data,
    getPosition: d => [d.coordinates[1], d.coordinates[0]], // [lat,lon] → [lon,lat]
    getRadius: d => d.population * 100,
    updateTriggers: { getRadius: year },
    radiusMinPixels: 4,
    radiusMaxPixels: 80,
    getFillColor: [0, 229, 255, 160],
    stroked: true,
    getLineColor: [255, 255, 255, 40],
    lineWidthMinPixels: 1,
    pickable: true,
  });
}

function buildHeatmapLayer(data: PrefectureData[], year: number): HeatmapLayer<PrefectureData> {
  return new HeatmapLayer<PrefectureData>({
    id: 'population-heatmap',
    data,
    getPosition: d => [d.coordinates[1], d.coordinates[0]], // [lat,lon] → [lon,lat]
    getWeight: d => d.population,
    updateTriggers: { getWeight: year },
    radiusPixels: 80,
    intensity: 1,
    threshold: 0.05,
    colorRange: [
      [0, 0, 128, 200],
      [0, 100, 255, 200],
      [0, 229, 255, 200],
      [0, 255, 128, 200],
      [255, 220, 0, 200],
      [255, 60, 0, 220],
    ],
  });
}

let deckgl: Deck | null = null;
let geoLayer: GeoJsonLayer | null = null;

function updateLayers(year: number, mode: 'scatter' | 'heatmap') {
  if (!deckgl || !geoLayer) return;
  const data = buildScatterData(year);
  const popLayer = mode === 'heatmap'
    ? buildHeatmapLayer(data, year)
    : buildScatterLayer(data, year);
  deckgl.setProps({ layers: [geoLayer, popLayer] });
}

onUnmounted(() => {
  deckgl?.finalize();
});

onMounted(async () => {
  deckgl = initDeck();
  try {
    const data = await loadFGB('/geo/neatogeo_prefectures.fgb', (count) => {
      loadingProgress.value = Math.min(count / 47 * 100, 95);
    });

    featureCount.value = data.features.length;
    geoLayer = buildLayer(data);
    updateLayers(selectedYear.value, layerMode.value);

    loadingProgress.value = 100;
    setTimeout(() => { loadingHidden.value = true; }, 400);
  } catch (err) {
    console.error('[FGB] 読み込みエラー:', err);
    errorMessage.value = (err as Error).message;
  }
});

watch([selectedYear, layerMode], ([year, mode]) => {
  updateLayers(year, mode as 'scatter' | 'heatmap');
});
</script>

<template>
  <!-- Loading screen -->
  <div id="loading" :class="{ hidden: loadingHidden }">
    <template v-if="errorMessage">
      <div class="loading-title" style="color:#ff6b35">読み込みに失敗しました</div>
      <div class="error-detail">{{ errorMessage }}</div>
    </template>
    <template v-else>
      <div class="loading-title">Japan Data Viz</div>
      <div class="loading-bar-wrap">
        <div class="loading-bar" :style="{ width: loadingProgress + '%' }"></div>
      </div>
    </template>
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
      <div class="stat-value">
        {{ featureCount > 0 ? featureCount : '—' }}<span v-if="featureCount > 0">都道府県</span>
      </div>
    </div>
  </div>

  <!-- Year slider -->
  <div id="year-control">
    <div class="year-label">{{ selectedYear }}</div>
    <input
      type="range"
      min="2000"
      max="2020"
      step="1"
      v-model.number="selectedYear"
    />
    <div class="year-range-labels"><span>2000</span><span>2020</span></div>
  </div>

  <!-- Layer toggle -->
  <div id="layer-toggle">
    <button
      :class="{ active: layerMode === 'scatter' }"
      @click="layerMode = 'scatter'"
    >散布図</button>
    <button
      :class="{ active: layerMode === 'heatmap' }"
      @click="layerMode = 'heatmap'"
    >ヒートマップ</button>
  </div>

  <!-- Tooltip -->
  <div
    id="tooltip"
    v-show="tooltipVisible"
    :style="{ left: tooltipX + 'px', top: tooltipY + 'px' }"
  >
    <div class="tt-name">{{ tooltipName }}</div>
    <div class="tt-pop">{{ tooltipPopulation.toFixed(1) }} 万人</div>
  </div>
</template>

<style scoped>
#map-container {
    position: fixed;
    inset: 0;
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

.logo {
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--accent);
}

.separator {
    width: 1px;
    height: 18px;
    background: var(--border);
    margin: 0 16px;
}

.subtitle {
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
}

.tt-name {
    font-weight: 700;
    font-size: 13px;
    color: var(--accent);
    margin-bottom: 2px;
}

.tt-pop {
    font-family: var(--font-mono);
    font-size: 12px;
    color: var(--text);
}

/* ── Year control ─────────────────────────────── */
#year-control {
    position: fixed;
    bottom: 36px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 100;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 20px 8px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    text-align: center;
    min-width: 200px;
}

.year-label {
    font-size: 20px;
    font-weight: 800;
    color: var(--accent);
    line-height: 1;
    margin-bottom: 8px;
}

#year-control input[type="range"] {
    width: 100%;
    accent-color: var(--accent);
    cursor: pointer;
}

.year-range-labels {
    display: flex;
    justify-content: space-between;
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--muted);
    margin-top: 2px;
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

.error-detail {
    font-family: var(--font-mono);
    font-size: 12px;
    color: var(--muted);
    margin-top: 12px;
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

/* ── Layer toggle ────────────────────────────── */
#layer-toggle {
    position: fixed;
    top: 70px;
    right: 20px;
    z-index: 100;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

#layer-toggle button {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 16px;
    font-family: var(--font-mono);
    font-size: 12px;
    letter-spacing: 0.06em;
    color: var(--muted);
    cursor: pointer;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    transition: color 0.2s, border-color 0.2s;
}

#layer-toggle button.active {
    color: var(--accent);
    border-color: var(--accent);
}

#layer-toggle button:hover:not(.active) {
    color: var(--text);
}
</style>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { geojson } from 'flatgeobuf';
import type { Feature, FeatureCollection } from 'geojson';
import { Deck } from '@deck.gl/core';
import { GeoJsonLayer, ScatterplotLayer } from '@deck.gl/layers';
import population from '../data/population.json';

type PrefectureData = {
  pref_name: string;
  coordinates: [latitude: number, longitude: number]; // データは[lat, lon]順
  population: number;
};

// ─────────────────────────────────────────────
//  リアクティブな状態
// ─────────────────────────────────────────────
const loadingProgress = ref(0);
const loadingHidden = ref(false);
const errorMessage = ref('');
const featureCount = ref(0);

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
      if (!object) {
        tooltipVisible.value = false;
        return;
      }
      if (!object.pref_name) {
        tooltipVisible.value = false;
        return;
      }
      tooltipName.value = `${object.pref_name} ${object.population}万人`;
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

function buildScatterLayer(data: PrefectureData[]): ScatterplotLayer<PrefectureData> {
  return new ScatterplotLayer<PrefectureData>({
    id: 'population-scatter',
    data,
    getPosition: d => [d.coordinates[1], d.coordinates[0]], // [lat,lon] → [lon,lat]
    getRadius: d => d.population * 50,                       // 人口に比例した半径（m）
    radiusMinPixels: 4,
    radiusMaxPixels: 80,
    getFillColor: d => {
      const t = Math.min(d.population / 6000, 1);
      return [55 + 200 * t, 100 * (1 - t), 255 * (1 - t), 180];
    },
    stroked: true,
    getLineColor: [255, 255, 255, 40],
    lineWidthMinPixels: 1,
    pickable: true,
  });
}

let deckgl: Deck | null = null;

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
    console.log('[FGB] first feature properties:', data.features[0]?.properties);

    deckgl.setProps({ layers: [
      buildLayer(data),
      buildScatterLayer(population as PrefectureData[])
    ] });

    loadingProgress.value = 100;
    setTimeout(() => { loadingHidden.value = true; }, 400);
  } catch (err) {
    console.error('[FGB] 読み込みエラー:', err);
    errorMessage.value = (err as Error).message;
  }
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

  <!-- Tooltip -->
  <div
    id="tooltip"
    v-show="tooltipVisible"
    :style="{ left: tooltipX + 'px', top: tooltipY + 'px' }"
  >
    <div class="tt-name">{{ tooltipName }}</div>
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
</style>

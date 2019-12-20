<template>
  <div id="wrapper">
    <div id="root">
      <div class="map-table-content">
        <div class="map-content">
          <div class="map" ref="map" id="map">

          </div>
        </div>
        <nav
        class="navbar navbar-default table-menu"
        style="margin-bottom: 0px;"
      >
        <div class="container-fluid">
          <p
            class="navbar-text"
            v-cloak
            title="Ilość wszystkich elemetów"
          >Ilość obiektów:
            <span v-text="items.length"></span>
          </p>
          <div class="navbar-form navbar-right">
            <div class="form-group">
              <input type="text" class="form-control"
              placeholder="Wyszukaj" title="wysukiwanie lokalne"
              v-model.trim="searchItemValue"/>
            </div>
          </div>
        </div>
      </nav>
        <!-- {{ $route.params.layerId }} -->
        <FeatureManagerTable
          v-if="items.length > 0"
          ref="table-data"
          :columns="columns"
          :editing="false"
          :items="items"
          :search="searchItemValue"
        />
        <div class="loading-overlay pt-10 pb-10" style="text-align: center;" v-else>
          <div class="loading-indicator mb-10"><h4>{{$i18n.t('default.loading')}}</h4>
          <i class="fa fa-lg fa-spin fa-spinner"></i></div>
        </div>

        <!-- <virtual-table
          style="height: calc(100% - 54px); position: relative;"
          ref="table-data"
          :items="spatialFilteredItems"
          :columns="itemColumns"
          :search="searchItemValue"
          :column-filters="currentColumnFilters"
          :editing="editing"
          @update-filtred-count="updateCount"
          @update-select-item="updateSelectItem"
          ></virtual-table> -->
      </div>
    </div>
  </div>
</template>

<script>
import { fromLonLat } from 'ol/proj';
import Map from 'ol/Map';
import MVT from 'ol/format/MVT';
import VectorTileLayer from 'ol/layer/VectorTile';
import VectorTileSource from 'ol/source/VectorTile';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import XYZ from 'ol/source/XYZ';
import FeatureManagerTable from '@/components/FeatureManagerTable.vue';

export default {
  components: {
    FeatureManagerTable,
  },
  data: () => ({
    columns: [{
      head: true, sortable: true, filter: true,
    }],
    items: [],
    searchItemValue: '',
    tilesError: false,
  }),
  computed: {
    apiUrl() {
      return this.$store.getters.getApiUrl;
    },
    mapCenter() {
      return this.$store.getters.getMapCenter;
    },
    mapZoom() {
      return this.$store.getters.getMapZoom;
    },
    token() {
      return this.$store.getters.getToken;
    },
  },
  methods: {
    getLayerByName(name) {
      return this.map
        .getLayers()
        .getArray()
        .find(l => l.get('name') === name);
    },
  },
  async mounted() {
    const tileSource = new VectorTileSource({
      format: new MVT(),
      url: `${this.apiUrl}/mvt/${this.$route.params.layerId}/{z}/{x}/{y}?token=${this.token}`,
    });

    this.map = new Map({
      target: 'map',
      layers: [
        new TileLayer({
          source: new XYZ({
            url: 'https://{a-c}.tile.openstreetmap.org/{z}/{x}/{y}.png',
          }),
        }),
        new VectorTileLayer({
          name: 'features',
          source: tileSource,
        }),
      ],
      view: new View({
        center: fromLonLat([this.mapCenter.lon, this.mapCenter.lat]),
        zoom: this.mapZoom,
      }),
    });

    const r = await this.$store.dispatch('getLayer', this.$route.params.layerId);
    if (r.status === 200) {
      r.obj.features.forEach((feat) => {
        Object.keys(feat.properties).forEach((el) => {
          this.columns.push({
            key: el, name: el, sortable: true, filter: true,
          });
        });
        const tempItem = {};
        Object.entries(feat.properties).forEach(([k, v]) => {
          tempItem[k] = v;
        });
        this.items.push(tempItem);
      });
    } else {
      this.$alertify.error(this.$i18n.t('default.error'));
    }
  },
};
</script>

<style scoped>
#map{
  width: 100%;
  height: 100%;
}
.map-table-content, .map-content {
  position: relative;
  z-index: 1;
}
</style>

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
          @selectFeatureById="selectFeatureById"
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
      <div class="right-panel padding-0">
        <div class="col-sm-12">
          <div style="display: inline-block; width: 100%;">
              <h4 class="col-sm-7 right-panel__title" v-if="$route.params.layerName">
                <i class="fa fa-map-o title__icon"></i>
                <span class="mvp-red right-panel__name">{{$route.params.layerName}}</span>
              </h4>
              <div class="col-sm-5" style="margin-top: 6px;">
                <div class="btn-group btn-group-sm" role="group"
                  style="float: right; margin-right: -15px;">
                  <div class="btn-group btn-group-sm" role="group">
                    <button type="button" class="btn btn-default dropdown-toggle"
                      data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                      <i class="fa fa-download green icon-hover"></i> <span class="caret"></span>
                    </button>
                    <ul class="dropdown-menu">
                      <li><a>SHP</a></li>
                      <li><a>GEOJSON</a></li>
                      <li><a>XLSX</a></li>
                    </ul>
                  </div>
                  <a class="btn btn-default">
                    <i class="fa fa-upload blue icon-hover"></i>
                  </a>
                  <a class="btn btn-default">
                    <i class="fa fa-cog yellow icon-hover"></i>
                  </a>
                </div>
              </div>
            </div>

            <ul class="nav nav-tabs nav-justified"
              style="margin-left: -15px; width: calc(100% + 30px);">
              <li role="presentation" :class="{active: indexActiveTab === 0}">
                <a href="#" @click="indexActiveTab = 0"><i class="fa fa-bars"></i> Legenda</a>
              </li>
              <li role="presentation"
                :class="{active: indexActiveTab === 1}" v-show="currentFeature">
                <a href="#" @click="indexActiveTab = 1"><i class="fa fa-table"></i> Atrybuty</a>
              </li>
              <li role="presentation"
                :class="{active: indexActiveTab === 2}" v-show="currentFeature">
                <a href="#" @click="indexActiveTab = 2"><i class="fa fa-info"></i> Informacje</a>
              </li>
            </ul>
            <div class="scroll-tab">
              <div v-show="indexActiveTab == 0" class="legend-panel right-sub-panel">
                <div>
                  <div class="baseLayers">
                    <h4>Warstwy podkładowe:</h4>
                    <ul class="list-group">
                      <li class="list-group-item"
                        v-for="name in baseLayers"
                        :key="name"
                        :class="{'activeLayer' : currentBaseLayer == name}"
                        @click="changeBaseLayer(name)"
                      >
                      {{ name }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              <div v-show="indexActiveTab == 1">
                <AttributesPanel
                  v-if="currentFeature"
                  ref="attributes-panel"
                  :fields="currentFeature"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
  </div>
</template>

<script>
import { fromLonLat, get as getProjection } from 'ol/proj';
import GeoJSON from 'ol/format/GeoJSON';
import Map from 'ol/Map';
import MVT from 'ol/format/MVT';
import VectorTileLayer from 'ol/layer/VectorTile';
import VectorTileSource from 'ol/source/VectorTile';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import WMTSCapabilities from 'ol/format/WMTSCapabilities';
import WMTS, { optionsFromCapabilities } from 'ol/source/WMTS';
import XYZ from 'ol/source/XYZ';
import FeatureManagerTable from '@/components/FeatureManagerTable.vue';
import AttributesPanel from '@/components/AttributesPanel.vue';

export default {
  components: {
    AttributesPanel,
    FeatureManagerTable,
  },
  data: () => ({
    baseLayers: ['OpenStreetMap', 'Ortofotomapa'],
    columns: [{
      head: true, sortable: true, filter: true,
    }],
    currentBaseLayer: 'OpenStreetMap',
    currentFeature: undefined,
    indexActiveTab: 0,
    items: [],
    searchItemValue: '',
    tilesError: false,
  }),
  computed: {
    activeLayer() {
      return this.$store.getters.getActiveLayer;
    },
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
    changeBaseLayer(layerName) {
      this.map.getLayers().getArray().forEach((el) => {
        if (el.get('group') === 'baselayers') {
          if (el.get('name') === layerName) {
            el.setVisible(true);
            this.currentBaseLayer = layerName;
          } else {
            el.setVisible(false);
          }
        }
      });
    },
    getLayerByName(name) {
      return this.map
        .getLayers()
        .getArray()
        .find(l => l.get('name') === name);
    },
    initOrtofoto() {
      return new Promise((resolve, reject) => {
        const parser = new WMTSCapabilities();
        fetch('http://mapy.geoportal.gov.pl/wss/service/WMTS/guest/wmts/ORTO?SERVICE=WMTS&REQUEST=GetCapabilities').then(response => response.text()).then((text) => {
          const result = parser.read(text);
          const options = optionsFromCapabilities(result, {
            layer: 'ORTOFOTOMAPA',
            matrixSet: 'EPSG:4326',
          });
          resolve(
            new TileLayer({
              opacity: 1,
              visible: false,
              name: 'Ortofotomapa',
              group: 'baselayers',
              source: new WMTS({
                url: 'http://mapy.geoportal.gov.pl/wss/service/WMTS/guest/wmts/ORTO',
                matrixSet: 'EPSG:4326',
                format: 'image/png',
                projection: getProjection('EPSG:4326'),
                tileGrid: options.tileGrid,
                style: 'default',
                wrapX: true,
              }),
            }),
          );
        }).catch((err) => {
          reject(err);
        });
      });
    },
    selectFeatureById(fid) {
      this.currentFeature = this.activeLayer.features.find(el => el.properties.id === fid);
      const feature = new GeoJSON().readFeature(this.currentFeature, {
        featureProjection: 'EPSG:3857',
        dataProjection: 'EPSG:4326',
      });
      this.map.getView().fit(feature.getGeometry());
      this.indexActiveTab = 1; // change tab in sidepanel
    },
  },
  async mounted() {
    this.map = new Map({
      target: 'map',
      layers: [
        new TileLayer({
          name: 'OpenStreetMap',
          group: 'baselayers',
          source: new XYZ({
            url: 'https://{a-c}.tile.openstreetmap.org/{z}/{x}/{y}.png',
          }),
        }),
      ],
      view: new View({
        center: fromLonLat([this.mapCenter.lon, this.mapCenter.lat]),
        zoom: this.mapZoom,
      }),
    });

    const ortofoto = await this.initOrtofoto();
    this.map.addLayer(ortofoto);
    this.map.addLayer(
      new VectorTileLayer({
        name: 'features',
        source: new VectorTileSource({
          format: new MVT(),
          url: `${this.apiUrl}/mvt/${this.$route.params.layerId}/{z}/{x}/{y}?token=${this.token}`,
        }),
      }),
    );

    const r = await this.$store.dispatch('getLayer', this.$route.params.layerId);
    if (r.status === 200) {
      this.$store.commit('setActiveLayer', r.obj);
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
.activeLayer {
  color: #ffffff;
  background-color: #2b3d4c;
}
.dropdown-menu {
  left: -40px;
}
#map{
  width: 100%;
  height: 100%;
}
.map-table-content, .map-content {
  position: relative;
  z-index: 1;
}
.right-panel__name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: inline-block;
  max-width: calc(100% - 25px);
}
.right-panel__title {
  display: inline-block;
  margin-bottom: 30px;
  line-height: 22px;
  margin-top: 6px;
  padding-left: 0px;
}
.title__icon {
  position: relative;
  top: -3px;
  margin-right: 10px;
}

.scroll-tab {
    overflow: auto;
    height: calc(100vh - 234px);
}

.right-sub-panel {
    width: 100%;
    display: table;
}
.right-sub-panel > div {
    display: table-caption;
}
.right-sub-panel > div > hr {
    margin-top: 0px;
    margin-bottom: 5px;
}
.right-sub-panel .empty-sub-panel {
    background-color: #eee;
    border-color: #eee;
    color: black;
    padding: 15px;
    margin-bottom: 20px;
    border: 1px solid transparent;
    border-radius: 4px;
}
.right-sub-panel .btn.action {
    padding: 0;
}

.attributes-panel .view hr {
    margin-top: 0px;
    margin-bottom: 10px;
}
.attributes-panel .view {
    margin-top: 10px;
}
.attachments-panel .upload {
    display: none;
}
.attachments-panel .thumbnail{
    max-width: 100%;
    margin-bottom: 0px;
}

.attributes-panel .html-preview{
    border-style: dotted;
    border-color: black;
    border-width: 1px;
    padding: 5px;
}

.filter-panel {
    background-color: #eee;
    border-color: #eee;
    color: black;
    padding: 15px;
    margin-bottom: 20px;
    border: 1px solid transparent;
    border-radius: 4px;
}
.filter-panel .form-group:not(:last-child) {
    margin-bottom: 10px;
}
.filter-panel .form-group:last-child {
    margin-bottom: 0px;
}

.filters-panel .condition .control-label {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
</style>

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
          >{{$i18n.t('featureManager.objectsNumber')}}
            <span v-text="items.length"></span>
          </p>
          <div class="navbar-form navbar-right">
            <div class="form-group">
              <input type="text" class="form-control"
              placeholder="Wyszukaj"
              :title="$i18n.t('featureManager.localSearch')"
              v-model.trim="searchItemValue"/>
            </div>
          </div>
          <button type="button" class="btn navbar-btn navbar-right btn-default"
            :class="{'btn-danger' : currentColumnFilters.length > 0,
              'btn-default' : currentColumnFilters.length == 0 }"
            :title="$i18n.t('featureManager.objectsFilter')"
            @click="openColumnFilterDecision"><i class="fa fa-filter"></i>
          </button>
          <button type="button" class="btn navbar-btn navbar-right btn-default"
            :title="$i18n.t('featureManager.addFeature')" @click="addNewFeature">
            <i class="fa fa-plus"></i>
          </button>
        </div>
      </nav>
        <!-- {{ $route.params.layerId }} -->
        <FeatureManagerTable
          v-if="items.length > 0"
          ref="table-data"
          :columns="columns"
          :column-filters="currentColumnFilters"
          :editing="false"
          :items="items"
          :layId="$route.params.layerId"
          :search="searchItemValue"
          @selectFeatureById="selectFeatureById"
        />
        <div class="loading-overlay pt-10 pb-10" style="text-align: center;" v-else>
          <div class="loading-indicator mb-10"><h4>{{$i18n.t('default.loading')}}</h4>
          <i class="fa fa-lg fa-spin fa-spinner"></i></div>
        </div>

        <div class="modal-mask" v-if="columnFilterDecisionDialogView">
          <div class="modal-wrapper">
            <div class="modal-dialog modal-md">
              <div class="modal-content">
                <div class="modal-header">
                  <h4 class="modal-title">{{$i18n.t('featureManager.objectsFilter')}}</h4>
                </div>
                <div class="modal-body">
                  <FiltersPanel
                    ref="column-filters"
                    :columns="columns"
                    v-model="selectedColumnFilters"></FiltersPanel>
                </div>
                <div class="modal-footer">
                  <div class="btn-group btn-group-justified" role="group">
                    <div class="btn-group" role="group">
                      <button type="button" class="btn btn-success"
                        @click="$emit('columnFilterDecision', 'accept')"
                        :disabled="!isFiltersValidated(selectedColumnFilters)">
                          {{$i18n.t('default.save')}}
                        </button>
                    </div>
                    <div class="btn-group" role="group">
                      <button type="button" class="btn btn-danger"
                        @click="$emit('columnFilterDecision', 'clear')">
                        {{$i18n.t('default.clear')}}
                      </button>
                    </div>
                    <div class="btn-group" role="group">
                      <button type="button" class="btn btn-default"
                        @click="$emit('columnFilterDecision', 'cancel')">
                        {{$i18n.t('default.cancel')}}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
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
                    <i class="fa fa-cog yellow icon-hover"></i>
                  </a>
                </div>
              </div>
            </div>

            <ul class="nav nav-tabs nav-justified"
              style="margin-left: -15px; width: calc(100% + 30px);">
              <li role="presentation" :class="{active: indexActiveTab === 0}">
                <a href="#" @click="indexActiveTab = 0">
                  <i class="fa fa-bars"></i> {{$i18n.t('featureManager.legend')}}</a>
              </li>
              <li role="presentation"
                :class="{active: indexActiveTab === 1}" v-show="currentFeature">
                <a href="#" @click="indexActiveTab = 1">
                  <i class="fa fa-table"></i> {{$i18n.t('featureManager.attributes')}}</a>
              </li>
              <li role="presentation"
                :class="{active: indexActiveTab === 2, disabled: !featureAttachments}"
                v-show="currentFeature">
                <a href="#" @click="indexActiveTab = 2">
                  <i class="fa fa-info"></i> {{$i18n.t('featureManager.informations')}}</a>
              </li>
            </ul>
            <div>
              <div v-show="indexActiveTab == 0" class="legend-panel right-sub-panel">
                <div class="scroll-tab">
                  <div class="baseLayers">
                    <h4>{{$i18n.t('default.basemaps')}}:</h4>
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
                <template v-if="!editing">
                  <div class="btn-group btn-group-edit" role="group">
                    <button
                      type="button"
                      class="btn btn-success"
                      @click="editAttributes"
                    >{{$i18n.t('default.edit')}}</button>
                  </div>
                </template>
                <template v-else>
                  <div class="btn-group btn-group-action btn-group-edit" role="group">
                    <button
                      type="button"
                      class="btn btn-success"
                      @click="saveEditing"
                    >{{$i18n.t('default.save')}}</button>
                  </div>
                  <div class="btn-group btn-group-action btn-group-edit" role="group">
                    <button
                      type="button"
                      class="btn btn-default"
                      @click="cancelEditing"
                    >{{$i18n.t('default.cancel')}}</button>
                  </div>
                  <div class="btn-group btn-group-action btn-group-edit" role="group">
                    <button type="button" class="btn btn-danger">
                      {{$i18n.t('default.delete')}}
                    </button>
                  </div>
                </template>

                <div class="scroll-tab">
                  <AttributesPanel
                    v-if="currentFeature"
                    ref="attributes-panel"
                    :editing="editing"
                    :fields="currentFeature"
                  />
                </div>
              </div>
              <div v-show="indexActiveTab == 2">
                <!-- <CommentsPanel
                  ref="comments-panel"
                  @changeDialogVisibility="changeDialogVisibility"
                  :selected-id="$route.params.layerId" /> -->
                <AttachmentsPanel
                  ref="attachments-panel"
                  v-if="currentFeature && Object.keys(featureAttachments).length > 0"
                  :lid="$route.params.layerId"
                  :fid="currentFeature.properties.id" />
              </div>
            </div>
          </div>
        </div>
      </div>
  </div>
</template>

<script>
import _ from 'lodash';
import { fromLonLat, get as getProjection } from 'ol/proj';
import Draw from 'ol/interaction/Draw';
import GeoJSON from 'ol/format/GeoJSON';
import Map from 'ol/Map';
import Modify from 'ol/interaction/Modify';
import MVT from 'ol/format/MVT';
import VectorTileLayer from 'ol/layer/VectorTile';
import VectorTileSource from 'ol/source/VectorTile';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import { Fill, Stroke, Style } from 'ol/style';
import WMTSCapabilities from 'ol/format/WMTSCapabilities';
import WMTS, { optionsFromCapabilities } from 'ol/source/WMTS';
import XYZ from 'ol/source/XYZ';
import FeatureManagerTable from '@/components/FeatureManagerTable.vue';
import AttributesPanel from '@/components/AttributesPanel.vue';
import AttachmentsPanel from '@/components/AttachmentsPanel.vue';
// import CommentsPanel from '@/components/CommentsPanel.vue';
import FiltersPanel from '@/components/FiltersPanel.vue';
import '@/assets/css/feature-manager.css';

export default {
  components: {
    AttachmentsPanel,
    AttributesPanel,
    // CommentsPanel,
    FeatureManagerTable,
    FiltersPanel,
  },
  data: () => ({
    baseLayers: ['OpenStreetMap', 'Ortofotomapa'],
    columnFilterDecisionDialogView: false,
    columns: [{
      head: true, sortable: true, filter: true,
    }],
    currentBaseLayer: 'OpenStreetMap',
    currentColumnFilters: [],
    currentFeature: undefined,
    currentLayerType: undefined,
    draw: undefined,
    editing: false,
    editingDataCopy: undefined,
    indexActiveTab: 0,
    isInfoDialogVisible: false,
    items: [],
    searchItemValue: '',
    selectedColumnFilters: [],
  }),
  computed: {
    activeLayer() {
      return this.$store.getters.getActiveLayer;
    },
    apiUrl() {
      return this.$store.getters.getApiUrl;
    },
    featureAttachments() {
      return this.$store.getters.getFeatureAttachments;
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
    async saveEditing() {
      const fid = this.currentFeature.properties.id;
      const features = this.getLayerByName('featuresVector').getSource().getFeatures();
      const vectorFeature = features.find(el => el.get('id') === fid).clone();
      this.currentFeature.geometry.coordinates = vectorFeature.getGeometry().transform('EPSG:3857', 'EPSG:4326').getCoordinates();
      const payload = {
        body: this.currentFeature,
        lid: this.$route.params.layerId,
        fid,
      };
      this.$alertify.warning(this.$i18n.t('default.editInProgress'));
      const r = await this.$store.dispatch('editFeature', payload);
      if (r.status === 200) {
        this.editingEndOperations();
        this.refreshVectorSource(this.getLayerByName('features'));
        const itemsIdx = this.items.findIndex(el => el.id === fid);
        this.items[itemsIdx] = r.obj.properties;
        this.$refs['table-data'].$recompute('windowItems'); // update table data
        this.$alertify.success(this.$i18n.t('default.editSuccess'));
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    addNewFeature() {
      const source = new VectorSource({ wrapX: false });
      const vector = new VectorLayer({ source });
      this.map.addLayer(vector);
      let drawType;
      if (this.currentLayerType === 'polygon' || this.currentLayerType === 'multipolygon') {
        drawType = 'Polygon';
      } else if (this.currentLayerType === 'linestring') {
        drawType = 'LineString';
      } else {
        drawType = 'Circle';
      }

      const draw = new Draw({
        source,
        type: drawType,
      });
      draw.set('name', 'drawInteraction');
      this.map.addInteraction(draw);
    },
    cancelEditing() {
      this.currentFeature = this.editingDataCopy;
      this.editingEndOperations();
    },
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
    changeDialogVisibility(vis) {
      this.isInfoDialogVisible = vis;
    },
    createModifyInteraction() {
      const modifyInteraction = new Modify({
        source: this.getLayerByName('featuresVector').getSource(),
      });
      modifyInteraction.set('name', 'modifyInteraction');
      modifyInteraction.setActive(false);
      this.map.addInteraction(modifyInteraction);
    },
    createSelectInteraction() {
      let active = true;
      this.map.on('click', (evt) => {
        if (!active || this.isInteractionActive('modifyInteraction')) return;

        const feature = this.map.forEachFeatureAtPixel(evt.pixel,
          feat => feat, {
            hitTolerance: 5,
          });
        this.selectFeature(feature);
      });
      return {
        setActive(value) {
          active = value;
        },
        getActive() {
          return active;
        },
      };
    },
    editAttributes() {
      this.editing = true;
      this.editingDataCopy = JSON.parse(JSON.stringify(this.currentFeature));

      this.getLayerByName('features').setVisible(false);
      this.activeLayer.features.forEach((feature) => {
        const tempFeature = new GeoJSON().readFeature(feature, {
          featureProjection: 'EPSG:3857',
          dataProjection: 'EPSG:4326',
        });
        this.getLayerByName('featuresVector').getSource().addFeature(tempFeature);
      });
      if (!this.getInteractionByName('modifyInteraction')) {
        this.createModifyInteraction();
      }
      this.getLayerByName('featuresVector').setVisible(true);
      this.getInteractionByName('modifyInteraction').setActive(true);
    },
    editingEndOperations() {
      this.getLayerByName('features').setVisible(true);
      this.getInteractionByName('modifyInteraction').setActive(false);
      this.getLayerByName('featuresVector').getSource().clear();
      this.editing = false;
    },
    getInteractionByName(name) {
      return this.map.getInteractions().getArray().find(i => i.get('name') === name);
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
          this.$alertify.error(this.$i18n.t('featureManager.ortoError'));
          reject(err);
        });
      });
    },
    isFiltersValidated(filters) {
      return _.every(filters, filter => filter.operation !== '' && filter.column !== '' && filter.value !== '');
    },
    isInteractionActive(interaction) {
      if (this.getInteractionByName(interaction)
        && this.getInteractionByName(interaction).getActive()) {
        return true;
      }
      return false;
    },
    openColumnFilterDecision() {
      const self = this;

      const handle = (key) => {
        if (key === 'accept') {
          self.currentColumnFilters = JSON.parse(JSON.stringify(self.selectedColumnFilters));

          self.columnFilterDecisionDialogView = false;
          self.$off('columnFilterDecision', handle);
          // self.$emit('update-column-filters');
        } else if (key === 'clear') {
          self.selectedColumnFilters = [];
        } else {
          self.selectedColumnFilters = JSON.parse(JSON.stringify(self.currentColumnFilters));

          self.columnFilterDecisionDialogView = false;
          self.$off('columnFilterDecision', handle);
        }
      };

      self.$on('columnFilterDecision', handle);
      self.columnFilterDecisionDialogView = true;
    },
    refreshVectorSource(layer) {
      const source = layer.getSource();
      source.tileCache.expireCache({});
      source.tileCache.clear();
      source.refresh();
      layer.changed();
    },
    selectFeature(feature) {
      if (feature) {
        const fid = feature.get('id');
        this.selectFeatureById(fid);
        this.$refs['table-data'].getAttachments(fid); // get attachments for feature
        if ('table-data' in this.$refs) {
          this.$refs['table-data'].selectItem(_.find(this.items, o => o.id === fid));
        }
      } else {
        this.$refs['table-data'].clearSelection();
      }
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

    /* const ortofoto = await this.initOrtofoto();
    this.map.addLayer(ortofoto); */

    const featureStyleResponse = await this.$store.dispatch(
      'getLayerStyle', this.$route.params.layerId,
    );
    const featureStyle = featureStyleResponse.obj.style;
    const featureStyleDef = new Style({
      fill: new Fill({
        color: `rgba(${featureStyle['fill-color']})`,
      }),
      stroke: new Stroke({
        color: `rgba(${featureStyle['stroke-color']})`,
        width: `${featureStyle['stroke-width']}`,
      }),
    });
    this.map.addLayer(
      new VectorTileLayer({
        name: 'features',
        preload: 0,
        source: new VectorTileSource({
          cacheSize: 1,
          format: new MVT(),
          url: `${this.apiUrl}/mvt/${this.$route.params.layerId}/{z}/{x}/{y}?token=${this.token}`,
        }),
        style: featureStyleDef,
      }),
    );
    this.map.addLayer(
      new VectorLayer({
        name: 'featuresVector',
        visible: false,
        source: new VectorSource({}),
        style: featureStyleDef,
      }),
    );

    this.createSelectInteraction();

    const r = await this.$store.dispatch('getLayer', this.$route.params.layerId);
    if (r.status === 200) {
      this.$store.commit('setActiveLayer', r.obj);
      Object.keys(r.obj.features[0].properties).forEach((el) => {
        this.columns.push({
          key: el, name: el, sortable: true, filter: true,
        });
      });
      r.obj.features.forEach((feat) => {
        const tempItem = {};
        Object.entries(feat.properties).forEach(([k, v]) => {
          tempItem[k] = v;
        });
        this.items.push(tempItem);
      });
    } else {
      this.$alertify.error(this.$i18n.t('default.error'));
    }

    const res = await this.$store.dispatch('getCurrentSettings', this.$route.params.layerId);
    this.currentLayerType = res.obj.settings.geometry_type.toLowerCase();
    this.$store.commit('setCurrentFeaturesTypes', res.obj.settings.columns);
  },
};
</script>

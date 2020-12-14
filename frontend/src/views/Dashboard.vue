<template>
  <span>
    <div class="mainnav"></div>
    <div class="dashboard content">
      <div class="container">
        <div class="layout layout-stack-sm layout-main-left">
          <!-- TABELA PROJEKTÓW -->
          <div
            v-if="projectsGetting"
            style="border-left: 0; box-shadow:none"
            class="col-sm-4 col-sm-push-8 layout-sidebar projects-panel"
          >
            <div class="loading-indicator mb-10">
              <h4>{{ $i18n.t('default.loading') }}</h4>
              <i class="fa fa-lg fa-spin fa-spinner" />
            </div>
          </div>
          <ProjectsPanel v-else :projects="projects" @deleteProject="deleteProject" />
          <!-- KONIEC TABELI PROJEKTÓW -->
          <!-- TABELA WARSTW -->
          <div style="border-right: 1px solid #ccc" class="col-sm-8 col-sm-pull-4 layout-main">
            <h2 class="flex-center container__border--bottom container__border--grey mb-0">
              <div class="p-0 container__border--bottom container__border--red section__header">
                <i class="fa fa-database" />
                <span data-i18n="dashboard.title">{{ $i18n.t('dashboard.title.layersList') }}</span>
              </div>
              <span class="flex-center">
                <div class="p-0 mr-5">
                  <vSelect
                    v-model="searchTag"
                    class="tagFilter"
                    label="name"
                    style="width: 300px"
                    :placeholder="$i18n.t('dashboard.placeholder.tagsFilter')"
                    :options="tags"
                  >
                    <template v-slot:option="option">
                      <span :style="`color: ${option.color}`">{{ option.name }}</span>
                    </template>
                    <template v-slot:selected-option="option">
                      <span :style="`color: ${option.color}`">{{
                        option.name | maxInputTagLength
                      }}</span>
                    </template>
                    <span slot="no-options">{{ $i18n.t('settings.tagNotFound') }}</span>
                  </vSelect>
                </div>
                <div class="p-0">
                  <input
                    v-model="searchLayer"
                    type="text"
                    class="form-control container__input"
                    :placeholder="$i18n.t('dashboard.placeholder.layersFilter')"
                  />
                </div>
              </span>
            </h2>
            <div
              :style="{ 'padding-bottom': isTagMenuOpen ? '30vh' : '0' }"
              class="section__content heading-block heading-block-main"
            >
              <span class="add-layer">
                <i class="fa fa-plus-circle fa-lg green pt-10" style="margin-right:5px;" />
                <a
                  data-toggle="modal"
                  data-target="#addLayerModal"
                  data-type="vectorLayer"
                  class="green section__content--add"
                  >{{ $i18n.t('dashboard.list.addLayer') }}</a
                >
              </span>
              <span class="add-layer">
                <i class="fa fa-plus-circle fa-lg green pt-10" style="margin-right:5px;" />
                <a
                  data-toggle="modal"
                  data-target="#addLayerWmsModal"
                  data-type="externalLayer"
                  class="green section__content--add"
                  >{{ $i18n.t('dashboard.list.addService') }}</a
                >
              </span>
              <div v-if="!layersAll" class="loading-overlay pt-10 pb-10">
                <div class="loading-indicator mb-10">
                  <h4>{{ $i18n.t('default.loading') }}</h4>
                  <i class="fa fa-lg fa-spin fa-spinner" />
                </div>
              </div>
              <div v-if="filteredLayersAll.length == 0" class="pt-10 pb-10">
                {{ $i18n.t('default.noLayers') }}
              </div>
              <template v-for="(val, key) in filteredLayersAll" v-else>
                <div :key="key" class="mb-0">
                  <div style="padding:9px 15px" class="panel-heading pl-0 pr-0">
                    <h4 class="panel-title flex-center">
                      <span style="display:inherit">
                        <span v-if="val.url" class="panel-title__names">
                          <i style="margin-right:9px" class="icon-li fa fa-link fa-lg" />
                          <span class="bold panel-title__wms">{{ val.name }}</span>
                          <span class="desc-sm" :title="val.url">
                            <strong>URL</strong>
                            :{{ val.url | maxLength }}
                          </span>
                          <span class="desc-sm" :title="val.layers">
                            <strong>{{ $i18n.t('default.layers') }}</strong>
                            : {{ val.layers | maxLength }}
                          </span>
                        </span>
                        <span v-else class="panel-title__names">
                          <i class="icon-li fa fa-map-o fa-lg mr-5" />
                          <span class="bold" href="#" @click="goToManager(val)">{{
                            val.name
                          }}</span>
                          <span class="desc-sm">{{ val.team }}</span>
                        </span>
                        <span v-if="val.tags" style="min-width: 100px">
                          <vSelect
                            taggable
                            multiple
                            class="mySelect"
                            label="name"
                            max-height="10px"
                            :disabled="isTagAddings"
                            :options="tags.filter(t => !val.tags.find(vT => vT.id === t.id))"
                            :value="val.tags"
                            :v-if="tags.length > 0"
                            @input="updateLayerTags(val, $event)"
                            @search:focus="isTagMenuOpen = true"
                            @search:blur="isTagMenuOpen = false"
                          >
                            <template v-slot:option="option">
                              <span
                                :style="`color: ${option.color};width: 50px; overflow:hidden`"
                                :title="option.name"
                                >{{ option.name }}</span
                              >
                            </template>
                            <template v-slot:selected-option="option">
                              <span
                                :style="
                                  `color: ${option.color};max-width: 10vh;overflow:hidden;white-space:nowrap`
                                "
                                :title="option.name"
                                >{{ option.name }}</span
                              >
                            </template>
                            <span slot="no-options">{{ $i18n.t('settings.tagNotFound') }}</span>
                          </vSelect>
                        </span>
                      </span>
                      <span id="layers-list-icons" class="panel-title__tools">
                        <i
                          v-if="!val.url"
                          class="fa fa-cog fa-lg yellow icon-hover"
                          data-toggle="modal"
                          data-target="#layerSettingsModal"
                          data-placement="top"
                          :title="$i18n.t('default.settings')"
                          @click="setEditedLayer('vector', val.id)"
                        />
                        <i
                          class="fa fa-trash fa-lg red icon-hover"
                          data-toggle="tooltip"
                          data-placement="top"
                          :title="$i18n.t('default.delete')"
                          @click="val.url ? deleteService(val.id) : deleteLayer(val)"
                        />
                      </span>
                    </h4>
                  </div>
                </div>
              </template>
            </div>
          </div>
          <!-- KONIEC TABELI WARSTW -->
        </div>
      </div>
    </div>
    <!--MODAL DODAWANIA WARSTW-->
    <div
      id="addLayerModal"
      ref="addLayerModal"
      class="modal fade"
      data-backdrop="static"
      tabindex="-1"
      role="dialog"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">{{ $i18n.t('dashboard.modal.addLayer') }}</h4>
          </div>
          <div class="modal-body">
            <div style="display: flex">
              <label class="control-label col-sm-4 pl-0">{{
                $i18n.t('dashboard.modal.layerName')
              }}</label>
              <input v-model="vectorLayerName" type="text" class="form-control" />
            </div>
            <div
              v-if="vectorLayerName.length > layerMaxNameLength"
              style="display: flex"
              class="pt-5"
            >
              <label class="control-label col-sm-4 pl-0" />
              <span style="color:#bd0f0f; width: 100%">{{
                `Zbyt długa nazwa (maksymalnie ${layerMaxNameLength} znaków)`
              }}</span>
            </div>
            <div style="display: flex" class="pt-10">
              <label class="control-label col-sm-4 pl-0">{{
                $i18n.t('dashboard.modal.epsg')
              }}</label>
              <input
                v-model="epsg"
                class="form-control"
                :disabled="isEpsgAutomatic"
                :title="isEpsgAutomatic ? $i18n.t('upload.automaticEpsg') : null"
                @keypress="isNumber($event)"
              />
            </div>
            <div style="display: flex" class="pt-10">
              <label class="control-label col-sm-4 pl-0">{{
                $i18n.t('dashboard.modal.dataFormat')
              }}</label>
              <select v-model="selectedDataExtension" class="form-control">
                <option
                  v-for="(dataFormat, idx) of dataFormats"
                  :key="idx"
                  :value="dataFormat"
                  v-text="dataFormat.text"
                />
              </select>
            </div>
            <div style="display: flex" class="pt-10">
              <label class="control-label col-sm-4 pl-0">{{
                $i18n.t('dashboard.modal.dataCoding')
              }}</label>
              <select v-model="selectedDataCoding" class="form-control">
                <option
                  v-for="(dataCoding, idx) of dataCodings"
                  :key="idx"
                  :value="dataCoding.value"
                  v-text="dataCoding.text"
                />
              </select>
            </div>
            <div class="pt-10 flex-center">
              <FileUpload
                ref="upload"
                v-model="files"
                :multiple="true"
                :drop="true"
                :drop-directory="true"
                @input-filter="fileFilter"
              >
                {{ this.$i18n.t('upload.defaultMessage') }}
                <div id="upload_list">
                  <ul>
                    <li v-for="(file, idx) in files" :key="idx" style="list-style-position: inside">
                      {{ file.name }}
                      <i
                        class="icon-li fa fa-times fa-lg ml-5 delete-file-icon"
                        @click="removeFile(file)"
                      />
                    </li>
                  </ul>
                </div>
              </FileUpload>
            </div>
          </div>
          <div class="modal-footer">
            <span v-if="isFileSending" class="file-sending">
              <button type="button" class="btn">
                <i class="fa fa-spin fa-spinner" />
              </button>
              <span>{{ $i18n.t('upload.fileSending') }}</span>
            </span>
            <button
              ref="closeModalBtn"
              type="button"
              class="btn btn-default"
              data-dismiss="modal"
              @click="clearUploadFiles"
            >
              {{ $i18n.t('default.cancel') }}
            </button>
            <button
              type="button"
              class="btn btn-success"
              :disabled="
                !vectorLayerName ||
                  isFileSending ||
                  vectorLayerName.length > layerMaxNameLength ||
                  files.length <= 0
              "
              @click="sendVectorLayer"
            >
              {{ $i18n.t('default.save') }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <!--KONIEC MODALA-->

    <!--MODAL DODAWANIA USŁUG-->
    <div
      id="addLayerWmsModal"
      ref="addLayerWmsModal"
      class="modal fade"
      data-backdrop="static"
      tabindex="-2"
      role="dialog"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-dialog-centered" role="document" style="max-height: 80%">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">{{ $i18n.t('dashboard.modal.addLayerWms') }}</h4>
          </div>
          <div class="modal-body">
            <div style="display: flex">
              <label class="control-label col-sm-4" style="width: 150px">{{
                $i18n.t('dashboard.modal.serviceName')
              }}</label>
              <input v-model="serviceName" type="text" class="form-control" />
            </div>
            <div style="display: flex" class="pt-10">
              <label class="control-label col-sm-4" style="width: 150px">{{
                $i18n.t('dashboard.modal.dataFormat')
              }}</label>
              <select v-model="selectedMapService" class="form-control">
                <option
                  v-for="(mapService, idx) of mapServices"
                  :key="idx"
                  :value="mapService"
                  v-text="mapService.text"
                />
              </select>
            </div>
            <div style="display: flex;" class="pt-10">
              <label class="control-label col-sm-4" style="width: 160px">{{
                $i18n.t('dashboard.modal.layerAddress')
              }}</label>
              <input v-model="serviceUrl" type="text" class="form-control" />
              <i
                class="fa fa-cloud-download fetch-wms-icon"
                :class="{ disabled: serviceUrl.length < 1 }"
                :title="$i18n.t('default.downloadAvailableLayers')"
                aria-hidden="true"
                @click="fetchWms"
              />
            </div>
            <div v-if="fetchedLayers.length > 0" class="pt-10">
              <ul class="select-layer-list">
                <li v-for="layer in fetchedLayers" :key="layer">
                  <label class="checkbox-inline">
                    <input id="checkbox" v-model="selectedLayers" type="checkbox" :value="layer" />
                    {{ layer }}
                  </label>
                </li>
              </ul>
            </div>
            <div
              v-if="fetchedLayers.length === 0 && isFetching"
              class="loading-overlay pt-10 pb-10"
              style="text-align: center;"
            >
              <div class="loading-indicator mb-10">
                <h4>{{ $i18n.t('default.loading') }}</h4>
                <i class="fa fa-lg fa-spin fa-spinner" />
              </div>
            </div>
            <hr />
            <div v-if="fetchedLayers.length > 0" class="pt-10">
              <label class="checkbox-inline">
                <input id="checkbox" v-model="isServicePublic" type="checkbox" />
                {{ $i18n.t('dashboard.modal.servicePublic') }}
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button
              ref="closeModalWmsBtn"
              type="button"
              class="btn btn-default"
              data-dismiss="modal"
              @click="clearServicesModal"
            >
              {{ $i18n.t('default.cancel') }}
            </button>
            <button
              type="button"
              class="btn btn-success"
              :disabled="
                selectedLayers.length === 0 ||
                  serviceName.length === 0 ||
                  selectedLayers.length === 0
              "
              @click="addService"
            >
              {{ $i18n.t('default.save') }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <!--KONIEC MODALA-->
  </span>
</template>

<script>
import FileUpload from 'vue-upload-component';
import WMSCapabilities from 'ol/format/WMSCapabilities';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';

export default {
  name: 'Dashboard',
  components: {
    FileUpload,
    ProjectsPanel: () => import('@/components/ProjectsPanel'),
    vSelect
  },
  filters: {
    maxLength: val => {
      if (val.length > 50) {
        return `${val.slice(0, 50)}...`;
      }
      return val;
    },
    maxInputTagLength: val => {
      if (val.length > 35) {
        return `${val.slice(0, 35)}...`;
      }
      return val;
    }
  },
  data: vm => ({
    currentEditedLayer: undefined,
    dataCodings: [
      {
        text: 'UTF-8',
        value: 'utf-8'
      },
      {
        text: 'Windows-1250',
        value: 'cp1250'
      }
    ],
    dataFormats: [
      {
        text: 'ESRI Shapefile',
        value: 'shapefile',
        extensions: ['.shp', '.shx', '.dbf', '.prj', '.cpg', '.qpj', '.qix']
      },
      { text: 'GeoJSON', value: 'geojson', extensions: ['.geojson'] },
      { text: 'GML', value: 'gml', extensions: ['.gml'] }
    ],
    mapServices: [
      {
        text: 'WMS',
        value: 'wms'
      }
    ],
    epsg: undefined,
    fetchedLayers: [],
    files: [],
    isEpsgAutomatic: true,
    isFetching: false,
    isFileSending: false,
    isSendingError: false,
    isServicePublic: false,
    isTagAddings: false,
    isTagMenuOpen: false,
    layersAll: undefined,
    layerMaxNameLength: 60,
    pickrComponents: {
      preview: true,
      opacity: true,
      hue: true,
      interaction: {
        hex: false,
        rgba: false,
        hsla: false,
        hsva: false,
        cmyk: false,
        input: false,
        clear: false,
        save: true
      }
    },
    postAction: `${vm.$store.getters.getApiUrl}/layers?token=${localStorage.getItem('token')}`,
    projects: [],
    projectsGetting: true,
    searchLayer: '',
    searchTag: '',
    serviceUrl: '',
    serviceName: '',
    selectedDataCoding: '',
    selectedDataExtension: '',
    selectedMapService: '',
    selectedLayers: [],
    tags: [],
    vectorLayerName: '',
    vectorLayersList: undefined
  }),
  computed: {
    featureAttachments() {
      return this.$store.getters.getFeatureAttachments;
    },
    filteredLayersAll() {
      if (!this.layersAll) {
        return false;
      }
      const filteredByName = this.layersAll.filter(layer =>
        layer.name.toLowerCase().includes(this.searchLayer.toLowerCase())
      );
      if (!this.searchTag) {
        return filteredByName;
      }
      return filteredByName.filter(
        layer => layer.tags && layer.tags.find(tag => tag.id === this.searchTag.id)
      );
    },
    servicesList() {
      return this.$store.getters.getServices;
    }
  },
  watch: {
    selectedDataExtension() {
      this.files = [];
    },
    vectorLayersList() {
      this.layersAll = this.getLayersAll();
    },
    servicesList() {
      this.layersAll = this.getLayersAll();
    }
  },
  async mounted() {
    this.selectedMapService = this.mapServices[0];
    this.selectedDataCoding = this.dataCodings[0].value;
    this.selectedDataExtension = this.dataFormats[0];
    this.getLayers();
    this.getProjects();
    this.getServices();
    this.getTags();
    this.getLayerMaxNameLength();
    this.$store.commit('setDefaultGroup', process.env.VUE_APP_DEFAULT_GROUP);
  },
  methods: {
    async updateLayerTags(val, e) {
      this.isTagAddings = true;
      const payload = { lid: val.id };
      if (e.length > val.tags.length) {
        const tag = e.filter(t => !val.tags.includes(t))[0];
        if (!tag) {
          this.$alertify.error(this.$i18n.t('settings.tagError'));
          this.isTagAddings = false;
          return;
        } else if (!tag.id) {
          const r = await this.$store.dispatch('addTag', {
            color: '#000000',
            name: tag.name
          });
          if (r.status === 201) {
            tag.id = r.body.data;
            tag.color = '#000000';
            this.tags.push(tag);
            payload.tid = tag.id;
            const rr = await this.$store.dispatch('tagLayer', payload);
            if (rr.status === 204) {
              this.filteredLayersAll.find(l => l.id === val.id).tags.push(tag);
              this.$alertify.success(this.$i18n.t('settings.tagAdded'));
              this.isTagAddings = false;
            } else {
              this.$alertify.error(this.$i18n.t('settings.tagError'));
              this.isTagAddings = false;
            }
          } else {
            this.isTagAddings = false;
            this.$alertify.error(this.$i18n.t('settings.tagError'));
          }
        } else {
          payload.tid = tag.id;
          const r = await this.$store.dispatch('tagLayer', payload);
          if (r.status === 204) {
            this.filteredLayersAll.find(l => l.id === val.id).tags.push(tag);
            this.$alertify.success(this.$i18n.t('settings.tagAdded'));
            this.isTagAddings = false;
          } else {
            this.$alertify.error(this.$i18n.t('settings.tagError'));
            this.isTagAddings = false;
          }
        }
      } else {
        const tag = val.tags.filter(t => !e.includes(t))[0];
        payload.tid = tag.id;
        const r = await this.$store.dispatch('untagLayer', payload);
        if (r.status === 204) {
          this.filteredLayersAll.find(l => l.id === val.id).tags = this.filteredLayersAll
            .find(l => l.id === val.id)
            .tags.filter(t => t.id !== tag.id);
          this.$alertify.success(this.$i18n.t('settings.tagDeleted'));
          this.isTagAddings = false;
        } else {
          this.$alertify.error(this.$i18n.t('settings.tagError'));
          this.isTagAddings = false;
        }
      }
    },
    async addService() {
      const r = await this.$store.dispatch('addService', {
        layers: this.selectedLayers.join(','),
        name: this.serviceName,
        public: this.isServicePublic,
        url: this.serviceUrl
      });
      if (r.status === 201) {
        this.$alertify.success(this.$i18n.t('default.success'));
        this.clearServicesModal();
        this.$store.commit('addService', r.body.services);
      } else {
        this.$i18n.t('default.error');
      }
    },
    async deleteService(sid) {
      this.$alertify
        .confirm(
          this.$i18n.t('dashboard.modal.deleteService'),
          async () => {
            const r = await this.$store.dispatch('deleteService', sid);
            if (r.status === 200) {
              this.$alertify.success(this.$i18n.t('default.deleted'));
              this.$store.commit('deleteService', sid);
            } else {
              this.$i18n.t('default.error');
            }
          },
          () => {}
        )
        .set({ title: this.$i18n.t('dashboard.modal.deleteServiceTitle') })
        .set({
          labels: {
            ok: this.$i18n.t('default.delete'),
            cancel: this.$i18n.t('default.cancel')
          }
        });
    },
    async getLayers() {
      const r = await this.$store.dispatch('getLayers');
      this.vectorLayersList = r.body.layers;
    },
    async getLayerMaxNameLength() {
      const r = await this.$store.dispatch('getLayerMaxNameLength');
      this.layerMaxNameLength = r.body.data;
    },
    async getProjects() {
      const r = await this.$store.dispatch('getProjects');
      this.projects = r.body.data;
      this.projectsGetting = false;
    },
    async getServices() {
      const r = await this.$store.dispatch('getServices');
      this.$store.commit('setServices', r.body.services);
    },
    async getTags() {
      const r = await this.$store.dispatch('getTags');
      this.tags = r.body.data;
    },
    async fetchWms() {
      if (this.serviceUrl.length < 1) {
        return;
      }
      this.isFetching = true;
      const parser = new WMSCapabilities();
      const url = `https://divi.io/wms_proxy/${this.serviceUrl}?request=GetCapabilities&service=WMS`;
      fetch(url)
        .then(response => response.text())
        .then(text => {
          const result = parser.read(text);
          this.fetchedLayers = result.Capability.Layer.Layer.map(el => el.Name);
          this.isFetching = false;
        })
        .catch(() => {
          this.$alertify.error(this.$i18n.t('default.error'));
          this.isFetching = false;
        });
    },
    async setEditedLayer(layType, layId) {
      if (layType === 'vector') {
        this.currentEditedLayer = Object.assign(
          {},
          this.vectorLayersList.find(el => el.id === layId)
        );
      }
      this.$router.push({
        name: 'settings',
        params: {
          layerId: this.currentEditedLayer.id,
          layer: this.currentEditedLayer,
          vectorLayersList: this.vectorLayersList
        }
      });
    },
    clearServicesModal() {
      document.querySelector('#addLayerWmsModal button.btn.btn-default').click();
      if (this.isFetching) {
        return;
      }
      this.fetchedLayers = [];
      this.selectedLayers = [];
      this.serviceName = '';
      this.isServicePublic = false;
      this.serviceUrl = '';
    },
    clearUploadFiles() {
      if (!this.isFileSending) {
        this.files = [];
        this.vectorLayerName = '';
        this.selectedDataCoding = this.dataCodings[0].value;
        this.selectedDataExtension = this.dataFormats[0];
        this.isEpsgAutomatic = true;
        this.epsg = '';
      }
    },
    deleteLayer(el) {
      this.$alertify
        .confirm(
          this.$i18n.t('dashboard.modal.deleteLayerContent'),
          async () => {
            const r = await this.$store.dispatch('deleteLayer', el.id);
            if (r.status === 200) {
              this.vectorLayersList = this.vectorLayersList.filter(lay => lay.id !== el.id);
              this.projects = this.projects.filter(p => p.active_layer_id !== el.id);
              this.$alertify.success(this.$i18n.t('default.deleted'));
            } else if (r.status === 403) {
              if (r.body.error === 'access denied, not an owner') {
                this.$alertify.error(this.$i18n.t('default.noAccess'));
              } else {
                this.$alertify.error(this.$i18n.t('default.error'));
              }
            } else {
              this.$alertify.error(this.$i18n.t('default.error'));
            }
          },
          () => {}
        )
        .set({ title: this.$i18n.t('dashboard.modal.deleteLayerTitle') })
        .set({
          labels: {
            ok: this.$i18n.t('default.delete'),
            cancel: this.$i18n.t('default.cancel')
          }
        });
    },
    deleteProject(pid) {
      this.projects = this.projects.filter(p => p.id !== pid);
    },
    fileFilter: function(newFile, oldFile, prevent) {
      let ext = newFile.name.substr(newFile.name.lastIndexOf('.'));
      if (newFile && !oldFile) {
        if (!this.selectedDataExtension.extensions.includes(ext)) {
          this.$alertify.error(this.$i18n.t('upload.uploadExtensionError'));
          return prevent();
        }
        for (const file of this.files) {
          if (newFile.name === file.name && newFile.size === file.size) {
            this.$alertify.error(this.$i18n.t('upload.uploadDuplicate'));
            return prevent();
          }
        }
      }
    },
    getLayersAll() {
      let layersAll = [];
      if (this.vectorLayersList && this.servicesList) {
        layersAll = [...this.vectorLayersList, ...this.servicesList].sort((a, b) =>
          a.name > b.name ? 1 : b.name > a.name ? -1 : 0
        );
      } else if (this.vectorLayersList) {
        layersAll = this.vectorLayersList;
      } else if (this.servicesList) {
        layersAll = this.servicesList;
      }
      return layersAll;
    },
    goToManager(val) {
      this.$router.push({
        name: 'feature_manager',
        params: {
          layerId: val.id,
          layerName: val.name,
          vectorLayersList: this.vectorLayersList
        }
      });
      this.setAttachmentsLayer(val.id);
      this.$store.commit('setLayerName', val.name);
    },
    isNumber(evt) {
      const e = evt || window.event;
      const charCode = e.which ? e.which : e.keyCode;
      if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        e.preventDefault();
        return false;
      }
      return true;
    },
    removeFile(file) {
      let fileIndex = this.files.indexOf(file);
      if (fileIndex > -1) {
        this.files = this.files.filter(f => f != file);
      }
    },
    sendingError(file) {
      if (!this.isSendingError) {
        this.$alertify.error(this.$i18n.t('upload.uploadError'));
      }
      if (file.xhr.status === 400) {
        this.isEpsgAutomatic = false;
        if (!this.isSendingError) this.$alertify.warning(this.$i18n.t('upload.noEpsg'));
      }
      // eslint-disable-next-line no-param-reassign
      file.status = 'queued';
      this.isSendingError = true;
    },
    sendingEvent(files, xhr, formData) {
      this.isSendingError = false;
      formData.append('name', this.vectorLayerName);
      if (!this.isEpsgAutomatic) {
        formData.append('epsg', this.epsg);
      }
    },
    sendingSuccess() {
      this.isEpsgAutomatic = true;
      this.isSendingError = false;
    },
    sendVectorLayer() {
      this.isFileSending = true;
      let formData = new FormData();
      for (const [index, file] of this.files.entries()) {
        formData.append(`file[${index}]`, file.file);
      }
      formData.append('name', this.vectorLayerName);
      formData.append('encoding', this.selectedDataCoding);
      if (!this.isEpsgAutomatic) {
        formData.append('epsg', this.epsg);
      }
      this.$http
        .post(this.postAction, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        .then(r => {
          this.isFileSending = false;
          this.$refs.closeModalBtn.click();
          if (r.status === 201) {
            this.$alertify.success(this.$i18n.t('upload.uploadSuccess') + ' ' + r.data.layers.name);
            let newLayer = {
              id: r.data.layers.id,
              name: r.data.layers.name,
              tags: []
            };
            if (!this.vectorLayersList.find(el => el.id === newLayer.id)) {
              this.vectorLayersList.push(newLayer);
              this.vectorLayersList.sort((a, b) =>
                a.name > b.name ? 1 : b.name > a.name ? -1 : 0
              );
            }
          } else if (r.status === 400) {
            this.epsg = '';
            this.isEpsgAutomatic = false;
            this.$alertify.warning(this.$i18n.t('upload.noEpsg'));
          } else {
            this.$alertify.error(this.$i18n.t('upload.uploadError') + ' ' /*+ newFile.name*/);
          }
        })
        .catch(err => {
          this.isFileSending = false;
          if (err.response.data.error === 'epsg not recognized') {
            this.$alertify.error(this.$i18n.t('upload.noEpsg'));
            this.isEpsgAutomatic = false;
            this.epsg = 2180;
          } else if (err.response.data.error === 'layer already exists') {
            this.$alertify.error(this.$i18n.t('upload.nameExistsError'));
          } else if (err.response.data.error === 'layer has attachemnts column') {
            this.$alertify.error(this.$i18n.t('upload.uploadAttachmentExistsError'));
          } else {
            this.$alertify.error(this.$i18n.t('upload.uploadError'));
          }
        });
    },
    setAttachmentsLayer(lid) {
      if (!Object.keys(this.featureAttachments).includes(lid)) {
        this.$store.commit('setAttachmentsLayer', lid);
      }
    }
  }
};
</script>

<style scoped>
.mySelect >>> .vs__dropdown-toggle,
.mySelect >>> .vs__search {
  background-color: white !important;
}
.mySelect >>> .vs__search {
  margin: 0;
}
.mySelect >>> .vs__search::placeholder,
.mySelect >>> .vs__dropdown-toggle {
  max-width: 80vh;
  text-align: center;
  padding-bottom: 2px;
  font-size: 12px;
  border: 1px solid rgb(235, 235, 235);
  /*
  border-radius: 0;
  border-bottom: 1px solid rgba(60, 60, 60, 0.26);
  */
}

.mySelect >>> .vs__dropdown-toggle:hover {
  border: 1px solid rgb(190, 190, 190);
}

.mySelect >>> .vs__dropdown-menu {
  max-height: 30vh;
  overflow-y: auto;
  overflow-x: hidden;
  width: 30vh;
  font-size: 12px;
  padding-bottom: 2px;
}

.mySelect >>> .vs__dropdown-menu > .vs__dropdown-option {
  width: 30vh;
  overflow: hidden;
}

.mySelect >>> .vs__dropdown-toggle > .vs__actions {
  display: none;
}

.mySelect >>> .vs__dropdown-toggle > .vs__selected-options > .vs__selected {
  background-color: white;
  margin: auto;
  margin-right: 2px;
}

.mySelect >>> .vs__dropdown-toggle > .vs__selected-options > .vs__search {
  color: white;
}

.tagFilter >>> .vs__search::placeholder,
.tagFilter >>> .vs__dropdown-toggle {
  height: 34px;
  max-width: 80vh;
  padding-bottom: 2px;
  font-size: 14px;
  margin: 0;
}
.tagFilter >>> .vs__dropdown-menu {
  font-size: 12px;
  overflow-x: hidden;
}
.tagFilter >>> .vs__dropdown-menu > .vs__dropdown-option {
  overflow: hidden;
}

.add-layer {
  display: block;
}
.btn-upload {
  margin-right: 20px;
}
.color-picker__label {
  position: relative;
  top: 2px;
  right: 10px;
}
.container {
  top: 20px;
}
.container__input {
  width: 300px;
}
.control-label {
  line-height: 29px;
  font-size: 12px;
}
.dashboard .container {
  width: 97%;
  top: 0;
}
.delete-file-icon {
  z-index: 2;
  position: relative;
}
.desc-sm {
  color: #b5b5b5;
  font-family: 'Open Sans', 'Trebuchet MS', arial, sans-serif;
  font-size: 12px;
  letter-spacing: -1px;
  line-height: 1.75em;
  margin-left: 5px;
}
.fetch-wms-icon {
  font-size: 26px;
  padding-left: 6px;
  padding-top: 6px;
  cursor: pointer;
}
.disabled {
  cursor: not-allowed;
  color: lightgrey;
}
.files-list li {
  width: 120px;
  list-style: none;
}
.file-sending > button {
  background-color: white;
  cursor: default;
  padding-top: 0;
}
.file-sending > span {
  margin-right: 30px;
  font-weight: bold;
}
.file-uploads {
  margin: auto;
  overflow: hidden;
  position: relative;
  display: inline-block;
  min-height: 100px;
  width: 80%;
  border: 1px solid lightgray;
}
.file-uploads.file-uploads-html4 input[type='file'] {
  opacity: 0;
  font-size: 20em;
  z-index: 1;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  position: absolute;
  width: 100%;
  height: 100%;
}
.file-uploads.file-uploads-html5 input[type='file'] {
  overflow: hidden;
  position: fixed;
  width: 1px;
  height: 1px;
  z-index: -1;
  opacity: 0;
}
.heading-block:after,
.heading-block:before {
  display: none;
}
#layers-list-icons {
  margin-right: 10px;
}
.loading-overlay {
  width: 100%;
  text-align: center;
}
.panel-title__names {
  font-size: 14px;
}
.panel-title__names .bold:not(.panel-title__wms):hover {
  cursor: pointer;
}
.panel-title__tools i:not(:last-child) {
  margin-right: 5px;
}
.section {
  height: 95%;
}
.section__content--add:hover {
  cursor: pointer;
}
.section__content.heading-block.heading-block-main {
  overflow-y: auto;
  max-height: calc(100% - 50px);
}
.section__header {
  padding-bottom: 15px;
  margin-bottom: -1px;
}
.select-layer-list {
  list-style-type: none;
  padding-left: 32px;
  text-align: left;
  text-decoration: none;
  max-height: 50vh;
  overflow-y: auto;
}
#upload_list {
  text-align: left;
  display: flex;
  justify-content: center;
}
</style>

<template>
  <div class="dashboard container align-center">
    <!-- TABELA WARSTW -->
    <div class="col-sm-12 pl-0 pr-0 section">
      <h2 class="flex-center container__border--bottom container__border--grey mb-0">
        <div class="p-0 container__border--bottom container__border--red section__header">
          <i class="fa fa-database" />
          <span data-i18n="dashboard.title">{{ $i18n.t('dashboard.title.layersList') }}</span>
        </div>
        <div class="p-0">
          <input
            type="text"
            class="form-control container__input"
            v-model="searchLayer"
            :placeholder="$i18n.t('dashboard.placeholder.layersFilter')"
          />
        </div>
      </h2>
      <div class="section__content heading-block heading-block-main">
        <span class="add-layer">
          <i
            class="fa fa-plus-circle fa-lg green pt-10"
            style="margin-right:5px;"
          />
          <a
            data-toggle="modal"
            data-target="#addLayerModal"
            data-type="vectorLayer"
            class="green section__content--add"
          >{{ $i18n.t('dashboard.list.addLayer') }}</a>
        </span>
        <span class="add-layer">
          <i
            class="fa fa-plus-circle fa-lg green pt-10"
            style="margin-right:5px;"
          />
          <a
            data-toggle="modal"
            data-target="#addLayerWmsModal"
            data-type="externalLayer"
            class="green section__content--add"
          >{{ $i18n.t('dashboard.list.addService') }}</a>
        </span>

        <div
          class="loading-overlay pt-10 pb-10"
          v-if="!layersAll"
        >
          <div class="loading-indicator mb-10">
            <h4>{{ $i18n.t('default.loading') }}</h4>
            <i class="fa fa-lg fa-spin fa-spinner" />
          </div>
        </div>

        <div
          v-if="filteredLayersAll.length == 0"
          class="pt-10 pb-10"
        >{{ $i18n.t('default.noLayers') }}</div>
        <template
          v-else
          v-for="(val, key) in filteredLayersAll"
        >
          <div
            class="mb-0"
            :key="key"
          >
            <div class="panel-heading pl-0 pr-0">
              <h4 class="panel-title flex-center">
                <span style="display:inherit">
                  <span
                    v-if="val.url"
                    class="panel-title__names"
                  >
                    <i
                      style="margin-right:9px"
                      class="icon-li fa fa-link fa-lg"
                    />
                    <span class="bold panel-title__wms">{{ val.name }}</span>
                    <span
                      class="desc-sm"
                      :title="val.url"
                    >
                      <strong>URL</strong>
                      :{{val.url|maxLength}}
                    </span>
                    <span
                      class="desc-sm"
                      :title="val.layers"
                    >
                      <strong>{{ $i18n.t('default.layers') }}</strong>
                      : {{ val.layers | maxLength }}
                    </span>
                  </span>
                  <span
                    v-else
                    class="panel-title__names"
                  >
                    <i class="icon-li fa fa-map-o fa-lg mr-5" />
                    <span
                      class="bold"
                      href="#"
                      @click="goToManager(val)"
                    >{{ val.name }}</span>
                    <span class="desc-sm">{{ val.team }}</span>
                  </span>
                  <span
                    v-if="val.tags"
                    style="min-width: 100px"
                  >
                    <vSelect
                      taggable
                      multiple
                      class="mySelect"
                      label="name"
                      maxHeight="10px"
                      placeholder="(Brak tagów)"
                      :disabled="isTagAddings"
                      :options="tags.filter(t => !val.tags.find(vT => vT.id === t.id))"
                      :value="val.tags"
                      :v-if="tags.length > 0"
                      @input="updateLayerTags(val, $event)"
                    >
                      <template v-slot:option="option">
                        <span :style="`color: ${option.color}`">{{option.name}}</span>
                      </template>
                      <template v-slot:selected-option="option">
                        <span :style="`color: ${option.color}`">{{option.name}}</span>
                      </template>
                      <span slot="no-options">{{$i18n.t('settings.tagNotFound')}}</span>
                    </vSelect>
                  </span>
                </span>
                <span
                  id="layers-list-icons"
                  class="panel-title__tools"
                >
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
                    @click="val.url?deleteService(val.id):deleteLayer(val)"
                  />
                </span>
              </h4>
            </div>
          </div>
        </template>
      </div>
    </div>
    <!-- KONIEC TABELI WARSTW -->

    <!--MODAL DODAWANIA WARSTW-->
    <div
      class="modal fade"
      data-backdrop="static"
      id="addLayerModal"
      tabindex="-1"
      role="dialog"
      aria-hidden="true"
      ref="addLayerModal"
    >
      <div
        class="modal-dialog modal-dialog-centered"
        role="document"
      >
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">{{ $i18n.t('dashboard.modal.addLayer') }}</h4>
          </div>
          <div class="modal-body">
            <div style="display: flex">
              <label class="control-label col-sm-4 pl-0">{{ $i18n.t('dashboard.modal.layerName') }}</label>
              <input
                type="text"
                class="form-control"
                v-model="vectorLayerName"
              />
            </div>
            <div
              style="display: flex"
              class="pt-10"
            >
              <label class="control-label col-sm-4 pl-0">{{ $i18n.t('dashboard.modal.epsg') }}</label>
              <input
                class="form-control"
                v-model="epsg"
                @keypress="isNumber($event)"
                :disabled="isEpsgAutomatic"
                :title="isEpsgAutomatic ? $i18n.t('upload.automaticEpsg') : null"
              />
            </div>
            <div
              style="display: flex"
              class="pt-10"
            >
              <label class="control-label col-sm-4 pl-0">{{ $i18n.t('dashboard.modal.dataFormat') }}</label>
              <select
                class="form-control"
                v-model="selectedDataExtension"
              >
                <option
                  v-for="(dataFormat, idx) of dataFormats"
                  v-text="dataFormat.text"
                  :key="idx"
                  :value="dataFormat"
                />
              </select>
            </div>
            <div class="pt-10">
              <file-upload
                ref="upload"
                v-model="files"
                :multiple="true"
                :drop="true"
                :drop-directory="true"
                @input-filter="fileFilter"
              >
                {{this.$i18n.t('upload.defaultMessage')}}
                <ul>
                  <li
                    v-for="(file,idx) in files"
                    :key="idx"
                  >
                    {{file.name}}
                    <i
                      class="icon-li fa fa-times fa-lg ml-5 delete-file-icon"
                      @click="removeFile(file)"
                    />
                  </li>
                </ul>
              </file-upload>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-default"
              data-dismiss="modal"
              @click="clearUploadFiles"
              ref="closeModalBtn"
            >{{ $i18n.t('default.cancel') }}</button>
            <button
              type="button"
              class="btn btn-success"
              @click="sendVectorLayer"
              :disabled="!vectorLayerName"
            >{{ $i18n.t('default.save') }}</button>
          </div>
        </div>
      </div>
    </div>
    <!--KONIEC MODALA-->

    <!--MODAL DODAWANIA USŁUG-->
    <div
      class="modal fade"
      data-backdrop="static"
      id="addLayerWmsModal"
      tabindex="-2"
      role="dialog"
      aria-hidden="true"
      ref="addLayerWmsModal"
    >
      <div
        class="modal-dialog modal-dialog-centered"
        role="document"
        style="max-height: 80%"
      >
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">{{ $i18n.t('dashboard.modal.addLayerWms') }}</h4>
          </div>
          <div class="modal-body">
            <div style="display: flex">
              <label
                class="control-label col-sm-4"
                style="width: 150px"
              >{{ $i18n.t('dashboard.modal.serviceName') }}</label>
              <input
                type="text"
                class="form-control"
                v-model="serviceName"
              />
            </div>
            <div
              style="display: flex"
              class="pt-10"
            >
              <label
                class="control-label col-sm-4"
                style="width: 150px"
              >{{ $i18n.t('dashboard.modal.dataFormat') }}</label>
              <select
                class="form-control"
                v-model="selectedMapService"
              >
                <option
                  v-for="(mapService, idx) of mapServices"
                  v-text="mapService.text"
                  :key="idx"
                  :value="mapService"
                />
              </select>
            </div>
            <div
              class="pt-10"
              style="display: flex;"
            >
              <label
                class="control-label col-sm-4"
                style="width: 160px"
              >{{ $i18n.t('dashboard.modal.layerAddress') }}</label>
              <input
                type="text"
                class="form-control"
                v-model="serviceUrl"
              />
              <i
                class="fa fa-cloud-download fetch-wms-icon"
                :class="{disabled: serviceUrl.length < 1}"
                :title="$i18n.t('default.downloadAvailableLayers')"
                aria-hidden="true"
                @click="fetchWms"
              />
            </div>
            <div
              class="pt-10"
              v-if="fetchedLayers.length > 0"
            >
              <ul class="select-layer-list">
                <li
                  v-for="layer in fetchedLayers"
                  :key="layer"
                >
                  <label class="checkbox-inline">
                    <input
                      type="checkbox"
                      id="checkbox"
                      :value="layer"
                      v-model="selectedLayers"
                    />
                    {{ layer }}
                  </label>
                </li>
              </ul>
            </div>
            <div
              class="loading-overlay pt-10 pb-10"
              style="text-align: center;"
              v-if="fetchedLayers.length === 0 && isFetching"
            >
              <div class="loading-indicator mb-10">
                <h4>{{ $i18n.t('default.loading') }}</h4>
                <i class="fa fa-lg fa-spin fa-spinner" />
              </div>
            </div>
            <hr />
            <div
              class="pt-10"
              v-if="fetchedLayers.length > 0"
            >
              <label class="checkbox-inline">
                <input
                  type="checkbox"
                  id="checkbox"
                  v-model="isServicePublic"
                />
                {{ $i18n.t('dashboard.modal.servicePublic') }}
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-default"
              data-dismiss="modal"
              ref="closeModalWmsBtn"
              @click="clearServicesModal"
            >{{ $i18n.t('default.cancel') }}</button>
            <button
              type="button"
              class="btn btn-success"
              :disabled="selectedLayers.length === 0 ||
                serviceName.length === 0 ||
                selectedLayers.length === 0"
              @click="addService"
            >{{ $i18n.t('default.save') }}</button>
          </div>
        </div>
      </div>
    </div>
    <!--KONIEC MODALA-->
  </div>
</template>

<script>
import FileUpload from 'vue-upload-component';
import WMSCapabilities from 'ol/format/WMSCapabilities';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';

export default {
  name: 'Dashboard',
  data: vm => ({
    currentEditedLayer: undefined,
    dataFormats: [
      {
        text: 'ESRI Shapefile',
        value: 'shapefile',
        extensions: ['.shp', '.shx', '.dbf', '.prj', '.cpg', '.qpj']
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
    isSendingError: false,
    isServicePublic: false,
    isTagAddings: false,
    layersAll: undefined,
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
    postAction: `${
      vm.$store.getters.getApiUrl
    }/layers?token=${localStorage.getItem('token')}`,
    searchLayer: '',
    serviceUrl: '',
    serviceName: '',
    selectedDataExtension: '',
    selectedMapService: '',
    selectedLayers: [],
    tags: [],
    vectorLayerName: '',
    vectorLayersList: undefined
  }),
  components: {
    FileUpload,
    vSelect
  },
  computed: {
    featureAttachments() {
      return this.$store.getters.getFeatureAttachments;
    },
    filteredLayersAll() {
      if (!this.layersAll) {
        return false;
      }
      return this.layersAll.filter(layer =>
        layer.name.toLowerCase().includes(this.searchLayer.toLowerCase())
      );
    },
    servicesList() {
      return this.$store.getters.getServices;
    }
  },
  filters: {
    maxLength: val => {
      if (val.length > 50) {
        return `${val.slice(0, 50)}...`;
      }
      return val;
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
          this.filteredLayersAll.find(
            l => l.id === val.id
          ).tags = this.filteredLayersAll
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
        .catch(error => {
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
      document
        .querySelector('#addLayerWmsModal button.btn.btn-default')
        .click();
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
      this.files = [];
      this.vectorLayerName = '';
      this.selectedDataExtension = this.dataFormats[0];
      this.isEpsgAutomatic = true;
    },
    deleteLayer(el) {
      this.$alertify
        .confirm(
          this.$i18n.t('dashboard.modal.deleteLayerContent'),
          async () => {
            const r = await this.$store.dispatch('deleteLayer', el.id);
            if (r.status === 200) {
              this.vectorLayersList = this.vectorLayersList.filter(
                lay => lay.id !== el.id
              );
              this.$alertify.success(this.$i18n.t('default.deleted'));
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
    fileFilter: function(newFile, oldFile, prevent) {
      let ext = newFile.name.substr(newFile.name.lastIndexOf('.'));
      if (newFile && !oldFile) {
        if (!this.selectedDataExtension.extensions.includes(ext)) {
          this.$alertify.error(this.$i18n.t('upload.uploadExtensionError'));
          return prevent();
        }
        for (file of this.files) {
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
        layersAll = [
          ...this.vectorLayersList,
          ...this.servicesList
        ].sort((a, b) => (a.name > b.name ? 1 : b.name > a.name ? -1 : 0));
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
        if (!this.isSendingError)
          this.$alertify.warning(this.$i18n.t('upload.noEpsg'));
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
      let formData = new FormData();
      for (const [index, file] of this.files.entries()) {
        formData.append(`file[${index}]`, file.file);
      }
      formData.append('name', this.vectorLayerName);
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
          this.$refs.closeModalBtn.click();
          if (r.status === 201) {
            vm.$alertify.success(
              vm.$i18n.t('upload.uploadSuccess') + ' ' + r.data.layers.name
            );
            let newLayer = {
              id: r.data.layers.id,
              name: r.data.layers.name
            };
            if (!this.vectorLayersList.find(el => el.id === newLayer.id)) {
              this.vectorLayersList.push(newLayer);
              this.vectorLayersList.sort((a, b) =>
                a.name > b.name ? 1 : b.name > a.name ? -1 : 0
              );
            }
          } else if (r.status === 400) {
            this.isEpsgAutomatic = false;
            this.$alertify.warning(this.$i18n.t('upload.noEpsg'));
          } else {
            vm.$alertify.error(
              vm.$i18n.t('upload.uploadError') + ' ' + newFile.name
            );
          }
        })
        .catch(err => {
          this.$refs.closeModalBtn.click();
          this.$alertify.error(this.$i18n.t('upload.uploadError'));
        });
    },
    setAttachmentsLayer(lid) {
      if (!Object.keys(this.featureAttachments).includes(lid)) {
        this.$store.commit('setAttachmentsLayer', lid);
      }
    }
  },
  async mounted() {
    this.selectedMapService = this.mapServices[0];
    this.selectedDataExtension = this.dataFormats[0];
    this.getLayers();
    this.getServices();
    this.getTags();
    this.$store.commit('setDefaultGroup', process.env.VUE_APP_DEFAULT_GROUP);
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
.mySelect >>> .vs__dropdown-toggle,
.mySelect >>> .vs__dropdown-menu {
  text-align: center;
  padding-bottom: 2px;
  font-size: 12px;
  border: none;
  border-radius: 0;
  border-bottom: 1px solid rgba(60, 60, 60, 0.26);
}

.mySelect >>> .vs__dropdown-toggle > .vs__actions {
  display: none;
}

.mySelect >>> .vs__dropdown-toggle > .vs__selected-options > .vs__selected {
  background-color: white;
  margin: 0 2px;
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
.dashboard.container {
  height: calc(100% - 76px);
  padding-left: 0px;
  padding-right: 0px;
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
.file-uploads {
  overflow: hidden;
  position: relative;
  text-align: center;
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
</style>

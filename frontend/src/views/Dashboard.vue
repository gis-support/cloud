<template>
  <div class="dashboard container align-center">
    <div class="col-sm-12 pl-0 pr-0 section">
      <h2 class="flex-center container__border--bottom container__border--grey mb-0">
        <div class="p-0 container__border--bottom container__border--red section__header">
          <i class="fa fa-database"></i>
          <span data-i18n="dashboard.title"> {{$i18n.t('dashboard.title.vectorLayersList')}}</span>
        </div>
        <div class="p-0">
          <input type="text" class="form-control container__input" v-model="searchVector"
            :placeholder="$i18n.t('dashboard.placeholder.layersFilter')">
        </div>
      </h2>
      <div class="section__content heading-block heading-block-main">
        <span data-toggle="modal" data-target="#addLayerModal" data-type="vectorLayer">
          <i class="fa fa-plus-circle fa-lg green pt-10" style="margin-right:5px;"></i>
          <a class="green section__content--add">{{$i18n.t('dashboard.list.addLayer')}}</a>
        </span>

        <div class="loading-overlay pt-10 pb-10" v-if="!vectorLayersList">
          <div class="loading-indicator mb-10"><h4>{{$i18n.t('default.loading')}}</h4>
          <i class="fa fa-lg fa-spin fa-spinner"></i></div>
        </div>

        <div v-if="filteredListVector.length == 0" class="pt-10 pb-10">
          {{$i18n.t('default.noLayers')}}
        </div>
        <template v-else v-for="(val, key) in filteredListVector">
          <div class="mb-0" :key="key">
            <div class="panel-heading pl-0 pr-0">
              <h4 class="panel-title flex-center">
                <span class="panel-title__names">
                  <i class="icon-li fa fa-map-o fa-lg mr-5"></i>
                  <span class="bold" href="#"
                    @click="$router.push(
                      {
                        name: 'feature_manager',
                        params: {
                          layerId: val.id,
                          layerName: val.name,
                          vectorLayersList
                        }
                      },
                      setAttachmentsLayer(val.id)
                      )">
                    {{ val.name }}
                  </span>
                  <span class="desc-sm">
                    {{ val.team }}
                  </span>
                </span>
                <span class="panel-title__tools">
                  <i class="fa fa-cog fa-lg yellow icon-hover" data-toggle="modal"
                  data-target="#layerSettingsModal" data-placement="top"
                  :title="$i18n.t('default.settings')" @click="setEditedLayer('vector', key)"></i>
                  <i class="fa fa-trash fa-lg red icon-hover" data-toggle="tooltip"
                    data-placement="top" :title="$i18n.t('default.delete')"
                    @click="deleteLayer(val)"></i>
                </span>
              </h4>
            </div>
          </div>
        </template>
      </div>
    </div>

    <div class="col-sm-12 pl-0 pr-0 section">
      <h2 class="flex-center container__border--bottom container__border--grey mb-0">
        <div class="p-0 container__border--bottom container__border--red section__header">
          <i class="fa fa-database"></i>
          <span data-i18n="dashboard.title">
            {{$i18n.t('dashboard.title.externalSourcesList')}}
          </span>
        </div>
        <div class="p-0">
          <input type="text" class="form-control container__input" v-model="searchExtSources"
            :placeholder="$i18n.t('dashboard.placeholder.externalSourcesFilter')">
        </div>
      </h2>
      <div class="section__content heading-block heading-block-main">
        <span data-toggle="modal" data-target="#addLayerWmsModal" data-type="externalLayer">
          <i class="fa fa-plus-circle fa-lg green pt-10" style="margin-right:5px;"></i>
          <a class="green section__content--add">{{$i18n.t('dashboard.list.addService')}}</a>
        </span>

        <div class="loading-overlay pt-10 pb-10" v-if="!servicesList">
          <div class="loading-indicator mb-10"><h4>{{$i18n.t('default.loading')}}</h4>
          <i class="fa fa-lg fa-spin fa-spinner"></i></div>
        </div>

        <div v-if="filteredServicesList.length == 0" class="pt-10 pb-10">
          {{$i18n.t('default.noLayers')}}
        </div>
        <template v-else v-for="(val, key) in filteredServicesList">
          <div class="mb-0" :key="key">
            <div class="panel-heading pl-0 pr-0">
              <h4 class="panel-title flex-center">
                <span class="panel-title__names">
                  <i class="icon-li fa fa-map-o fa-lg mr-5"></i>
                  <span class="bold panel-title__wms">
                    {{ val.name }}
                  </span>
                  <span class="desc-sm" :title="val.url">
                    <strong>URL</strong>: {{ val.url | maxLength }}
                  </span>
                  <span class="desc-sm" :title="val.group">
                    <strong>{{$i18n.t('default.group')}}</strong>: {{ val.group }}
                  </span>
                  <span class="desc-sm" :title="val.layers">
                    <strong>{{$i18n.t('default.layers')}}</strong>: {{ val.layers | maxLength }}
                  </span>
                </span>
                <span class="panel-title__tools">
                  <!-- <i class="fa fa-cog fa-lg yellow icon-hover" data-toggle="tooltip"
                    data-placement="top" :title="$i18n.t('default.settings')"></i> -->
                  <i class="fa fa-trash fa-lg red icon-hover" data-toggle="tooltip"
                    data-placement="top" :title="$i18n.t('default.delete')"
                    @click="deleteService(val.id)"></i>
                </span>
              </h4>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!--MODAL DODAWANIA WARSTW-->
    <div class="modal fade" data-backdrop="static" id="addLayerModal" tabindex="-1" role="dialog"
      aria-hidden="true" ref="addLayerModal">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">{{$i18n.t('dashboard.modal.addLayer')}}</h4>
          </div>
          <div class="modal-body">
            <div style="display: flex">
              <label class="control-label col-sm-4 pl-0">
                {{$i18n.t('dashboard.modal.layerName')}}
              </label>
              <input type="text" class="form-control" v-model="vectorLayerName">
            </div>
            <div style="display: flex" class="pt-10">
              <label class="control-label col-sm-4 pl-0">
                {{$i18n.t('dashboard.modal.epsg')}}
              </label>
              <input
                class="form-control"
                v-model="epsg"
                @keypress="isNumber($event)"
                :disabled="isEpsgAutomatic"
                :title="isEpsgAutomatic ? $i18n.t('upload.automaticEpsg') : null"
              >
            </div>
            <div class="pt-10">
              <vue-dropzone
                ref="dropzoneUploadLayer"
                id="dropzone"
                :options="dropzoneOptions"
                @vdropzone-error="sendingError"
                @vdropzone-sending-multiple="sendingEvent"
                @vdropzone-success-multiple="sendingSuccess"
              />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal"
              @click="clearUploadFiles" ref="closeModalBtn">
              {{$i18n.t('default.cancel')}}
            </button>
            <button type="button" class="btn btn-success" @click="sendVectorLayer"
              :disabled="!vectorLayerName"
            >
              {{$i18n.t('default.save')}}
            </button>
          </div>
        </div>
      </div>
    </div>
    <!--KONIEC MODALA-->

    <!--MODAL DODAWANIA USŁUG-->
    <div class="modal fade" data-backdrop="static" id="addLayerWmsModal" tabindex="-2" role="dialog"
      aria-hidden="true" ref="addLayerWmsModal">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">{{$i18n.t('dashboard.modal.addLayerWms')}}</h4>
          </div>
          <div class="modal-body">
            <div style="display: flex">
              <label class="control-label col-sm-4" style="width: 150px">
                {{$i18n.t('dashboard.modal.serviceName')}}
              </label>
              <input type="text" class="form-control" v-model="serviceName">
            </div>
            <div class="pt-10" style="display: flex;">
              <label class="control-label col-sm-4" style="width: 160px">
                {{$i18n.t('dashboard.modal.layerAddress')}}
              </label>
              <input type="text" class="form-control" v-model="serviceUrl">
              <i
                class="fa fa-cloud-download fetch-wms-icon"
                :class="{disabled: serviceUrl.length < 1}"
                :title="$i18n.t('default.downloadAvailableLayers')"
                aria-hidden="true"
                @click="fetchWms">
              </i>
            </div>
            <div class="pt-10" v-if="fetchedLayers.length > 0">
              <ul class="select-layer-list">
                <li v-for="layer in fetchedLayers" :key="layer">
                  <label class="checkbox-inline">
                    <input type="checkbox" id="checkbox" :value="layer" v-model="selectedLayers">
                  </label>
                </li>
              </ul>
            </div>
            <div class="loading-overlay pt-10 pb-10" style="text-align: center;"
              v-if="fetchedLayers.length === 0 && isFetching">
              <div class="loading-indicator mb-10"><h4>{{$i18n.t('default.loading')}}</h4>
              <i class="fa fa-lg fa-spin fa-spinner"></i></div>
            </div>
            <hr/>
            <div class="pt-10" v-if="fetchedLayers.length > 0">
              <label class="checkbox-inline">
                <input type="checkbox" id="checkbox" v-model="isServicePublic">
                {{$i18n.t('dashboard.modal.servicePublic')}}
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default"
              data-dismiss="modal"
              ref="closeModalWmsBtn"
              @click="clearServicesModal"
            >
              {{$i18n.t('default.cancel')}}
            </button>
            <button type="button"
              class="btn btn-success"
              :disabled="selectedLayers.length === 0 ||
                serviceName.length === 0 ||
                selectedLayers.length === 0"
              @click="addService"
            >
              {{$i18n.t('default.save')}}
            </button>
          </div>
        </div>
      </div>
    </div>
    <!--KONIEC MODALA-->
  </div>
</template>

<script>
import vue2Dropzone from 'vue2-dropzone';
import 'vue2-dropzone/dist/vue2Dropzone.min.css';
import WMSCapabilities from 'ol/format/WMSCapabilities';

export default {
  name: 'dashboard',
  data: vm => ({
    currentEditedLayer: undefined,
    epsg: undefined,
    fetchedLayers: [],
    isEpsgAutomatic: true,
    isFetching: false,
    isSendingError: false,
    isServicePublic: false,
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
        save: true,
      },
    },
    searchExtSources: '',
    searchVector: '',
    serviceUrl: '',
    serviceName: '',
    selectedLayers: [],
    vectorLayerName: '',
    vectorLayersList: undefined,
    dropzoneOptions: {
      url: `${vm.$store.getters.getApiUrl}/layers?token=${localStorage.getItem('token')}`,
      addRemoveLinks: true,
      autoProcessQueue: false,
      dictCancelUpload: vm.$i18n.t('upload.cancelUpload'),
      dictRemoveFile: vm.$i18n.t('upload.removeFile'),
      dictDefaultMessage: vm.$i18n.t('upload.defaultMessage'),
      thumbnailWidth: 150,
      maxFilesize: 256,
      timeout: 180000,
      uploadMultiple: true,
      parallelUploads: 10,
      methods: 'post',
      success(file, response) {
        vm.$alertify.success(vm.$i18n.t('upload.uploadSuccess'));
        const newLayer = { id: response.layers.id, name: response.layers.name };
        if (!vm.vectorLayersList.find(el => el.id === newLayer.id)) {
          vm.vectorLayersList.push(newLayer);
        }
        vm.$refs.closeModalBtn.click();
      },
    },
  }),
  components: {
    vueDropzone: vue2Dropzone,
  },
  computed: {
    featureAttachments() {
      return this.$store.getters.getFeatureAttachments;
    },
    filteredServicesList() {
      if (!this.servicesList) {
        return false;
      }
      return this.servicesList.filter(
        layer => layer.name.toLowerCase().includes(this.searchExtSources.toLowerCase()),
      );
    },
    filteredListVector() {
      if (!this.vectorLayersList) {
        return false;
      }
      return this.vectorLayersList.filter(
        layer => layer.name.toLowerCase().includes(this.searchVector.toLowerCase()),
      );
    },
    servicesList() {
      return this.$store.getters.getServices;
    },
  },
  filters: {
    maxLength: (val) => {
      if (val.length > 50) {
        return `${val.slice(0, 50)}...`;
      }
      return val;
    },
  },
  methods: {
    async addService() {
      const r = await this.$store.dispatch('addService', {
        layers: this.selectedLayers.join(','),
        name: this.serviceName,
        public: this.isServicePublic,
        url: this.serviceUrl,
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
      this.$alertify.confirm(this.$i18n.t('dashboard.modal.deleteService'), async () => {
        const r = await this.$store.dispatch('deleteService', sid);
        if (r.status === 200) {
          this.$alertify.success(this.$i18n.t('default.deleted'));
          this.$store.commit('deleteService', sid);
        } else {
          this.$i18n.t('default.error');
        }
      }, () => {})
        .set({ title: this.$i18n.t('dashboard.modal.deleteServiceTitle') })
        .set({ labels: { ok: this.$i18n.t('default.delete'), cancel: this.$i18n.t('default.cancel') } });
    },
    async getLayers() {
      const r = await this.$store.dispatch('getLayers');
      this.vectorLayersList = r.body.layers;
    },
    async getServices() {
      const r = await this.$store.dispatch('getServices');
      this.$store.commit('setServices', r.body.services);
    },
    async fetchWms() {
      this.isFetching = true;
      const parser = new WMSCapabilities();
      const url = `https://divi.io/wms_proxy/${this.serviceUrl}?request=GetCapabilities&service=WMS`;
      fetch(url).then(response => response.text()).then((text) => {
        const result = parser.read(text);
        this.fetchedLayers = result.Capability.Layer.Layer.map(el => el.Name);
        this.isFetching = false;
      });
    },
    async setEditedLayer(layType, key) {
      if (layType === 'vector') {
        this.currentEditedLayer = Object.assign({}, this.vectorLayersList[key]);
      }
      this.$router.push({
        name: 'settings',
        params: {
          layerId: this.currentEditedLayer.id,
          layer: this.currentEditedLayer,
          vectorLayersList: this.vectorLayersList,
        },
      });
    },
    clearServicesModal() {
      document.querySelector('#addLayerWmsModal button.btn.btn-default').click();
      this.fetchedLayers = [];
      this.selectedLayers = [];
      this.serviceName = '';
      this.isServicePublic = false;
      this.serviceUrl = '';
    },
    clearUploadFiles() {
      this.$refs.dropzoneUploadLayer.removeAllFiles();
      this.vectorLayerName = '';
      this.isEpsgAutomatic = true;
    },
    deleteLayer(el) {
      this.$alertify.confirm(this.$i18n.t('dashboard.modal.deleteLayerContent'), async () => {
        const r = await this.$store.dispatch('deleteLayer', el.id);
        if (r.status === 200) {
          this.vectorLayersList = this.vectorLayersList.filter(lay => lay.id !== el.id);
          this.$alertify.success(this.$i18n.t('default.deleted'));
        } else {
          this.$alertify.error(this.$i18n.t('default.error'));
        }
      }, () => {})
        .set({ title: this.$i18n.t('dashboard.modal.deleteLayerTitle') })
        .set({ labels: { ok: this.$i18n.t('default.delete'), cancel: this.$i18n.t('default.cancel') } });
    },
    isNumber(evt) {
      const e = (evt) || window.event;
      const charCode = (e.which) ? e.which : e.keyCode;
      if ((charCode > 31 && (charCode < 48 || charCode > 57))) {
        e.preventDefault();
        return false;
      }
      return true;
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
      this.$refs.dropzoneUploadLayer.processQueue();
    },
    setAttachmentsLayer(lid) {
      if (!Object.keys(this.featureAttachments).includes(lid)) {
        this.$store.commit('setAttachmentsLayer', lid);
      }
    },
  },
  async mounted() {
    // console.log(this.$swagger);
    this.getLayers();
    this.getServices();
    this.$store.commit('setDefaultGroup', process.env.VUE_APP_DEFAULT_GROUP);
  },
};
</script>

<style scoped>
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
.desc-sm {
  color: #b5b5b5;
  font-family: "Open Sans","Trebuchet MS",arial,sans-serif;
  font-size: 12px;
  letter-spacing: -1px;
  line-height: 1.75em;
  margin-left: 5px;
}
.fetch-wms-icon {
  font-size:26px;
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
.heading-block:after, .heading-block:before {
  display: none;
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
  height: 50%;
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

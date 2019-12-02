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
          <a class="green">{{$i18n.t('dashboard.list.addLayer')}}</a>
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
                  <span class="bold" href="#">
                    {{ val.name }}
                  </span>
                  <span class="desc-sm">
                    {{ val.team }}
                  </span>
                </span>
                <span class="panel-title__tools">
                  <i class="fa fa-cog fa-lg yellow icon-hover" data-toggle="modal"
                  data-target="#layerSettingsModal" data-placement="top"
                  title="Ustawienia" @click="setEditedLayer('vector', key)"></i>
                  <i class="fa fa-trash fa-lg red icon-hover" data-toggle="tooltip"
                    data-placement="top" title="Usuń" @click="deleteLayer(val)"></i>
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
        <span data-toggle="modal" data-target="#addLayerModal" data-type="externalLayer">
          <i class="fa fa-plus-circle fa-lg green pt-10" style="margin-right:5px;"></i>
          <a class="green">{{$i18n.t('dashboard.list.addLayer')}}</a>
        </span>

        <div class="loading-overlay pt-10 pb-10" v-if="!externalLayersList">
          <div class="loading-indicator mb-10"><h4>{{$i18n.t('default.loading')}}</h4>
          <i class="fa fa-lg fa-spin fa-spinner"></i></div>
        </div>

        <div v-if="filteredListExternal.length == 0" class="pt-10 pb-10">
          {{$i18n.t('default.noLayers')}}
        </div>
        <template v-else v-for="(val, key) in filteredListExternal">
          <div class="mb-0" :key="key">
            <div class="panel-heading pl-0 pr-0">
              <h4 class="panel-title flex-center">
                <span class="panel-title__names">
                  <i class="icon-li fa fa-map-o fa-lg mr-5"></i>
                  <span class="bold" href="#">
                    {{ val.name }}
                  </span>
                  <span class="desc-sm">
                    {{ val.layType }}
                  </span>
                  <span class="desc-sm">
                    {{ val.url }}
                  </span>
                </span>
                <span class="panel-title__tools">
                  <i class="fa fa-cog fa-lg yellow icon-hover" data-toggle="tooltip"
                    data-placement="top" title="Ustawienia"></i>
                  <i class="fa fa-trash fa-lg red icon-hover" data-toggle="tooltip"
                    data-placement="top" title="Usuń"></i>
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
              <label class="control-label col-sm-4">{{$i18n.t('dashboard.modal.layerName')}}</label>
              <input type="text" class="form-control" v-model="vectorLayerName">
            </div>
            <div class="pt-10">
              <vue-dropzone
                ref="dropzoneUploadLayer"
                id="dropzone"
                :options="dropzoneOptions"
                @vdropzone-sending-multiple="sendingEvent"
              />
            </div>
          </div>
          <div class="modal-footer">
            <span v-if="isUploadSuccessful">
              <button type="button" class="btn btn-default" data-dismiss="modal"
                @click="clearUploadFiles">
                {{$i18n.t('default.close')}}
              </button>
            </span>
            <span v-else>
              <button type="button" class="btn btn-default" data-dismiss="modal"
                @click="clearUploadFiles">
                {{$i18n.t('default.cancel')}}
              </button>
              <button type="button" class="btn btn-success" @click="sendVectorLayer">
                {{$i18n.t('default.save')}}
              </button>
            </span>
          </div>
        </div>
      </div>
    </div>
    <!--KONIEC MODALA-->

    <!--MODAL USTAWIENIA WARSTWY-->
    <div class="modal fade" data-backdrop="static" id="layerSettingsModal" tabindex="-1"
      role="dialog" aria-hidden="true" ref="layerSettingsModal">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content" v-if="currentEditedLayer">
          <div class="modal-header">
            <h4 class="modal-title">
              {{$i18n.t('dashboard.modal.settingsLayer')}}
            </h4>
          </div>
          <div class="modal-body">
            <div style="display: flex">
              <label class="control-label col-sm-4">{{$i18n.t('dashboard.modal.layerName')}}</label>
              <input type="text" class="form-control mr-5"
                v-model="currentEditedLayer.name">
              <button type="button" class="btn btn-success" @click="saveLayerName">
                {{$i18n.t('default.saveName')}}
              </button>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal"
              @click="closeSettingsModal">
              {{$i18n.t('default.close')}}
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

export default {
  name: 'dashboard',
  data: vm => ({
    currentEditedLayer: undefined,
    currentLayerSettings: [],
    isUploadSuccessful: false,
    searchExtSources: '',
    searchVector: '',
    vectorLayerName: '',
    vectorLayersList: undefined,
    externalLayersList: [
      { name: 'Nadleśnictwa', layType: 'WMS', url: 'www.url.pl/wms' },
      { name: 'Podtopienia', layType: 'WMTS', url: 'www.url.pl/wmts' },
    ],
    dropzoneOptions: {
      url: `${vm.$store.getters.getApiUrl}/layers?token=${vm.$store.getters.getToken}`,
      addRemoveLinks: true,
      autoProcessQueue: false,
      dictCancelUpload: vm.$i18n.t('upload.cancelUpload'),
      dictRemoveFile: vm.$i18n.t('upload.removeFile'),
      dictDefaultMessage: vm.$i18n.t('upload.defaultMessage'),
      thumbnailWidth: 150,
      maxFilesize: 2,
      uploadMultiple: true,
      parallelUploads: 10,
      methods: 'post',
      acceptedFiles: '.shp,.shx,.dbf,.prj,.geojson',
      success(file, response) {
        vm.$alertify.success(vm.$i18n.t('upload.uploadSuccess'));
        vm.changeUploadSuccess(true);
        const newLayer = { id: response.layers.id, name: response.layers.name };
        if (!vm.vectorLayersList.find(el => el.id === newLayer.id)) {
          vm.vectorLayersList.push(newLayer);
        }
      },
      error() {
        vm.$alertify.error(vm.$i18n.t('upload.uploadError'));
      },
    },
  }),
  components: {
    vueDropzone: vue2Dropzone,
  },
  computed: {
    filteredListExternal() {
      if (!this.externalLayersList) {
        return false;
      }
      return this.externalLayersList.filter(
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
  },
  methods: {
    changeUploadSuccess(isSuccessful) {
      this.isUploadSuccessful = isSuccessful;
    },
    closeSettingsModal() {
      this.currentEditedLayer = {};
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
    async getLayers() {
      const r = await this.$store.dispatch('getLayers');
      this.vectorLayersList = r.body.layers;
    },
    async saveLayerName() {
      const layIndex = this.vectorLayersList.findIndex(el => el.id === this.currentEditedLayer.id);
      const payload = {
        body: {
          layer_name: this.currentEditedLayer.name,
        },
        lid: this.currentEditedLayer.id,
      };

      const r = await this.$store.dispatch('changeLayerName', payload);
      if (r.status === 200) {
        this.$alertify.success(this.$i18n.t('dashboard.modal.layerNameChanged'));
        this.$set(
          this.vectorLayersList[layIndex], 'id', r.obj.settings,
        ); // zmiana id
        this.$set(
          this.vectorLayersList[layIndex], 'name', this.currentEditedLayer.name,
        ); // zmiana nazwy
      } else {
        this.$i18n.t('default.error');
      }
    },
    async setEditedLayer(layType, key) {
      if (layType === 'vector') {
        this.currentEditedLayer = Object.assign({}, this.vectorLayersList[key]);
      }
      const r = await this.$store.dispatch('getLayerColumns', this.currentEditedLayer.id);
      this.currentLayerSettings = r.body.settings;
    },
    clearUploadFiles() {
      this.$refs.dropzoneUploadLayer.removeAllFiles();
      this.isUploadSuccessful = false;
    },
    sendingEvent(files, xhr, formData) {
      formData.append('name', this.vectorLayerName);
    },
    sendVectorLayer() {
      if (this.vectorLayerName === '') {
        const msg = this.$i18n.t('upload.noLayerNameError');
        this.$alertify.error(msg);
        return;
      }
      this.$refs.dropzoneUploadLayer.processQueue();
    },
  },
  mounted() {
    // console.log(this.$swagger);
    this.getLayers();
  },
};
</script>

<style scoped>
.btn-upload {
  margin-right: 20px;
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
.panel-title__tools i:not(:last-child) {
  margin-right: 5px;
}
.section {
  height: 50%;
}
.section__content.heading-block.heading-block-main {
  overflow-y: auto;
  max-height: calc(100% - 50px);
}
.section__header {
  padding-bottom: 15px;
  margin-bottom: -1px;
}
</style>

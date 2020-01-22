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
                  <span class="bold" href="#"
                    @click="$router.push(
                      {
                        name: 'feature_manager',
                        params: { layerId: val.id, layerName: val.name}
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
                    data-placement="top" :title="$i18n.t('default.settings')"></i>
                  <i class="fa fa-trash fa-lg red icon-hover" data-toggle="tooltip"
                    data-placement="top" :title="$i18n.t('default.delete')"></i>
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
            <button type="button" class="btn btn-default" data-dismiss="modal"
              @click="clearUploadFiles" ref="closeModalBtn">
              {{$i18n.t('default.cancel')}}
            </button>
            <button type="button" class="btn btn-success" @click="sendVectorLayer">
              {{$i18n.t('default.save')}}
            </button>
          </div>
        </div>
      </div>
    </div>
    <!--KONIEC MODALA-->

    <!--MODAL DODAWANIA USŁUG-->
    <div class="modal fade" data-backdrop="static" id="addLayerWmsModal" tabindex="-1" role="dialog"
      aria-hidden="true" ref="addLayerWmsModal">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">{{$i18n.t('dashboard.modal.addLayerWms')}}</h4>
          </div>
          <div class="modal-body">
            <div style="display: flex">
              <label class="control-label col-sm-4">
                {{$i18n.t('dashboard.modal.layerAddress')}}
              </label>
              <input type="text" class="form-control" v-model="wmsAddress">
              <i
                class="fa fa-cloud-download fetch-wms-icon"
                :class="{disabled: wmsAddress.length < 1}"
                :title="$i18n.t('default.downloadAvailableLayers')"
                aria-hidden="true"
                @click="fetchWms">
              </i>
            </div>
            <div class="pt-10">

            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal"
              ref="closeModalBtn">
              {{$i18n.t('default.cancel')}}
            </button>
            <button type="button" class="btn btn-success">
              {{$i18n.t('default.save')}}
            </button>
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
            <h4 class="text-left">{{$i18n.t('dashboard.modal.layerName')}}</h4>
            <div style="display: flex">
              <input type="text" class="form-control mr-5"
                v-model="currentEditedLayer.name">
              <button type="button" class="btn btn-success" @click="saveLayerName">
                {{$i18n.t('default.saveName')}}
              </button>
            </div>
            <div class="pt-10">
              <h4 class="text-left">
                {{$i18n.t('dashboard.modal.layerColumns')}}
                <i class="fa fa-chevron-up" @click="toggleColumnsSection(false)"
                  v-if="isColumnsVisible" aria-hidden="true" style="cursor: pointer;"
                  :title="$i18n.t('dashboard.modal.hideColumns')"
                ></i>
                <i class="fa fa-chevron-down" @click="toggleColumnsSection(true)"
                  v-if="!isColumnsVisible" aria-hidden="true" style="cursor: pointer;"
                  :title="$i18n.t('dashboard.modal.showColumns')"
                ></i>
              </h4>
              <table v-if="isColumnsVisible" class="table table-striped table-bordered table-hover">
                <thead>
                  <tr role="row">
                    <th class="text-centered">{{$i18n.t('default.name')}}</th>
                    <th class="text-centered">{{$i18n.t('default.dataType')}}</th>
                    <th class="text-centered">{{$i18n.t('default.actions')}}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(value, name, index) in currentLayerSettings.columns" :key="index">
                    <td>{{name}}</td>
                    <td>{{value}}</td>
                    <td>
                      <i class="fa fa-trash fa-lg red icon-hover" :title="$i18n.t('default.delete')"
                        @click="deleteColumn(name)"></i>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="pt-10">
              <h4 class="text-left">{{$i18n.t('dashboard.modal.addColumn')}}</h4>
              <div style="display: flex">
                <input type="text" class="form-control mr-5"
                 placeholder="Nazwa kolumny" v-model="newColumnName">
                <select class="form-control mr-5" name="column-types-select"
                  v-model="newColumnType">
                  <option value="" selected>{{$i18n.t('dashboard.modal.chooseColumnType')}}</option>
                  <option v-for="colType in columnTypes" :key="colType" :value="colType">
                    {{colType}}
                  </option>
                </select>
                <button type="button" class="btn btn-success" @click="addNewColumn">
                  {{$i18n.t('default.add')}}
                </button>
              </div>
            </div>
            <div class="pt-10">
              <h4 class="text-left">Styl warstwy</h4>
              <div style="display: flex; justify-content: space-around;">
                <div style="display: flex;">
                  <label class="color-picker__label">
                    {{$i18n.t('dashboard.modal.strokeColor')}}
                  </label>
                  <div class="color-picker--stroke" style="height:50px; width:50px"></div>
                </div>
                <div style="display: flex;">
                  <label class="color-picker__label">
                    {{$i18n.t('dashboard.modal.fillColor')}}
                  </label>
                  <div class="color-picker--fill" style="height:50px; width:50px"></div>
                </div>
                <div
                  style="display: flex;"
                  v-if="Object.keys(styles).includes(currentEditedLayer.id)"
                >
                  <label class="color-picker__label">
                    {{$i18n.t('dashboard.modal.strokeWidth')}}
                  </label>
                  <input type="number" class="form-control"
                    min="1" max="9" step="1"
                    style="width: 50px; position: relative; top: -5px"
                    v-model="styles[currentEditedLayer.id]['stroke-width']">
                </div>
                <button type="button"
                  class="btn btn-success"
                  @click="saveStyle"
                  style="position: relative;top: -6px;right: -13px;"
                >
                  {{$i18n.t('default.save')}}
                </button>
              </div>
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
import Pickr from '@simonwep/pickr';
import '@simonwep/pickr/dist/themes/nano.min.css';
import WMSCapabilities from 'ol/format/WMSCapabilities';

export default {
  name: 'dashboard',
  data: vm => ({
    currentEditedLayer: undefined,
    currentLayerSettings: [],
    isColumnsVisible: true,
    newColumnName: undefined,
    newColumnType: '',
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
    styles: {},
    vectorLayerName: '',
    vectorLayersList: undefined,
    wmsAddress: '',
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
      maxFilesize: 256,
      timeout: 180000,
      uploadMultiple: true,
      parallelUploads: 10,
      methods: 'post',
      acceptedFiles: '.shp,.shx,.dbf,.prj,.geojson',
      success(file, response) {
        vm.$alertify.success(vm.$i18n.t('upload.uploadSuccess'));
        const newLayer = { id: response.layers.id, name: response.layers.name };
        if (!vm.vectorLayersList.find(el => el.id === newLayer.id)) {
          vm.vectorLayersList.push(newLayer);
        }
        vm.$refs.closeModalBtn.click();
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
    columnTypes() {
      return this.$store.getters.getColumnTypes;
    },
    featureAttachments() {
      return this.$store.getters.getFeatureAttachments;
    },
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
    async addNewColumn() {
      if (!this.newColumnName || !this.newColumnType) {
        this.$alertify.error(this.$i18n.t('dashboard.modal.noNameOrType'));
        return;
      }
      const payload = {
        body: {
          column_name: this.newColumnName,
          column_type: this.newColumnType,
        },
        lid: this.currentLayerSettings.id,
      };
      const r = await this.$store.dispatch('changeLayer', payload);
      if (r.status === 200) {
        this.currentLayerSettings.columns[this.newColumnName] = this.newColumnType;
        this.newColumnName = undefined;
        this.newColumnType = '';
        this.$alertify.success(this.$i18n.t('dashbaord.modal.columnAdded'));
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    async deleteColumn(colName) {
      this.$alertify.confirm(this.$i18n.t('dashboard.modal.deleteLayerColumn'), async () => {
        const payload = {
          body: { column_name: colName },
          lid: this.currentEditedLayer.id,
        };

        const r = await this.$store.dispatch('deleteColumn', payload);
        if (r.status === 200) {
          this.$alertify.success(this.$i18n.t('default.deleted'));
          this.$delete(this.currentLayerSettings.columns, colName);
        } else {
          this.$i18n.t('default.error');
        }
      }, () => {})
        .set({ title: this.$i18n.t('dashboard.modal.deleteColumnTitle') })
        .set({ labels: { ok: this.$i18n.t('default.delete'), cancel: this.$i18n.t('default.cancel') } });
    },
    async getLayers() {
      const r = await this.$store.dispatch('getLayers');
      this.vectorLayersList = r.body.layers;
    },
    async fetchWms() {
      const parser = new WMSCapabilities();
      const url = `https://divi.io/wms_proxy/${this.wmsAddress}?request=GetCapabilities&service=WMS`;
      fetch(url).then(response => response.text()).then((text) => {
        const result = parser.read(text);
        console.log(result);
      });
    },
    async saveLayerName() {
      const layIndex = this.vectorLayersList.findIndex(el => el.id === this.currentEditedLayer.id);
      const payload = {
        body: {
          layer_name: this.currentEditedLayer.name,
        },
        lid: this.currentEditedLayer.id,
      };

      const r = await this.$store.dispatch('changeLayer', payload);
      if (r.status === 200) {
        this.$alertify.success(this.$i18n.t('dashboard.modal.layerNameChanged'));
        // zmiana id
        this.$set(
          this.vectorLayersList[layIndex], 'id', r.obj.settings,
        );
        this.$set(
          this.currentLayerSettings, 'id', r.obj.settings,
        );
        // zmiana nazwy
        this.$set(
          this.vectorLayersList[layIndex], 'name', this.currentEditedLayer.name,
        );
        this.$set(
          this.currentLayerSettings, 'name', this.currentEditedLayer.name,
        );
      } else {
        this.$i18n.t('default.error');
      }
    },
    async saveStyle() {
      const r = await this.$store.dispatch('saveStyle', {
        lid: this.currentEditedLayer.id,
        body: this.styles[this.currentEditedLayer.id],
      });
      if (r.status === 200) {
        this.$alertify.success(this.$i18n.t('default.success'));
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    async setEditedLayer(layType, key) {
      if (layType === 'vector') {
        this.currentEditedLayer = Object.assign({}, this.vectorLayersList[key]);
      }
      const r = await this.$store.dispatch('getLayerColumns', this.currentEditedLayer.id);
      this.currentLayerSettings = r.body.settings;

      const styleResponse = await this.$store.dispatch(
        'getLayerStyle', this.currentEditedLayer.id,
      );
      this.$set(this.styles, this.currentEditedLayer.id, styleResponse.body.style);

      this.$nextTick(() => {
        if (!document.querySelector('.color-picker--fill')) return;
        const pickrFill = Pickr.create({
          el: '.color-picker--fill',
          container: 'body',
          theme: 'nano',
          default: `rgba(${this.styles[this.currentEditedLayer.id]['fill-color']})`,
          defaultRepresentation: 'RGBA',
          position: 'top-start',
          components: this.pickrComponents,
          strings: {
            save: 'Zapisz',
          },
        });

        const pickrStroke = Pickr.create({
          el: '.color-picker--stroke',
          container: 'body',
          theme: 'nano',
          default: `rgba(${this.styles[this.currentEditedLayer.id]['stroke-color']})`,
          defaultRepresentation: 'RGBA',
          position: 'top-start',
          components: this.pickrComponents,
          strings: {
            save: 'Zapisz',
          },
        });

        pickrFill.on('save', (color) => {
          const col = color.toRGBA().map(el => parseInt(el, 10));
          this.$set(this.styles[this.currentEditedLayer.id], 'fill-color', col.join(','));
        });

        pickrStroke.on('save', (color) => {
          const col = color.toRGBA().map(el => parseInt(el, 10));
          this.$set(this.styles[this.currentEditedLayer.id], 'stroke-color', col.join(','));
        });
      });
    },
    clearUploadFiles() {
      this.$refs.dropzoneUploadLayer.removeAllFiles();
      this.vectorLayerName = '';
    },
    closeSettingsModal() {
      this.currentEditedLayer = {};
      this.newColumnName = undefined;
      this.newColumnType = '';
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
    setAttachmentsLayer(lid) {
      if (!Object.keys(this.featureAttachments).includes(lid)) {
        this.$store.commit('setAttachmentsLayer', lid);
      }
    },
    toggleColumnsSection(isVisible) {
      this.isColumnsVisible = isVisible;
    },
  },
  async mounted() {
    // console.log(this.$swagger);
    this.getLayers();
    const r = await this.$store.dispatch('getUserGroups');
    this.$store.commit('setDefaultGroup', r.body.groups[0]);
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
.panel-title__names .bold:hover {
  cursor: pointer !important;
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
.text-centered {
  text-align: center;
}
.text-left {
  text-align: left;
}
</style>

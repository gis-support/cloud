<template>
  <div class="container">
    <div class="col-md-3 layout-sidebar">
      <ul id="myTab" class="nav nav-layout-sidebar nav-stacked">
        <li class="active">
          <a href="#info-tab" data-toggle="tab" @click="setActiveTab('info-tab')">
          <i class="fa fa-info-circle"></i>
          &nbsp;&nbsp;<span>{{$i18n.t('settings.layerInfo')}}</span>
          </a>
        </li>
        <li>
          <a href="#style-tab" data-toggle="tab" @click="setActiveTab('style-tab')">
          <i class="fa fa-map-pin"></i>
          &nbsp;&nbsp;<span>{{$i18n.t('settings.symbolization')}}</span>
          </a>
        </li>
        <li class="disabled">
          <a href="#labels-tab" data-toggle="tab"
            @click.prevent.stop @click="setActiveTab('labels-tab')">
          <i class="fa fa-map-pin"></i>
          &nbsp;&nbsp;<span>{{$i18n.t('settings.labels')}}</span>
          </a>
        </li>
      </ul>
    </div>
    <div class="col-md-9 col-sm-8 layout-main">
      <div class="loading-overlay pt-10 pb-10 text-centered" v-if="!isMounted">
        <div class="loading-indicator mb-10"><h4>{{$i18n.t('default.loading')}}</h4>
        <i class="fa fa-lg fa-spin fa-spinner"></i></div>
      </div>
      <div id="settings-content" class="tab-content stacked-content" v-else>
        <div class="heading-block">
          <h3>
            <span data-i18n="layerSettings.title">{{$i18n.t('default.layerSettings')}}: </span>
            <span class="red">{{currentEditedLayer.name}}</span>
            <a @click="goToLayer" :title="$i18n.t('default.goToLayer')">
              <i class="fa fa-chevron-circle-right red icon-hover"></i>
            </a>
          </h3>
        </div>
        <div class="tab-pane in active" id="info-tab" v-if="activeTab === 'info-tab'">
          <h4 class="text-left">{{$i18n.t('dashboard.modal.layerName')}}</h4>
          <div style="display: flex">
            <input type="text" class="form-control mr-5"
              v-model="currentEditedLayer.name">
            <button
              type="button"
              class="btn btn-success"
              @click="saveLayerName"
              :disabled="!currentEditedLayer.name"
            >
              {{$i18n.t('default.saveName')}}
            </button>
          </div>
          <div class="pt-10">
            <h4 class="text-left">{{$i18n.t('dashboard.modal.addColumn')}}</h4>
            <div style="display: flex">
              <input type="text" class="form-control mr-5"
                placeholder="Nazwa kolumny" v-model="newColumnName">
              <select class="form-control mr-5" name="column-types-select"
                v-model="newColumnType">
                <option :value="undefined" selected disabled>
                  {{$i18n.t('dashboard.modal.chooseColumnType')}}
                </option>
                <option v-for="colType in columnTypes" :key="colType" :value="colType">
                  {{colType}}
                </option>
              </select>
              <button
                type="button"
                class="btn btn-success"
                @click="addNewColumn"
                :disabled="!newColumnType || !newColumnName"
              >
                {{$i18n.t('default.add')}}
              </button>
            </div>
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
                  <td class="text-centered">{{name}}</td>
                  <td class="text-centered">{{value}}</td>
                  <td class="text-centered">
                    <i
                      v-if="name !== 'id'"
                      class="fa fa-trash fa-lg red icon-hover"
                      :title="$i18n.t('default.delete')"
                      @click="deleteColumn(name)"></i>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="tab-pane in active" id="style-tab" v-if="activeTab === 'style-tab'">
          <div class="col-md-12 pb-10" style="display: flex;">
            <div class="col-md-6">
              <label class="control-label col-sm-6 pl-0">{{$i18n.t('settings.visType')}}</label>
              <select class="form-control col-sm-4 mt-15" v-model="symbolizationType">
                <option disabled value="">{{$i18n.t('settings.chooseVisualizationType')}}</option>
                <option value="single">{{$i18n.t('default.single')}}</option>
                <option value="categorized">{{$i18n.t('default.categorized')}}</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="control-label col-sm-6 pl-0">{{$i18n.t('settings.objStyle')}}</label>
              <select class="form-control col-sm-4 mt-15" v-model="layerType"
                v-if="layerType === 'point' || layerType === 'square' || layerType === 'triangle'">
                <option disabled value="">{{$i18n.t('settings.chooseObjectStyle')}}</option>
                <option value="point">{{$i18n.t('default.point')}}</option>
                <option value="square">{{$i18n.t('default.square')}}</option>
                <option value="triangle">{{$i18n.t('default.triangle')}}</option>
              </select>
              <select
                class="form-control col-sm-4 mt-15"
                v-model="layerType"
                v-else-if="layerType === 'polygon'"
              >
                <option disabled value="polygon">{{$i18n.t('default.polygon')}}</option>
              </select>
              <select class="form-control col-sm-4 mt-15" v-model="layerType" v-else>
                <option disabled value="">{{$i18n.t('settings.chooseObjectStyle')}}</option>
                <option value="line">{{$i18n.t('default.line')}}</option>
                <option value="dotted">{{$i18n.t('default.dotted')}}</option>
                <option value="dashed">{{$i18n.t('default.dashed')}}</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <div class="col-md-3 color-picker__container" v-if="strokeColor" style="left: -30px;">
              <label class="control-label">Kolor obrysu</label><br>
              <verte
                model="rgb"
                :value="strokeColor"
                v-model="strokeColor"
              ></verte>
            </div>
            <div class="col-md-3 color-picker__container">
              <label class="control-label">Grubość obrysu</label>
              <input
                type="number"
                min="0"
                max="10"
                class="form-control mt-15"
                style="width:50px"
                v-model="strokeWidth"
              />
            </div>
            <div class="col-md-3 color-picker__container" v-if="fillColor">
              <label class="control-label">Kolor wypełnienia</label><br>
              <verte
                model="rgb"
                :value="fillColor"
                v-model="fillColor"
              ></verte>
            </div>
            <div class="col-md-3 color-picker__container" style="right: -20px" v-if="width">
              <label class="control-label">Wielkość punktu</label>
              <input
                type="number"
                min="0"
                max="10"
                class="form-control mt-15"
                style="width:50px"
                v-model="width"
              />
            </div>
          </div>
          <div class="col-md-12 pr-30" style="display:flex; justify-content:flex-end;">
            <button
              type="button"
              class="btn btn-success mt-15"
              @click="saveStyle"
            >
              {{$i18n.t('default.save')}}
            </button>
          </div>
        </div>
        <div class="tab-pane in active" id="labels-tab" v-if="activeTab === 'labels-tab'">
          <p>labels</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import verte from 'verte';
import 'verte/dist/verte.css';

export default {
  name: 'settings',
  components: { verte },
  data: () => ({
    activeTab: 'info-tab',
    currentEditedLayer: undefined,
    currentLayerSettings: undefined,
    fillColor: undefined,
    isColumnsVisible: true,
    isMounted: false,
    layerType: undefined,
    newColumnName: undefined,
    newColumnType: undefined,
    strokeColor: undefined,
    strokeWidth: undefined,
    styles: {},
    symbolizationType: undefined,
    vectorLayersList: undefined,
    width: 0,
  }),
  computed: {
    columnTypes() {
      return this.$store.getters.getColumnTypes;
    },
    featureAttachments() {
      return this.$store.getters.getFeatureAttachments;
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
        this.$alertify.success(this.$i18n.t('dashboard.modal.columnAdded'));
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
    async loadStyle() {
      const lid = this.currentEditedLayer.id;
      const styleResponse = await this.$store.dispatch('getLayerStyle', this.currentEditedLayer.id);
      this.$set(this.styles, this.currentEditedLayer.id, styleResponse.body.style);

      // stroke-width i stroke-color są we wszystkich typach
      this.strokeColor = `rgba(${this.styles[lid]['stroke-color']})`;
      this.strokeWidth = this.styles[lid]['stroke-width'];
      this.layerType = this.styles[lid].type;
      this.symbolizationType = styleResponse.body.style.renderer;

      if (Object.keys(this.styles[lid]).includes('fill-color')) {
        this.fillColor = `rgba(${this.styles[lid]['fill-color']})`;
      }
      if (Object.keys(this.styles[lid]).includes('width')) {
        this.width = this.styles[lid].width;
      }
      console.log(this.strokeColor, this.fillColor);
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
      let fill;
      let stroke;
      if (this.fillColor) {
        fill = this.fillColor.substring( // get rgba between ()
          this.fillColor.lastIndexOf('(') + 1,
          this.fillColor.lastIndexOf(')'),
        );

        if (fill.split(',').length === 3) {
          fill = `${fill},1`;
        }
      }
      if (this.strokeColor) {
        stroke = this.strokeColor.substring( // get rgba between ()
          this.strokeColor.lastIndexOf('(') + 1,
          this.strokeColor.lastIndexOf(')'),
        );

        if (stroke.split(',').length === 3) {
          stroke = `${stroke},1`;
        }
      }

      const r = await this.$store.dispatch('saveStyle', {
        lid: this.currentEditedLayer.id,
        body: {
          type: this.layerType,
          'fill-color': fill,
          'stroke-color': stroke,
          'stroke-width': this.strokeWidth,
          width: this.width,
          renderer: this.symbolizationType,
        },
      });
      if (r.status === 200) {
        this.$alertify.success(this.$i18n.t('default.success'));
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    goToLayer() {
      const lid = this.currentEditedLayer.id;
      if (!Object.keys(this.featureAttachments).includes(lid)) {
        this.$store.commit('setAttachmentsLayer', lid);
      }
      this.$router.push({
        name: 'feature_manager',
        params: {
          layerId: this.currentEditedLayer.id,
          layerName: this.currentEditedLayer.name,
        },
      });
    },
    setActiveTab(tab) {
      this.activeTab = tab;
    },
    toggleColumnsSection(isVisible) {
      this.isColumnsVisible = isVisible;
    },
  },
  async mounted() {
    this.currentEditedLayer = this.$route.params.layer;
    this.vectorLayersList = this.$route.params.vectorLayersList;
    if (!this.vectorLayersList) {
      const r = await this.$store.dispatch('getLayers');
      this.vectorLayersList = r.body.layers;
    }
    if (!this.currentEditedLayer) {
      this.currentEditedLayer = this.vectorLayersList.find(
        el => el.id === this.$route.params.layerId,
      );
    }

    const r = await this.$store.dispatch('getLayerColumns', this.currentEditedLayer.id);
    this.currentLayerSettings = r.body.settings;

    this.loadStyle();
    this.isMounted = true;
  },
};
</script>

<style scoped>
  .control-label {
    position: relative;
    top: 8px;
  }
  .color-picker__container {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .disabled {
    cursor: not-allowed !important;
  }
  .ml-10 {
    margin-left: 10px;
  }
  .mt-15 {
    margin-top: 15px;
  }
  .picker__container {
    display: flex;
  }
  .pr-30 {
    padding-right: 30px;
  }
  .text-centered {
    text-align: center;
  }
  .text-left {
    text-align: left;
  }
  .verte {
    justify-content: flex-start;
  }
</style>

<template>
  <div class="container">
    <div class="col-md-3 layout-sidebar">
      <ul id="myTab" class="nav nav-layout-sidebar nav-stacked">
          <li class="active">
          <a href="#info-tab" data-toggle="tab">
          <i class="fa fa-info-circle"></i>
          &nbsp;&nbsp;<span>{{$i18n.t('settings.layerInfo')}}</span>
          </a>
        </li>
        <li>
          <a href="#style-tab" data-toggle="tab">
          <i class="fa fa-map-pin"></i>
          &nbsp;&nbsp;<span>{{$i18n.t('settings.symbolization')}}</span>
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
        <div class="tab-pane fade in active" id="info-tab">
          <div class="heading-block">
            <h3>
              <span data-i18n="layerSettings.title">{{$i18n.t('default.layerSettings')}}: </span>
              <span class="red">{{currentEditedLayer.name}}</span>
              <a @click="goToLayer" :title="$i18n.t('default.goToLayer')">
                <i class="fa fa-chevron-circle-right red icon-hover"></i>
              </a>
            </h3>
          </div>
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
          <!-- <div class="pt-10">
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
          </div> -->
        </div>
        <div class="tab-pane fade in active" id="style-tab">
          <p>styles</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'settings',
  data: () => ({
    currentEditedLayer: undefined,
    currentLayerSettings: undefined,
    isColumnsVisible: true,
    isMounted: false,
    newColumnName: undefined,
    newColumnType: undefined,
    styles: {},
    vectorLayersList: undefined,
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

    const styleResponse = await this.$store.dispatch('getLayerStyle', this.currentEditedLayer.id);
    this.$set(this.styles, this.currentEditedLayer.id, styleResponse.body.style);

    this.isMounted = true;
  },
};
</script>

<style scoped>
  .text-centered {
    text-align: center;
  }
  .text-left {
    text-align: left;
  }
</style>

<template>
  <div class="container">
    <div class="col-md-3 layout-sidebar">
      <ul
        id="myTab"
        class="nav nav-layout-sidebar nav-stacked"
      >
        <li class="active">
          <a
            href="#info-tab"
            data-toggle="tab"
            @click="setActiveTab('info-tab')"
          >
            <i class="fa fa-info-circle" />
            &nbsp;&nbsp;
            <span>{{ $i18n.t('settings.layerInfo') }}</span>
          </a>
        </li>
        <li>
          <a
            href="#style-tab"
            data-toggle="tab"
            @click="setActiveTab('style-tab')"
          >
            <i class="fa fa-map-pin" />
            &nbsp;&nbsp;
            <span>{{ $i18n.t('settings.symbolization') }}</span>
          </a>
        </li>
        <li>
          <a
            href="#labels-tab"
            data-toggle="tab"
            @click="setActiveTab('labels-tab')"
          >
            <i class="fa fa-tags" />
            &nbsp;&nbsp;
            <span>{{ $i18n.t('settings.labels') }}</span>
          </a>
        </li>
      </ul>
    </div>
    <div class="col-md-9 col-sm-8 layout-main">
      <div
        class="loading-overlay pt-10 pb-10 text-centered"
        v-if="!isMounted"
      >
        <div class="loading-indicator mb-10">
          <h4>{{ $i18n.t('default.loading') }}</h4>
          <i class="fa fa-lg fa-spin fa-spinner" />
        </div>
      </div>
      <div
        id="settings-content"
        class="tab-content stacked-content"
        v-else
      >
        <div class="heading-block">
          <h3>
            <span data-i18n="layerSettings.title">{{ $i18n.t('default.layerSettings') }}:</span>
            <span class="red">{{ currentEditedLayer.name }}</span>
            <a
              @click="goToLayer"
              :title="$i18n.t('default.goToLayer')"
            >
              <i class="fa fa-chevron-circle-right red icon-hover" />
            </a>
          </h3>
        </div>
        <div
          class="tab-pane in active"
          id="info-tab"
          v-if="activeTab === 'info-tab'"
        >
          <h4 class="text-left">{{ $i18n.t('dashboard.modal.layerName') }}</h4>
          <div style="display: flex">
            <input
              type="text"
              class="form-control mr-5"
              v-model="currentEditedLayer.name"
            />
            <button
              type="button"
              class="btn btn-success"
              @click="saveLayerName"
              :disabled="!currentEditedLayer.name || currentEditedLayer.name.length > layerMaxNameLength"
            >{{ $i18n.t('default.saveName') }}</button>
          </div>
          <div class="pt-10">
            <h4 class="text-left">{{ $i18n.t('dashboard.modal.addColumn') }}</h4>
            <div style="display: flex">
              <input
                type="text"
                class="form-control mr-5"
                placeholder="Nazwa kolumny"
                v-model="newColumnName"
              />
              <select
                class="form-control mr-5"
                name="column-types-select"
                v-model="newColumnType"
              >
                <option
                  :value="undefined"
                  selected
                  disabled
                >{{ $i18n.t('dashboard.modal.chooseColumnType') }}</option>
                <option
                  v-for="colType in columnTypes"
                  :key="colType"
                  :value="colType"
                  v-text="$i18n.t(`default.columnsTypes.${colType}`)"
                >{{ colType }}</option>
              </select>
              <button
                type="button"
                class="btn btn-success"
                @click="newColumnType==='dict'?openDictionaryModal():addNewColumn()"
                :disabled="!newColumnType || !newColumnName"
              >{{ $i18n.t('default.add') }}</button>
            </div>
          </div>
          <div class="pt-10">
            <h4 class="text-left">
              {{ $i18n.t('dashboard.modal.layerColumns') }}
              <i
                class="fa fa-chevron-up"
                @click="toggleColumnsSection(false)"
                v-if="isColumnsVisible"
                aria-hidden="true"
                style="cursor: pointer;"
                :title="$i18n.t('dashboard.modal.hideColumns')"
              />
              <i
                class="fa fa-chevron-down"
                @click="toggleColumnsSection(true)"
                v-if="!isColumnsVisible"
                aria-hidden="true"
                style="cursor: pointer;"
                :title="$i18n.t('dashboard.modal.showColumns')"
              />
            </h4>
            <table
              v-if="isColumnsVisible"
              class="table table-striped table-bordered table-hover"
            >
              <thead>
                <tr role="row">
                  <th class="text-centered">{{ $i18n.t('default.name') }}</th>
                  <th class="text-centered">{{ $i18n.t('default.dataType') }}</th>
                  <th class="text-centered">{{ $i18n.t('default.actions') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(value, name, index) in currentLayerSettings.columns"
                  :key="index"
                >
                  <td class="text-centered">{{ name }}</td>
                  <td class="text-centered">{{ $i18n.t(`default.columnsTypes.${value}`) }}</td>
                  <td class="text-centered">
                    <i
                      v-if="name !== 'id' && name != '__attachments'"
                      class="fa fa-trash fa-lg red icon-hover"
                      :title="$i18n.t('default.delete')"
                      @click="deleteColumn(name)"
                    />
                    <i
                      v-if="value === 'dict'"
                      class="fa fa-pencil fa-lg icon-hover"
                      :title="$i18n.t('default.edit')"
                      @click="openDictionaryModal(name)"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div
          class="tab-pane in active"
          id="style-tab"
          v-if="activeTab === 'style-tab'"
        >
          <div
            class="col-md-12 pb-10"
            style="display: flex;"
          >
            <div class="col-md-6 pl-0">
              <label class="control-label col-sm-6 pl-0">{{ $i18n.t('settings.visType') }}</label>
              <select
                class="form-control col-sm-4 mt-15"
                v-model="symbolizationType"
              >
                <option
                  disabled
                  value
                >{{ $i18n.t('settings.chooseVisualizationType') }}</option>
                <option value="single">{{ $i18n.t('default.single') }}</option>
                <option value="categorized">{{ $i18n.t('default.categorized') }}</option>
              </select>
            </div>
            <div
              class="col-md-6 pl-0"
              v-if="symbolizationType === 'single'"
            >
              <label class="control-label col-sm-6 pl-0">{{ $i18n.t('settings.objStyle') }}</label>
              <select
                class="form-control col-sm-4 mt-15"
                v-model="layerType"
                v-if="layerType === 'point' || layerType === 'square' || layerType === 'triangle'"
              >
                <option
                  disabled
                  value
                >{{ $i18n.t('settings.chooseObjectStyle') }}</option>
                <option value="point">{{ $i18n.t('default.point') }}</option>
                <option value="square">{{ $i18n.t('default.square') }}</option>
                <option value="triangle">{{ $i18n.t('default.triangle') }}</option>
              </select>
              <select
                class="form-control col-sm-4 mt-15"
                disabled
                v-model="layerType"
                v-else-if="layerType === 'polygon'"
              >
                <option
                  disabled
                  value
                >{{ $i18n.t('default.polygon') }}</option>
                <option
                  disabled
                  value="polygon"
                >{{ $i18n.t('default.polygon') }}</option>
              </select>
              <select
                class="form-control col-sm-4 mt-15"
                v-model="layerType"
                v-else
              >
                <option
                  disabled
                  value
                >{{ $i18n.t('settings.chooseObjectStyle') }}</option>
                <option value="line">{{ $i18n.t('default.line') }}</option>
                <option value="dotted">{{ $i18n.t('default.dotted') }}</option>
                <option value="dashed">{{ $i18n.t('default.dashed') }}</option>
              </select>
            </div>
          </div>
          <div
            class="form-group"
            v-if="symbolizationType === 'single'"
          >
            <div
              class="col-md-3 color-picker__container"
              style="left: -30px;"
            >
              <label class="control-label">{{ $i18n.t('settings.stroke-color') }}</label>
              <br />
              <color-picker
                model="rgb"
                v-model="strokeColor"
              />
            </div>
            <div class="col-md-3 color-picker__container">
              <label class="control-label">
                {{ $i18n.t('settings.stroke-width') }}
                <i
                  class="fa fa-question-circle icon-hover"
                  :title="$i18n.t('settings.sizeInfo')"
                />
              </label>
              <input
                type="number"
                min="1"
                max="10"
                @keyup="checkValue($event, 'strokeWidth')"
                class="form-control mt-15"
                style="width:50px"
                v-model="strokeWidth"
              />
            </div>
            <div
              class="col-md-3 color-picker__container"
              v-if="layerType !== 'line' || layerType !== 'dotted' || layerType !== 'dashed'"
            >
              <label class="control-label">{{ $i18n.t('settings.fill-color') }}</label>
              <br />
              <color-picker
                model="rgb"
                v-model="fillColor"
              />
            </div>
            <div
              class="col-md-3 color-picker__container"
              style="right: -20px"
              v-if="layerType === 'point' || layerType === 'triangle' || layerType === 'square'"
            >
              <label class="control-label">
                {{ $i18n.t('settings.width') }}
                <i
                  class="fa fa-question-circle icon-hover"
                  :title="$i18n.t('settings.sizeInfo')"
                />
              </label>
              <input
                type="number"
                min="1"
                step="1"
                max="10"
                @keyup="checkValue($event, 'width')"
                class="form-control mt-15"
                style="width:50px"
                v-model="width"
              />
            </div>
            <div
              class="col-md-12 pr-30"
              style="display:flex; justify-content:flex-end;"
            >
              <button
                type="button"
                class="btn btn-success mt-15"
                @click="saveStyle"
              >{{ $i18n.t('default.saveStyle') }}</button>
            </div>
          </div>
          <div
            class="form-group"
            v-else
          >
            <div
              class="col-md-12 pb-10"
              style="display: flex;"
            >
              <div class="col-md-6 pl-0">
                <label class="control-label col-sm-6 pl-0">{{ $i18n.t('settings.attribute') }}</label>
                <select
                  class="form-control col-sm-4 mt-15"
                  v-model="categorizedAttr"
                >
                  <option
                    disabled
                    value
                  >{{ $i18n.t('settings.chooseAttr') }}</option>
                  <template v-for="attr in Object.keys(currentLayerSettings.columns)">
                    <option
                      :key="attr"
                      :value="attr"
                    >{{ attr }}</option>
                  </template>
                </select>
              </div>
              <div class="col-md-6">
                <button
                  type="button"
                  class="btn btn-success"
                  style="margin-top: 38px"
                  :disabled="!categorizedAttr"
                  @click="categorizeFeatures(categorizedAttr, currentEditedLayer.id)"
                >{{ $i18n.t('settings.classify') }}</button>
                <button
                  type="button"
                  class="btn btn-success ml-10"
                  style="margin-top: 38px"
                  v-if="categories.length > 0"
                  @click="saveCategorizedStyles"
                >{{ $i18n.t('default.saveStyle') }}</button>
              </div>
            </div>
            <div class="col-md-12 pb-10">
              <table
                v-if="categories.length > 0"
                class="table table-striped table-bordered table-hover ml-15"
              >
                <thead>
                  <tr role="row">
                    <th
                      v-if="headers.includes('value')"
                      class="text-centered"
                    >{{ $i18n.t('settings.value') }}</th>
                    <th
                      v-if="headers.includes('fill-color')"
                      class="text-centered"
                    >{{ $i18n.t('settings.fill-color') }}</th>
                    <th
                      v-if="headers.includes('stroke-color')"
                      class="text-centered"
                    >{{ $i18n.t('settings.stroke-color') }}</th>
                    <th
                      v-if="headers.includes('stroke-width')"
                      class="text-centered"
                    >
                      {{ $i18n.t('settings.stroke-width') }}
                      <i
                        class="fa fa-question-circle icon-hover"
                        :title="$i18n.t('settings.sizeInfo')"
                      />
                    </th>
                    <th
                      v-if="headers.includes('width')"
                      class="text-centered"
                    >
                      {{ $i18n.t('settings.width') }}
                      <i
                        class="fa fa-question-circle icon-hover"
                        :title="$i18n.t('settings.sizeInfo')"
                      />
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(feat, index) in categories"
                    :key="index"
                  >
                    <td
                      v-if="feat.hasOwnProperty('value')"
                      class="text-centered"
                    >
                      <p style="position: relative; top: 5px;">{{ feat.value }}</p>
                    </td>
                    <td
                      v-if="feat.hasOwnProperty('fill-color')"
                      class="text-centered"
                    >
                      <color-picker v-model="feat['fill-color-rgba']" />
                    </td>
                    <td
                      v-if="feat.hasOwnProperty('stroke-color')"
                      class="text-centered"
                    >
                      <color-picker v-model="feat['stroke-color-rgba']" />
                    </td>
                    <td
                      v-if="feat.hasOwnProperty('stroke-width')"
                      class="text-centered"
                    >
                      <input
                        type="number"
                        min="1"
                        max="10"
                        @keyup="checkValue($event, 'stroke-width', index, 'categories')"
                        class="form-control"
                        style="width:50px; margin:0 auto;"
                        v-model="feat['stroke-width']"
                      />
                    </td>
                    <td
                      v-if="feat.hasOwnProperty('width')"
                      class="text-centered"
                    >
                      <input
                        type="number"
                        min="1"
                        max="10"
                        @keyup="checkValue($event, 'width', index, 'categories')"
                        class="form-control"
                        style="width:50px; margin:0 auto;"
                        v-model="feat['width']"
                      />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div
          class="tab-pane in active"
          id="labels-tab"
          v-if="activeTab === 'labels-tab'"
        >
          <span class="d-flex">
            <h4>{{ $i18n.t('settings.labelsTitle') }}</h4>
            <i
              class="fa fa-question-circle icon-hover ml-10"
              :title="$i18n.t('settings.labelsHelper')"
            />
          </span>
          <button
            type="button"
            style="float: right"
            class="btn btn-success mb-10"
            @click="saveLabels(labelsAll.filter(el => activeLabels.includes(el)))"
          >{{ $i18n.t('default.saveLabels') }}</button>
          <table class="table table-striped table-bordered table-hover">
            <thead>
              <tr role="row">
                <th class="text-centered">{{ $i18n.t('default.active') }}</th>
                <th class="text-centered">{{ $i18n.t('default.attribute') }}</th>
              </tr>
            </thead>
            <draggable
              tag="tbody"
              :list="labelsAll"
              @start="drag=true"
              @end="drag=false"
            >
              <tr
                v-for="(el, index) in labelsAll"
                :key="index"
              >
                <td
                  class="text-centered"
                  style="width: 50px"
                >
                  <input
                    type="checkbox"
                    :id="el"
                    :value="el"
                    v-model="activeLabels"
                  />
                </td>
                <td class="text-centered">{{ el }}</td>
              </tr>
            </draggable>
          </table>
        </div>
      </div>
    </div>
    <modal
      name="dicts"
      :draggable="false"
      width="30%"
      height="auto"
      @before-close="closeDictModal"
    >
      <div class="modal-content">
        <div class="modal-header">
          <h4 class="modal-title">{{ $i18n.t('settings.dictField') + ": " + currentDictName }}</h4>
        </div>
        <div class="modal-body">
          <div>
            <h4>{{ $i18n.t('settings.newValue') }}</h4>
            <div
              class="form-group"
              style="display: flex;"
            >
              <label
                class="control-label col-sm-4"
                style="position: relative; top: 8px"
              >{{ $i18n.t('settings.value') }}</label>
              <input
                v-model="currentDictValue"
                class="form-control col-sm-7 mr-5"
              />
              <button
                type="button"
                class="btn btn-default"
                :title="$i18n.t('default.add')"
                @click="currentDictValues.includes(currentDictValue)?$alertify.error($i18n.t('settings.valueExists')):currentDictValues.push(currentDictValue);currentDictValue=''"
              >
                <i class="fa fa-plus" />
              </button>
            </div>
            <div style="min-height:300px; max-height:300px; overflow-y:auto">
              <table class="table table-striped table-bordered table-hover">
                <thead v-if="currentDictValues.length > 0">
                  <tr role="row">
                    <th class="text-centered">{{ $i18n.t('default.ordinalNumber') }}</th>
                    <th class="text-centered">{{ $i18n.t('default.value') }}</th>
                    <th class="text-centered">{{ $i18n.t('default.actions') }}</th>
                  </tr>
                </thead>
                <draggable
                  tag="tbody"
                  :list="currentDictValues"
                  @start="drag=true"
                  @end="drag=false"
                >
                  <tr
                    v-for="(dV, idx) in currentDictValues"
                    :key="idx"
                  >
                    <td class="text-centered">{{ idx+1 }}</td>
                    <td class="text-centered">{{ dV }}</td>
                    <td class="text-centered">
                      <i
                        @click="currentDictValues.splice(idx,1)"
                        style="cursor: pointer"
                        :title="$i18n.t('settings.deleteValue')"
                        class="fa fa-trash"
                      />
                    </td>
                  </tr>
                </draggable>
              </table>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <div
            class="btn-group btn-group-justified"
            role="group"
          >
            <div
              class="btn-group"
              role="group"
            >
              <button
                type="button"
                class="btn btn-success"
                @click="isDictNew?addNewColumn():editColumn()"
              >{{ $i18n.t("default.save") }}</button>
            </div>
            <div
              class="btn-group"
              role="group"
            >
              <button
                type="button"
                class="btn btn-danger"
                @click="$modal.hide('dicts')"
              >{{ $i18n.t("default.cancel") }}</button>
            </div>
          </div>
        </div>
      </div>
    </modal>
  </div>
</template>

<script>
import _ from 'lodash';
import draggable from 'vuedraggable';
import ColorPicker from '@/components/ColorPicker';

export default {
  name: 'Settings',
  components: {
    draggable,
    ColorPicker
  },
  data: () => ({
    activeLabels: [],
    activeTab: 'info-tab',
    categories: [],
    categorizedAttr: undefined,
    currentDictName: undefined,
    currentDictValue: '',
    currentDictValues: [],
    currentEditedLayer: undefined,
    currentLayerSettings: undefined,
    drag: false,
    fillColor: '255,254,255,0.4',
    isColumnsVisible: true,
    isDictNew: true,
    isMounted: false,
    labelsAll: [],
    layerMaxNameLength: 60,
    layerType: undefined,
    newColumnName: undefined,
    newColumnType: undefined,
    strokeColor: '51,153,204,1',
    strokeWidth: 1,
    styles: {},
    symbolizationType: undefined,
    vectorLayersList: undefined,
    width: 1
  }),
  computed: {
    columnTypes() {
      return this.$store.getters.getColumnTypes;
    },
    featureAttachments() {
      return this.$store.getters.getFeatureAttachments;
    }
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
          values:
            this.newColumnType === 'dict' ? this.currentDictValues : undefined
        },
        lid: this.currentLayerSettings.id
      };
      const r = await this.$store.dispatch('changeLayer', payload);
      if (r.status === 200) {
        this.currentLayerSettings.columns[
          this.newColumnName
        ] = this.newColumnType;
        this.newColumnName = undefined;
        this.newColumnType = '';
        this.$alertify.success(this.$i18n.t('dashboard.modal.columnAdded'));
        this.$modal.hide('dicts');
      } else {
        if (r.obj.error === 'dict value must be 63 characters or less') {
          this.$alertify.error(this.$i18n.t('default.dictValueToLongError'));
        } else {
        this.$alertify.error(this.$i18n.t('default.error'));
        }
      }
    },
    async categorizeFeatures(attr, lid) {
      const r = await this.$store.dispatch('categorizeFeatures', { attr, lid });
      if (r.status === 200) {
        this.categories = r.body.categories;
        this.headers = Object.keys(r.body.categories[0]);

        this.categories.forEach(feat => {
          this.$set(feat, 'fill-color-rgba', `rgba(${feat['fill-color']})`);
          this.$set(feat, 'stroke-color-rgba', `rgba(${feat['stroke-color']})`);
        });
      } else {
        this.$i18n.t('default.error');
      }
    },
    async deleteColumn(colName) {
      this.$alertify
        .confirm(
          this.$i18n.t('dashboard.modal.deleteLayerColumn'),
          async () => {
            const payload = {
              body: { column_name: colName },
              lid: this.currentEditedLayer.id
            };

            const r = await this.$store.dispatch('deleteColumn', payload);
            if (r.status === 200) {
              this.$alertify.success(this.$i18n.t('default.deleted'));
              this.$delete(this.currentLayerSettings.columns, colName);
            } else {
              this.$i18n.t('default.error');
            }
          },
          () => {}
        )
        .set({ title: this.$i18n.t('dashboard.modal.deleteColumnTitle') })
        .set({
          labels: {
            ok: this.$i18n.t('default.delete'),
            cancel: this.$i18n.t('default.cancel')
          }
        });
    },
    async editColumn() {
      const payload = {
        body: {
          column_name: this.newColumnName,
          column_type: this.newColumnType,
          values:
            this.newColumnType === 'dict' ? this.currentDictValues : undefined
        },
        lid: this.currentLayerSettings.id
      };
      const r = await this.$store.dispatch('putDictsValues', {
        lid: this.currentEditedLayer.id,
        column_name: this.currentDictName,
        body: { data: this.currentDictValues }
      });
      if (r.status === 200) {
        this.$alertify.success(this.$i18n.t('settings.columnEdited'));
        this.checkStyle(r.obj.data);
      } else {
        if (r.obj.error === 'dict value must be 63 characters or less') {
          this.$alertify.error(this.$i18n.t('default.dictValueToLongError'));
        } else {
        this.$alertify.error(this.$i18n.t('default.error'));
        }
      }
      this.$modal.hide('dicts');
    },
    async getDictValues() {
      const dictValues = await this.$store.dispatch('getDictsValues', {
        lid: this.currentEditedLayer.id,
        column_name: this.currentDictName
      });
      if (dictValues.status === 200) {
        this.currentDictValues = dictValues.body.data;
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    async getLayerMaxNameLength() {
      const r = await this.$store.dispatch('getLayerMaxNameLength');
      this.layerMaxNameLength = r.body.data;
    },
    async loadColumnsAndLabels() {
      const r = await this.$store.dispatch(
        'getLayerColumns',
        this.currentEditedLayer.id
      );
      this.currentLayerSettings = r.body.settings;
      this.labelsAll = Object.keys(r.body.settings.columns).filter(
        el => el !== 'id'
      );
    },
    async loadStyle() {
      const lid = this.currentEditedLayer.id;
      const styleResponse = await this.$store.dispatch(
        'getLayerStyle',
        this.currentEditedLayer.id
      );
      this.$set(
        this.styles,
        this.currentEditedLayer.id,
        styleResponse.body.style
      );
      this.activeLabels = styleResponse.body.style.labels;
      this.labelsAll = _.union(
        this.activeLabels.filter(v => this.labelsAll.includes(v)),
        this.labelsAll
      );

      // stroke-width i stroke-color są we wszystkich typach
      this.strokeColor = `rgba(${this.styles[lid]['stroke-color']})`;
      this.strokeWidth = this.styles[lid]['stroke-width'];
      this.layerType = this.styles[lid].type;
      this.symbolizationType = styleResponse.body.style.renderer;
      if (this.symbolizationType === 'categorized') {
        this.categories = styleResponse.body.style.categories;
        this.categorizedAttr = styleResponse.body.style.attribute;
        this.headers = Object.keys(this.categories[0]);

        this.categories.forEach(feat => {
          this.$set(feat, 'fill-color-rgba', `rgba(${feat['fill-color']})`);
          this.$set(feat, 'stroke-color-rgba', `rgba(${feat['stroke-color']})`);
        });
        this.layerType = this.categories[0].type;
      }
      if (Object.keys(this.styles[lid]).includes('fill-color')) {
        // temp fix on verte
        this.fillColor = this.styles[lid]['fill-color'].split(',');
        if (this.fillColor[2] === '255') {
          this.fillColor[2] = '254';
        }
        this.fillColor = `rgba(${this.fillColor.join(',')})`;
      }
      if (Object.keys(this.styles[lid]).includes('width')) {
        this.width = this.styles[lid].width;
      }
    },
    async saveLayerName() {
      const layIndex = this.vectorLayersList.findIndex(
        el => el.id === this.currentEditedLayer.id
      );
      const payload = {
        body: {
          layer_name: this.currentEditedLayer.name
        },
        lid: this.currentEditedLayer.id
      };

      const r = await this.$store.dispatch('changeLayer', payload);
      if (r.status === 200) {
        this.$alertify.success(
          this.$i18n.t('dashboard.modal.layerNameChanged')
        );
        // zmiana id
        this.$set(this.vectorLayersList[layIndex], 'id', r.obj.settings);
        this.$set(this.currentLayerSettings, 'id', r.obj.settings);
        // zmiana nazwy
        this.$set(
          this.vectorLayersList[layIndex],
          'name',
          this.currentEditedLayer.name
        );
        this.$set(
          this.currentLayerSettings,
          'name',
          this.currentEditedLayer.name
        );
        window.history.pushState(null, '', r.obj.settings);
      } else {
        this.$i18n.t('default.error');
      }
    },
    async saveCategorizedStyles() {
      this.categories.forEach(feat => {
        let fillRgb = this.formatColor(feat['fill-color-rgba']);
        let strokeRgb = this.formatColor(feat['stroke-color-rgba']);
        if (fillRgb.split(',').length === 3) {
          fillRgb = `${fillRgb},1`;
        }
        if (strokeRgb.split(',').length === 3) {
          strokeRgb = `${strokeRgb},1`;
        }
        this.$set(feat, 'fill-color', fillRgb);
        this.$set(feat, 'stroke-color', strokeRgb);
      });
      const labelsToSave = this.labelsAll.filter(el =>
        this.activeLabels.includes(el)
      );
      const r = await this.$store.dispatch('saveStyle', {
        lid: this.currentEditedLayer.id,
        body: {
          categories: this.categories,
          attribute: this.categorizedAttr,
          renderer: this.symbolizationType,
          labels: labelsToSave
        }
      });
      if (r.status === 200) {
        this.$alertify.success(this.$i18n.t('default.styleSaved'));
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    async saveLabels() {
      if (this.symbolizationType === 'categorized') {
        this.saveCategorizedStyles();
      } else {
        let fill;
        let stroke;
        if (this.fillColor) {
          fill = this.formatColor(this.fillColor);

          if (fill.split(',').length === 3) {
            fill = `${fill},1`;
          }
        }
        if (this.strokeColor) {
          stroke = this.formatColor(this.strokeColor);

          if (stroke.split(',').length === 3) {
            stroke = `${stroke},1`;
          }
        }
        const labelsToSave = this.labelsAll.filter(el =>
          this.activeLabels.includes(el)
        );
        const r = await this.$store.dispatch('saveStyle', {
          lid: this.currentEditedLayer.id,
          body: {
            type: this.layerType,
            attribute: this.categorizedAttr,
            'fill-color': fill,
            'stroke-color': stroke,
            'stroke-width': this.strokeWidth,
            labels: labelsToSave,
            width: this.width,
            renderer: this.symbolizationType
          }
        });
        if (r.status === 200) {
          this.$alertify.success(this.$i18n.t('default.styleSaved'));
        } else {
          this.$alertify.error(this.$i18n.t('default.error'));
        }
      }
    },
    async saveStyle() {
      let fill;
      let stroke;
      if (this.fillColor) {
        fill = this.formatColor(this.fillColor);

        if (fill.split(',').length === 3) {
          fill = `${fill},1`;
        }
      }
      if (this.strokeColor) {
        stroke = this.formatColor(this.strokeColor);

        if (stroke.split(',').length === 3) {
          stroke = `${stroke},1`;
        }
      }

      const labelsToSave = this.labelsAll.filter(el =>
        this.activeLabels.includes(el)
      );
      const r = await this.$store.dispatch('saveStyle', {
        lid: this.currentEditedLayer.id,
        body: {
          type: this.layerType,
          labels: labelsToSave,
          'fill-color': fill,
          'stroke-color': stroke,
          'stroke-width': this.strokeWidth,
          width: this.width,
          renderer: this.symbolizationType
        }
      });
      if (r.status === 200) {
        this.$alertify.success(this.$i18n.t('default.styleSaved'));
        this.categories = [];
        this.categorizedAttr = undefined;
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    checkStyle(style) {
      if (
        style.renderer === 'categorized' &&
        style.attribute === this.categorizedAttr &&
        this.symbolizationType === 'categorized'
      ) {
        const categories = [];
        for (let cat of style.categories) {
          categories.push(cat.value);
        }
        for (let cat of this.categories) {
          if (!categories.includes(cat.value)) {
            this.categories.splice(this.categories.indexOf(cat), 1);
          }
        }
      }
    },
    checkValue(e, model, idx, arr) {
      const charCode = e.which ? e.which : e.keyCode;
      if (
        (charCode > 37 && charCode > 47 && charCode < 58) ||
        (charCode > 37 && charCode > 95 && charCode < 106)
      ) {
        if (e.srcElement.valueAsNumber > Number(e.srcElement.max)) {
          typeof idx === 'number' && arr
            ? (this[arr][idx][model] = e.srcElement.max)
            : (this[model] = e.srcElement.max);
          this.$alertify.warning(this.$i18n.t('settings.maxSize'));
        } else if (e.srcElement.valueAsNumber < Number(e.srcElement.min)) {
          typeof idx === 'number' && arr
            ? (this[arr][idx][model] = e.srcElement.min)
            : (this[model] = e.srcElement.min);
          this.$alertify.warning(this.$i18n.t('settings.minSize'));
        }
      } else {
        if (!e.srcElement.valueAsNumber) {
          this.$alertify.warning(this.$i18n.t('settings.invalidValue'));
          typeof idx === 'number' && arr
            ? (this[arr][idx][model] = 1)
            : (this[model] = 1);
        }
      }
    },
    closeDictModal() {
      this.currentDictValue = undefined;
      this.currentDictValues = [];
    },
    formatColor(rgba) {
      return rgba.substring(
        // get rgba between ()
        rgba.lastIndexOf('(') + 1,
        rgba.lastIndexOf(')')
      );
    },
    goToLayer() {
      const lid = this.currentEditedLayer.id;
      if (!Object.keys(this.featureAttachments).includes(lid)) {
        this.$store.commit('setAttachmentsLayer', lid);
      }
      this.$store.commit('setLayerName', this.currentEditedLayer.name);
      this.$router.push({
        name: 'feature_manager',
        params: {
          layerId: this.currentEditedLayer.id,
          layerName: this.currentEditedLayer.name
        }
      });
    },
    openDictionaryModal(col) {
      if (col) {
        this.isDictNew = false;
        this.currentDictName = col;
        this.getDictValues();
      } else {
        this.isDictNew = true;
        this.currentDictName = this.newColumnName;
      }
      this.$modal.show('dicts');
    },
    setActiveTab(tab) {
      this.loadColumnsAndLabels();
      this.loadStyle();
      this.activeTab = tab;
    },
    toggleColumnsSection(isVisible) {
      this.isColumnsVisible = isVisible;
    }
  },
  watch: {
    symbolizationType(newValue, oldValue) {
      // set default style
      if (
        newValue === 'single' &&
        oldValue === 'categorized' &&
        this.symbolizationType === 'single'
      ) {
        this.fillColor = 'rgba(255,255,254,0.4)';
        this.strokeColor = 'rgba(51,153,204,1)';
        this.strokeWidth = 1;
        this.width = 1;
      }
    }
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
        el => el.id === this.$route.params.layerId
      );
    }

    const r = await this.$store.dispatch(
      'getLayerColumns',
      this.currentEditedLayer.id
    );
    this.currentLayerSettings = r.body.settings;
    this.labelsAll = Object.keys(r.body.settings.columns).filter(
      el => el !== 'id'
    );

    this.loadStyle();
    this.getLayerMaxNameLength();
    this.isMounted = true;
  }
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
.mb-10 {
  margin-bottom: 10px;
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
</style>

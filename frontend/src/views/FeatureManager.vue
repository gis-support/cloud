<template>
  <div id="wrapper">
    <div id="root">
      <div class="map-table-content">
        <div class="map-content">
          <div
            class="map"
            ref="map"
            id="map"
          >
            <div class="add-feature-tool map-tool-left">
              <button
                type="button"
                class="map-btn"
                :title="$i18n.t('featureManager.addFeature')"
                @click="drawNewFeature"
                v-if="!isDrawing && permission === 'write' && items.length > 0"
              >
                <i class="fa fa-plus" />
              </button>
              <span
                class="navbar-right"
                v-else-if="items.length > 0"
              >
                <button
                  type="button"
                  class="map-btn"
                  v-if="permission === 'write'"
                  :title="$i18n.t('featureManager.cancelFeatureAdding')"
                  @click="clearFeatureAdding"
                >
                  <i class="fa fa-times-circle" />
                </button>
              </span>
            </div>
            <div class="measure-tool map-tool-left">
              <button
                type="button"
                class="map-btn"
                @click.stop="showMeasure"
                :title="showMeasureTitle"
              >
                <i
                  v-if="!isMeasureShow && !isMeasure"
                  class="fa fa-arrow-right"
                />
                <i
                  v-if="isMeasureShow && !isMeasure"
                  class="fa fa-arrow-left"
                />
                <i
                  v-if="isMeasure"
                  class="fa fa-trash"
                />
              </button>
              <button
                v-show="isMeasureShow"
                type="button"
                class="map-btn"
                :title="$i18n.t('featureManager.map.areaMeasure')"
                @click="startMeasure('Polygon')"
              >☐</button>
              <button
                v-show="isMeasureShow"
                type="button"
                class="map-btn"
                :title="$i18n.t('featureManager.map.distanceMeasure')"
                @click="startMeasure('LineString')"
              >\</button>
            </div>
            <div class="buffer-tool map-tool-left">
              <button
                v-show="currentFeature"
                type="button"
                class="map-btn"
                @click="openBufferDialog"
                :title="$i18n.t('featureManager.map.buffer')"
              >B</button>
            </div>
            <div class="distance-tool map-tool-left">
              <button
                v-show="currentFeature"
                type="button"
                class="map-btn"
                @click="openDistanceDialog"
                :title="$i18n.t('featureManager.map.distance')"
              >D</button>
            </div>
            <div class="rotation-tool map-tool-right">
              <button
                type="button"
                class="map-btn"
                @click="openRotationDialog"
                :title="$i18n.t('featureManager.map.rotation')"
              >A</button>
            </div>
          </div>
        </div>
        <div
          v-if="isTableShow"
          class="navbar-table-content"
        >
          <nav
            class="navbar navbar-default table-menu"
            style="margin-bottom: 0px;"
          >
            <div class="container-fluid">
              <button
                type="button"
                class="btn navbar-btn navbar-left btn-default"
                @click="isTableShow = false"
                :title="$i18n.t('featureManager.closeTable')"
              >
                <i class="fa fa-times fa-lg" />
              </button>
              <p
                class="navbar-text"
                v-cloak
              >
                {{ $i18n.t("featureManager.objectsNumber") }}
                <span v-text="searchCount" />
              </p>
              <div class="navbar-form navbar-right">
                <div class="form-group">
                  <input
                    type="text"
                    class="form-control"
                    placeholder="Wyszukaj"
                    :title="$i18n.t('featureManager.localSearch')"
                    v-model.trim="searchItemValue"
                  />
                </div>
              </div>
              <button
                type="button"
                class="btn navbar-btn navbar-right btn-default"
                :class="{
                  'btn-danger': currentColumnFilters.length > 0,
                  'btn-default': currentColumnFilters.length == 0
                }"
                :title="$i18n.t('featureManager.objectsFilter')"
                @click="openColumnFilterDecision"
              >
                <i class="fa fa-filter" />
              </button>
              <button
                type="button"
                class="btn navbar-btn navbar-right btn-default"
                v-if="selectedRows.length > 0"
                @click="downloadLayer(selectedRows)"
              >
                <i class="fa fa-download" />
              </button>
              <button
                style="margin-right: 2px"
                type="button"
                class="btn navbar-btn navbar-right btn-default"
                :title="$i18n.t('featureManager.zoomToSelected')"
                v-if="currentFeature"
                @click="zoomToSelected"
              >
                <i class="fa fa-search" />
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
            :lay-id="$route.params.layerId"
            :rows-to-download="selectedRows"
            :search="searchItemValue"
            @selectFeatureById="selectFeatureById"
            @updateSearchCount="updateSearchCount"
            @updateSelectedRows="updateSelectedRows"
          />
          <div
            class="loading-overlay pt-10 pb-10"
            style="text-align: center"
            v-else
          >
            <div class="loading-indicator mb-10">
              <h4>{{ $i18n.t("default.loading") }}</h4>
              <i class="fa fa-lg fa-spin fa-spinner" />
            </div>
          </div>
        </div>

        <div
          class="modal-mask"
          v-if="columnFilterDecisionDialogView"
        >
          <div class="modal-wrapper">
            <div class="modal-dialog modal-md">
              <div class="modal-content">
                <div class="modal-header">
                  <h4 class="modal-title">{{ $i18n.t("featureManager.objectsFilter") }}</h4>
                </div>
                <div class="modal-body">
                  <FiltersPanel
                    ref="column-filters"
                    :columns="columns"
                    v-model="selectedColumnFilters"
                  />
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
                        @click="$emit('columnFilterDecision', 'accept')"
                        :disabled="!isFiltersValidated(selectedColumnFilters)"
                      >{{ $i18n.t("default.save") }}</button>
                    </div>
                    <div
                      class="btn-group"
                      role="group"
                    >
                      <button
                        type="button"
                        class="btn btn-danger"
                        @click="$emit('columnFilterDecision', 'clear')"
                      >{{ $i18n.t("default.clear") }}</button>
                    </div>
                    <div
                      class="btn-group"
                      role="group"
                    >
                      <button
                        type="button"
                        class="btn btn-default"
                        @click="$emit('columnFilterDecision', 'cancel')"
                      >{{ $i18n.t("default.cancel") }}</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div
          class="modal-mask"
          v-if="addFeatureDialog"
        >
          <div class="modal-wrapper">
            <div class="modal-dialog modal-md modal-new-feature">
              <div class="modal-content">
                <div class="modal-header">
                  <h4 class="modal-title">{{ $i18n.t("featureManager.addFeatureTitle") }}</h4>
                </div>
                <div
                  class="modal-body"
                  v-if="activeLayer"
                >
                  <template v-for="name in Object.keys(activeLayer.features[0].properties)">
                    <div
                      class="form-group"
                      style="display: flex;"
                      :key="name"
                      v-if="name !== 'id'"
                    >
                      <label
                        class="control-label col-sm-4"
                        style="position: relative; top: 8px"
                      >
                        {{
                        name
                        }}
                      </label>
                      <InputNumber
                        v-model.number="newFeatureProperties[name]"
                        v-if="featureTypes[name] === 'integer' || featureTypes[name] === 'real'"
                        :type="featureTypes[name]"
                      />
                      <input
                        class="form-control col-sm-7"
                        v-model="newFeatureProperties[name]"
                        v-else-if="featureTypes[name] === 'character varying'"
                        type="text"
                      />
                      <Datepicker
                        v-else-if="featureTypes[name] === 'timestamp without time zone'"
                        v-model="newFeatureProperties[name]"
                        format="dd.MM.yyyy"
                      ></Datepicker>
                      <select
                        v-else-if="featureTypes[name] === 'dict'"
                        class="form-control"
                        v-model="newFeatureProperties[name]"
                      >
                        <option
                          v-for="(dV, idx) in dictValues.find(d => d.column_name === name).values"
                          v-text="dV"
                          :value="dV"
                          :key="idx"
                        />
                      </select>
                    </div>
                  </template>
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
                        @click="saveNewFeature"
                      >{{ $i18n.t("default.save") }}</button>
                    </div>
                    <div
                      class="btn-group"
                      role="group"
                    >
                      <button
                        type="button"
                        class="btn btn-danger"
                        @click="clearFeatureAdding"
                      >{{ $i18n.t("default.cancel") }}</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <button
          type="button"
          class="btn btn-default show-table"
          v-if="!isTableShow"
          @click="isTableShow = true"
          :title="$i18n.t('featureManager.showTable')"
        >
          <i class="fa fa-table" />
        </button>
        <modal
          name="bufferTable"
          :draggable="true"
          width="70%"
          height="auto"
          @before-close="closeBufferTableDialog()"
        >
          <div class="modal-content dragg-content">
            <div class="modal-header">
              <h4 class="modal-title">{{ $i18n.t("featureManager.bufferTable") }}</h4>
            </div>
            <div
              class="modal-body"
              style="padding-bottom:0"
            >
              <div style="height: 32vh">
                <BufferTable
                  v-if="bufferFeatures.length > 0"
                  ref="buffer-data"
                  :columns="bufferColumns"
                  :items="bufferFeatures"
                />
                <div
                  class="loading-overlay pt-10 pb-10"
                  style="text-align: center"
                  v-else
                >
                  <div class="loading-indicator">
                    <h4>{{ "Brak danych" }}</h4>
                  </div>
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
                    :disabled="bufferFeatures.length < 1"
                    type="button"
                    class="btn btn-success"
                    @click="downloadObjectsArray"
                  >{{ $i18n.t("featureManager.downloadList") }}</button>
                </div>
                <div
                  class="btn-group"
                  role="group"
                >
                  <button
                    type="button"
                    class="btn btn-danger"
                    @click="$modal.hide('bufferTable')"
                  >{{ $i18n.t("default.close") }}</button>
                </div>
              </div>
            </div>
          </div>
        </modal>
        <modal
          name="buffer"
          :draggable="true"
          width="35%"
          height="auto"
          @before-close="closeBufferDialog()"
        >
          <div class="modal-content dragg-content">
            <div class="modal-header">
              <h4 class="modal-title">{{ $i18n.t("featureManager.map.buffer") }}</h4>
            </div>
            <div
              class="modal-body"
              v-if="activeLayer"
            >
              <div style="margin-bottom: 100px">
                <h4>{{ $i18n.t("featureManager.bufferAnalysis") }}</h4>
                <div
                  class="form-group"
                  style="display: flex;"
                >
                  <label
                    class="control-label col-sm-4"
                    style="position: relative; top: 8px"
                  >
                    {{
                    $i18n.t("featureManager.bufferValue") + " [m]"
                    }}
                  </label>
                  <input
                    class="form-control col-sm-7"
                    v-model="bufferValue"
                    type="number"
                    @input="clearBufferDialog"
                  />
                </div>
                <div
                  style="float: right"
                  class="btn-group"
                  role="group"
                >
                  <button
                    :disabled="!bufferValue || bufferValue <= 0"
                    type="button"
                    class="btn btn-default"
                    @click="generateBuffer"
                  >{{ $i18n.t("featureManager.bufferGenerate") }}</button>
                </div>
              </div>
              <div>
                <h4>{{ $i18n.t("featureManager.generateObjectsArray") }}</h4>
                <div
                  class="form-group"
                  style="display: flex;"
                >
                  <label
                    class="control-label col-sm-4"
                    style="position: relative; top: 8px"
                  >
                    {{
                    $i18n.t("featureManager.bufferLayer")
                    }}
                  </label>
                  <select
                    style="max-width: 75%"
                    class="form-control"
                    :disabled="!isBuffer"
                    v-model="selectedLayer"
                  >
                    <option
                      v-for="(layer, idx) of layers"
                      v-text="layer.name"
                      :key="idx"
                      :value="layer"
                    />
                  </select>
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
                    :disabled="!selectedLayer"
                    type="button"
                    class="btn btn-success"
                    @click="generateObjectsArray"
                  >{{ $i18n.t("featureManager.generateList") }}</button>
                </div>
                <div
                  class="btn-group"
                  role="group"
                >
                  <button
                    type="button"
                    class="btn btn-danger"
                    @click="$modal.hide('buffer')"
                  >{{ $i18n.t("default.close") }}</button>
                </div>
              </div>
            </div>
          </div>
        </modal>
        <modal
          name="distance"
          :draggable="true"
          width="35%"
          height="auto"
          @before-close="bufferValue = undefined; selectedFieldName = undefined; bufferFeatureGeometry = undefined"
        >
          <div class="modal-content dragg-content">
            <div class="modal-header">
              <h4 class="modal-title">{{ $i18n.t("featureManager.distanceAnalysis") }}</h4>
            </div>
            <div
              class="modal-body"
              v-if="activeLayer"
            >
              <div style="margin-bottom: 50px">
                <div
                  class="form-group"
                  style="display: flex;"
                >
                  <label
                    class="control-label col-sm-4"
                    style="position: relative; top: 8px"
                  >
                    {{
                    $i18n.t("featureManager.bufferValue") + " [m]"
                    }}
                  </label>
                  <input
                    class="form-control col-sm-7"
                    v-model="bufferValue"
                    type="number"
                  />
                </div>
                <div
                  class="form-group"
                  style="display: flex;"
                >
                  <label
                    class="control-label col-sm-4"
                    style="position: relative; top: 8px"
                  >
                    {{
                    $i18n.t("featureManager.fieldName")
                    }}
                  </label>
                  <select
                    style="max-width: 75%"
                    class="form-control"
                    v-model="selectedFieldName"
                  >
                    <option
                      v-for="(prop, idx) of currentFeatureFieldsNames"
                      v-text="prop"
                      :key="idx"
                      :value="prop"
                    />
                  </select>
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
                    :disabled="!bufferValue || !selectedFieldName"
                    type="button"
                    class="btn btn-success"
                    @click="generateDistance"
                  >{{ $i18n.t("featureManager.download") }}</button>
                </div>
                <div
                  class="btn-group"
                  role="group"
                >
                  <button
                    type="button"
                    class="btn btn-danger"
                    @click="$modal.hide('distance')"
                  >{{ $i18n.t("default.close") }}</button>
                </div>
              </div>
            </div>
          </div>
        </modal>
        <modal
          name="rotation"
          :draggable="true"
          width="30%"
          height="auto"
          @before-close="rotationValue = 0"
        >
          <div class="modal-content dragg-content">
            <div class="modal-header">
              <h4 class="modal-title">{{ $i18n.t("featureManager.map.rotation") }}</h4>
            </div>
            <div
              class="modal-body"
              v-if="activeLayer"
            >
              <div
                class="form-group"
                style="display: flex;"
              >
                <label
                  class="control-label col-sm-4"
                  style="position: relative; top: 8px"
                >
                  {{
                  $i18n.t("featureManager.rotationValue") + ` [ ${String.fromCharCode(176)} ]`
                  }}
                </label>
                <input
                  class="form-control col-sm-7"
                  v-model="rotationValue"
                  type="number"
                  :step="45"
                  :max="360"
                  :min="0"
                />
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
                    :disabled="
                      rotationValue > 360 || rotationValue < 0 || !/^\d+$/.test(rotationValue)
                    "
                    type="button"
                    class="btn btn-success"
                    @click="rotateMapByAngle(rotationValue)"
                  >{{ $i18n.t("featureManager.rotate") }}</button>
                </div>
                <div
                  class="btn-group"
                  role="group"
                >
                  <button
                    type="button"
                    class="btn btn-danger"
                    @click="$modal.hide('rotation')"
                  >{{ $i18n.t("default.close") }}</button>
                </div>
              </div>
            </div>
          </div>
        </modal>

        <modal
          name="addLayer"
          :draggable="true"
          width="30%"
          height="70%"
        >
          <div class="modal-content dragg-content">
            <div class="modal-header">
              <h4 class="modal-title">{{ $i18n.t("featureManager.addLayer") }}</h4>
            </div>
            <div
              class="modal-body layer-modal-body"
              v-if="activeLayer"
            >
              <div
                class="form-group"
                style="height: 100%"
              >
                <div class="pb-10">
                  <input
                    type="text"
                    class="form-control container__input"
                    v-model="searchLayer"
                    :placeholder="$i18n.t('dashboard.placeholder.layersFilter')"
                  />
                </div>
                <div class="layers-wrapper">
                  <template v-for="(layer, idx) in layersFilteredByName">
                    <div
                      class="mb-0"
                      :key="idx"
                    >
                      <div class="panel-heading pl-0 pr-0">
                        <h4 class="panel-title flex-center">
                          <span
                            v-if="layer.url"
                            class="panel-title__names"
                          >
                            <i
                              style="margin-right:9px"
                              class="icon-li fa fa-link fa-lg"
                            />
                            <span
                              class="bold"
                              href="#"
                            >{{ layer.name }} ({{ layer.layers | maxLength }})</span>
                          </span>
                          <span
                            v-else
                            class="panel-title__names"
                          >
                            <i class="icon-li fa fa-map-o fa-lg mr-5" />
                            <span
                              class="bold"
                              href="#"
                            >{{ layer.name }}</span>
                          </span>
                          <span
                            id="layers-list-icons"
                            class="panel-title__tools"
                          >
                            <i
                              class="fa fa-plus-circle fa-lg green"
                              :title="$i18n.t('featureManager.addLayer')"
                              @click="addLayer(layer)"
                            />
                          </span>
                        </h4>
                      </div>
                    </div>
                  </template>
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
                    class="btn btn-danger"
                    @click="$modal.hide('addLayer')"
                  >{{ $i18n.t("default.close") }}</button>
                </div>
              </div>
            </div>
          </div>
        </modal>
        <modal
          name="saveProject"
          :draggable="true"
          width="30%"
          height="auto"
          @before-close="projectName=''"
        >
          <div class="modal-content dragg-content">
            <div class="modal-content">
              <div class="modal-header">
                <h4
                  class="modal-title"
                >{{ project?$i18n.t(`featureManager.saveProject`):$i18n.t(`featureManager.createProject`) }}</h4>
              </div>
              <div class="modal-body">
                <div
                  class="form-group"
                  style="display: flex;"
                >
                  <label
                    class="control-label col-sm-4"
                    style="position: relative; top: 8px"
                  >{{ $i18n.t(`default.name`) }}</label>
                  <input
                    class="form-control col-sm-7"
                    v-model="projectName"
                    type="text"
                  />
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
                      :disabled="!projectName"
                      type="button"
                      class="btn btn-success"
                      @click="saveProject"
                    >{{ $i18n.t("default.save") }}</button>
                  </div>
                  <div
                    class="btn-group"
                    role="group"
                  >
                    <button
                      type="button"
                      class="btn btn-danger"
                      @click="$modal.hide('saveProject')"
                    >{{ $i18n.t("default.close") }}</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </modal>

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
        ></virtual-table>-->
      </div>
      <div class="right-panel padding-0">
        <div class="col-sm-12">
          <div style="display: inline-block; width: 100%;">
            <h4 class="col-sm-10 right-panel__title">
              <i class="fa fa-map-o title__icon" />
              <span
                class="mvp-red right-panel__name"
                :title="layerName"
              >
                {{
                layerName ? layerName : "" | maxLength
                }}
              </span>
            </h4>
            <div
              class="col-sm-2"
              style="margin-top: 6px;"
              v-if="permission === 'write'"
            >
              <div
                class="btn-group btn-group-sm"
                role="group"
                style="float: right; margin-right: -15px; display: flex;"
              >
                <a
                  class="btn btn-default"
                  @click="goToSettings"
                  :title="$i18n.t('default.settings')"
                >
                  <i class="fa fa-cog yellow icon-hover" />
                </a>
                <div
                  class="btn-group btn-group-sm"
                  role="group"
                >
                  <button
                    type="button"
                    class="btn btn-default dropdown-toggle"
                    data-toggle="dropdown"
                    aria-haspopup="true"
                    aria-expanded="false"
                    :title="$i18n.t('featureManager.download')"
                  >
                    <i class="fa fa-download green icon-hover" />
                    <span class="caret" />
                  </button>
                  <ul class="dropdown-menu">
                    <!-- <li><a>SHP</a></li> -->
                    <li @click="downloadLayer([])">
                      <a>GEOJSON</a>
                    </li>
                    <!-- <li><a>XLSX</a></li> -->
                  </ul>
                </div>
              </div>
            </div>
          </div>
          <div
            class="flex-center"
            style="margin-bottom:30px"
          >
            <div>
              <h4
                v-if="project"
                style="margin-bottom:5px;overflow:hidden"
                class="col-sm-20"
                :title="project.name"
              >
                <i class="fa fa-database title__icon" />
                {{project.name | maxLength}}
              </h4>
            </div>
            <div
              class="btn-group btn-group-sm"
              role="group"
              style=" display: flex;"
            >
              <a
                class="btn btn-default"
                @click="$modal.show('saveProject');projectName=project?project.name:''"
                :title="project?$i18n.t(`featureManager.saveProject`):$i18n.t(`featureManager.createProject`)"
              >
                <i
                  v-bind:class="{'fa-plus': !project, 'fa-save': project}"
                  class="fa fa-lg fa-plus icon-hover"
                />
              </a>
            </div>
          </div>

          <ul
            class="nav nav-tabs nav-justified"
            style="margin-left: -15px; width: calc(100% + 30px);"
          >
            <li
              role="presentation"
              :class="{ active: indexActiveTab === 0 }"
            >
              <a
                href="#"
                @click="indexActiveTab = 0"
              >
                <i class="fa fa-bars" />
                {{ $i18n.t("featureManager.legend") }}
              </a>
            </li>
            <li
              role="presentation"
              :class="{ active: indexActiveTab === 1 }"
              v-show="currentFeature"
            >
              <a
                href="#"
                @click="indexActiveTab = 1"
              >
                <i class="fa fa-table" />
                {{ $i18n.t("featureManager.attributes") }}
              </a>
            </li>
            <li
              role="presentation"
              :class="{ active: indexActiveTab === 2, disabled: !featureAttachments }"
              v-show="currentFeature"
            >
              <a
                href="#"
                @click="indexActiveTab = 2;$refs['attachments-panel'].getAttachmentsMeta()"
              >
                <i class="fa fa-info" />
                {{ $i18n.t("featureManager.informations") }}
              </a>
            </li>
          </ul>
          <div>
            <div
              v-show="indexActiveTab === 0"
              class="legend-panel right-sub-panel"
            >
              <div class="scroll-tab">
                <div class="baseLayers">
                  <h4>{{ $i18n.t("default.basemaps") }}:</h4>
                  <ul class="list-group">
                    <li
                      class="list-group-item"
                      v-for="name in baseLayers"
                      :key="name"
                      :class="{ activeLayer: currentBaseLayer == name }"
                      @click="changeBaseLayer(name)"
                    >{{ name }}</li>
                  </ul>
                </div>
                <div class="others">
                  <div class="mb-10">
                    <h4 class="mb-0">{{ $i18n.t("default.otherLayers") }}:</h4>
                    <span @click="openAddLayerModal">
                      <i
                        class="fa fa-plus-circle fa-lg green pt-10"
                        style="margin-right:5px;"
                      />
                      <a
                        class="green section__content--add"
                      >{{ $i18n.t('featureManager.addLayer') }}</a>
                    </span>
                  </div>

                  <draggable
                    tag="ul"
                    class="list-group"
                    :list="otherLayers"
                    @start="drag=true"
                    @change="setLayersOrder"
                    v-if="otherLayers.length > 0"
                  >
                    <li
                      class="list-group-item"
                      v-for="{id, name} in otherLayers"
                      :key="name"
                      :class="{ activeLayer: activeOtherLayers.includes(id) }"
                    >
                      <div class="list__element--otherLayer">
                        <label
                          class="checkbox-inline mb-0"
                          :title="name"
                        >
                          <input
                            type="checkbox"
                            @click="setLayerVisibility(name)"
                            :value="id"
                            v-model="activeOtherLayers"
                          />
                          <span>{{ name }}</span>
                        </label>
                        <i
                          class="fa fa-minus-circle fa-lg red"
                          style="margin-right:5px;"
                          :title="$i18n.t('featureManager.removeLayer')"
                          @click="removeLayer(name)"
                        />
                      </div>
                    </li>
                  </draggable>
                  <span v-else>
                    <ul class="list-group">
                      <li class="list-group-item no-item">{{ $i18n.t("default.noOtherLayers") }}</li>
                    </ul>
                  </span>
                </div>
              </div>
            </div>

            <div v-show="indexActiveTab === 1">
              <template v-if="permission === 'write'">
                <template v-if="!editing">
                  <div
                    class="btn-group btn-group-edit"
                    role="group"
                  >
                    <button
                      type="button"
                      class="btn btn-success btn-group-justified"
                      @click="editAttributes"
                    >{{ $i18n.t("default.edit") }}</button>
                  </div>
                </template>
                <template v-else>
                  <div
                    class="btn-group btn-group-action btn-group-edit"
                    role="group"
                  >
                    <button
                      type="button"
                      class="btn btn-success"
                      @click="saveEditing"
                    >{{ $i18n.t("default.save") }}</button>
                  </div>
                  <div
                    class="btn-group btn-group-action btn-group-edit"
                    role="group"
                  >
                    <button
                      type="button"
                      class="btn btn-default"
                      @click="cancelEditing"
                    >{{ $i18n.t("default.cancel") }}</button>
                  </div>
                  <div
                    class="btn-group btn-group-action btn-group-edit"
                    role="group"
                  >
                    <button
                      type="button"
                      class="btn btn-danger"
                      @click="deleteFeature"
                    >{{ $i18n.t("default.delete") }}</button>
                  </div>
                </template>
              </template>

              <div class="scroll-tab">
                <AttributesPanel
                  v-if="currentFeature"
                  ref="attributes-panel"
                  :editing="editing"
                  :fields="currentFeature"
                  :dictValues="dictValues"
                />
              </div>
            </div>
            <div v-show="indexActiveTab === 2">
              <AttachmentsPanel
                ref="attachments-panel"
                v-if="currentFeature && Object.keys(featureAttachments).length > 0"
                :attachmentsIds="currentFeature.properties.__attachments"
                :lid="$route.params.layerId"
                :fid="currentFeature.properties.id"
                :permission="permission"
                :users-group="usersGroup"
                @addIds="addIds"
                @deleteIds="deleteIds"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { register } from "ol/proj/proj4.js";
import proj4 from "proj4";
import WMTSTileGrid from "ol/tilegrid/WMTS.js";
import turfBuffer from '@turf/buffer';
import moment from 'moment';
import Map from 'ol/Map';
import View from 'ol/View';
import { fromLonLat, get as getProjection } from 'ol/proj';
import { Draw, Modify } from 'ol/interaction';
import { MVT, WMTSCapabilities, GeoJSON } from 'ol/format';
import {
  VectorTile as VectorTileSource,
  Vector as VectorSource,
  TileWMS,
  XYZ,
  WMTS
} from 'ol/source';
import {
  VectorTile as VectorTileLayer,
  Vector as VectorLayer,
  Tile as TileLayer,
  Group as LayerGroup
} from 'ol/layer';
import { Circle, Fill, Stroke, Style, RegularShape, Text } from 'ol/style';
import {
  LineString,
  Polygon,
  Point,
  MultiPoint,
  MultiLineString,
  MultiPolygon
} from 'ol/geom.js';
import { getArea, getLength } from 'ol/sphere.js';
import { unByKey } from 'ol/Observable.js';
import Overlay from 'ol/Overlay.js';
import { optionsFromCapabilities } from 'ol/source/WMTS';
import FeatureManagerTable from '@/components/FeatureManagerTable.vue';
import AttributesPanel from '@/components/AttributesPanel.vue';
import AttachmentsPanel from '@/components/AttachmentsPanel.vue';
import BufferTable from '@/components/BufferTable.vue';
import FiltersPanel from '@/components/FiltersPanel.vue';
import InputNumber from '@/components/InputNumber';
import Datepicker from 'vuejs-datepicker';
import '@/assets/css/feature-manager.css';
import draggable from 'vuedraggable';

export default {
  components: {
    AttachmentsPanel,
    AttributesPanel,
    BufferTable,
    FeatureManagerTable,
    FiltersPanel,
    InputNumber,
    Datepicker,
    draggable
  },
  data: () => ({
    activeLayerName: '',
    activeServices: [],
    addFeatureDialog: false,
    baseLayers: ['OpenStreetMap', 'Ortofotomapa', 'OrtofotomapaDwa'],
    bufferColumns: [
      {
        head: true,
        sortable: true,
        filter: true
      }
    ],
    bufferDialog: false,
    bufferFeatureGeometry: undefined,
    bufferFeatures: [],
    bufferValue: undefined,
    columnFilterDecisionDialogView: false,
    columns: [
      {
        head: true,
        sortable: true,
        filter: true
      }
    ],
    currentBaseLayer: 'OpenStreetMap',
    currentColumnFilters: [],
    currentFeature: undefined,
    dictValues: [],
    labels: [],
    layerGeometry: undefined,
    layerType: undefined,
    draw: undefined,
    editing: false,
    editingDataCopy: undefined,
    indexActiveTab: 0,
    isBuffer: false,
    isBufferTableShowing: false,
    isDrawing: false,
    isInfoDialogVisible: false,
    isMeasure: false,
    isMeasureShow: false,
    isTableShow: true,
    items: [],
    layers: [],
    layersAll: [],
    layerStyle: undefined,
    measureTooltip: undefined,
    measureTooltipElement: undefined,
    measureType: undefined,
    newFeatureProperties: {},
    permission: [],
    //project: { name: 'Nazwa projektu' },
    project: undefined,
    projectName: '',
    rotationValue: 0,
    searchCount: 0,
    searchItemValue: '',
    selectedColumnFilters: [],
    selectedFieldName: undefined,
    selectedLayer: undefined,
    selectedRows: [],
    usersGroup: undefined,
    activeOtherLayers: [],
    allOtherLayers: [],
    otherLayers: [],
    searchLayer: ''
  }),
  computed: {
    layersOutOfProject() {
      if (!this.layersAll) {
        return false;
      }
      const ids = this.otherLayers.map(l => l.id);
      return this.layersAll.filter(
        layer =>
          !ids.includes(layer.id) && layer.id !== this.$route.params.layerId
      );
    },
    layersFilteredByName() {
      if (!this.layersOutOfProject) {
        return false;
      }
      return this.layersOutOfProject.filter(layer =>
        layer.name.toLowerCase().includes(this.searchLayer.toLowerCase())
      );
    },
    activeLayer() {
      return this.$store.getters.getActiveLayer;
    },
    apiUrl() {
      return this.$store.getters.getApiUrl;
    },
    currentFeatureFieldsNames() {
      if (this.currentFeature) {
        return Object.keys(this.currentFeature.properties);
      } else {
        return [];
      }
    },
    featureAttachments() {
      return this.$store.getters.getFeatureAttachments;
    },
    featureTypes() {
      return this.$store.getters.getCurrentFeaturesTypes;
    },
    layerName() {
      return this.activeLayerName;
    },
    mapCenter() {
      return this.$store.getters.getMapCenter;
    },
    mapZoom() {
      return this.$store.getters.getMapZoom;
    },
    services() {
      return this.$store.getters.getServices;
    },
    showMeasureTitle() {
      if (this.isMeasureShow) {
        return this.$i18n.t('featureManager.map.hideMeasurements');
      } else if (this.isMeasure) {
        return this.$i18n.t('featureManager.map.endMeasurements');
      } else {
        return this.$i18n.t('featureManager.map.showMeasurements');
      }
    },
    token() {
      return this.$store.getters.getToken;
    },
    user() {
      return this.$store.getters.getUser;
    }
  },
  filters: {
    maxLength: val => {
      if (val.length > 30) {
        return `${val.slice(0, 30)}...`;
      }
      return val;
    }
  },
  methods: {
    addLayer(layer) {
      if (!layer) {
        return;
      }
      this.otherLayers.push({ id: layer.id, name: layer.name });
      this.activeOtherLayers.push(layer.id);
      if (Number.isInteger(layer.id)) {
        this.createServiceLayer(layer);
      } else {
        this.createOtherMVTLayer(layer.id, layer.name);
      }
    },
    createMVTLayer(id, name) {
      return new VectorTileLayer({
        name: name,
        renderBuffer: 256,
        source: new VectorTileSource({
          cacheSize: 1,
          format: new MVT(),
          url: `${
            this.apiUrl
          }/mvt/${id}/{z}/{x}/{y}?token=${localStorage.getItem('token')}`
        }),
        style: f => this.styleFeatures(f, true)
      });
    },
    createServiceLayer(layer) {
      const serviceLayer = new TileLayer({
        name: layer.name,
        visible: true,
        source: new TileWMS({
          url: layer.url,
          params: {
            LAYERS: layer.layers,
            TILED: true
            //SRS: 'EPSG:2180'
          }
        })
      });
      this.getLayerByName('otherLayers')
        .getLayers()
        .getArray()
        .push(serviceLayer);
    },
    removeLayer(name) {
      const index = this.otherLayers.map(l => l.name).indexOf(name);
      this.otherLayers.splice(index, 1);
      const otherLayersArray = this.getLayerByName('otherLayers')
        .getLayers()
        .getArray();
      const indexGroup = otherLayersArray.map(l => l.get('name')).indexOf(name);
      otherLayersArray.splice(indexGroup, 1);
      this.map.updateSize();
    },
    async createOtherMVTLayer(id, name) {
      const r = await this.$store.dispatch('getLayerStyle', id);
      if (r.status === 200) {
        const otherLabels = r.obj.style.labels;
        const otherLayerStyle = r.obj.style;
        let otherLayerType = undefined;
        if (otherLayerStyle.renderer === 'single') {
          otherLayerType = r.obj.style.type;
        }
        const otherLayer = new VectorTileLayer({
          name: name,
          renderBuffer: 256,
          source: new VectorTileSource({
            cacheSize: 1,
            format: new MVT(),
            url: `${
              this.apiUrl
            }/mvt/${id}/{z}/{x}/{y}?token=${localStorage.getItem('token')}`
          }),
          style: feature => {
            const styles = [];
            const labelsToShow = [];
            otherLabels.forEach(el => {
              labelsToShow.push(feature.getProperties()[el]);
            });
            const featStyle = new Style({
              text: new Text({
                text: labelsToShow.join(' '),
                fill: new Fill({ color: 'white' }),
                stroke: new Stroke({ color: 'black', width: 4 }),
                offsetY: -10
              })
            });
            if (otherLayerType) {
              const stroke = new Stroke({
                color: `rgba(${otherLayerStyle['stroke-color']})`,
                width: `${otherLayerStyle['stroke-width']}`
              });
              const fill = new Fill({
                color: `rgba(${otherLayerStyle['fill-color']})`
              });
              if (otherLayerType === 'point') {
                featStyle.setImage(
                  new Circle({
                    fill,
                    stroke,
                    radius: otherLayerStyle.width
                  })
                );
              } else if (
                otherLayerStyle === 'square' ||
                otherLayerStyle === 'triangle'
              ) {
                featStyle.setImage(
                  new RegularShape({
                    fill,
                    stroke,
                    points: otherLayerType === 'square' ? 4 : 3,
                    radius: otherLayerStyle.width,
                    angle: otherLayerType === 'square' ? Math.PI / 4 : 0
                  })
                );
              } else if (
                otherLayerType === 'polygon' ||
                otherLayerType === 'line'
              ) {
                featStyle.setFill(fill);
                featStyle.setStroke(stroke);
              } else if (
                otherLayerType === 'dashed' ||
                otherLayerType === 'dotted'
              ) {
                const lineDash =
                  otherLayerType === 'dashed' ? [10, 10] : [1, 10];
                stroke.setLineDash(lineDash);
                featStyle.setStroke(stroke);
              }
            } else {
              const attr = feature.get(otherLayerStyle.attribute);
              const filteredFeat = otherLayerStyle.categories.find(
                el => el.value == attr
              );
              if (filteredFeat) {
                const stroke = new Stroke({
                  color: `rgba(${filteredFeat['stroke-color']})`,
                  width: `${filteredFeat['stroke-width']}`
                });
                const fill = new Fill({
                  color: `rgba(${filteredFeat['fill-color']})`
                });
                if (filteredFeat.type === 'point') {
                  featStyle.setImage(
                    new Circle({
                      fill,
                      stroke,
                      radius: filteredFeat.width
                    })
                  );
                } else {
                  featStyle.setFill(fill);
                  featStyle.setStroke(stroke);
                }
              } else {
                featStyle.setImage(
                  new Circle({
                    fill: new Fill({
                      color: [250, 250, 250, 0.4]
                    }),
                    stroke: new Stroke({
                      color: [51, 153, 204, 1],
                      width: 1
                    }),
                    radius: 2
                  })
                );
              }
            }
            return featStyle;
          }
        });
        this.getLayerByName('otherLayers')
          .getLayers()
          .getArray()
          .push(otherLayer);
        this.map.updateSize();
      } else {
        this.$alertify.error(this.$i18n.t('default.errorStyle'));
      }
    },
    async createStyle() {
      const r = await this.$store.dispatch(
        'getLayerStyle',
        this.$route.params.layerId
      );
      if (r.status === 200) {
        this.labels = r.obj.style.labels;
        this.layerStyle = r.obj.style;
        if (this.layerStyle.renderer === 'single') {
          this.layerType = r.obj.style.type;
          this.setLayerGeometry(r.obj.style.type);
        } else {
          this.setLayerGeometry(r.obj.style.categories[0].type);
        }
      } else {
        this.$alertify.error(this.$i18n.t('default.errorStyle'));
      }
    },
    async deleteFeature() {
      this.$alertify
        .confirm(
          this.$i18n.t('featureManager.deleteFeatureConfirm'),
          async () => {
            const r = await this.$store.dispatch('deleteFeature', {
              lid: this.$route.params.layerId,
              fid: this.currentFeature.properties.id
            });
            if (r.status === 200) {
              this.editingEndOperations();
              this.refreshVectorSource(this.getLayerByName('features'));
              const featIdx = this.items.findIndex(
                el => el.id === this.currentFeature.properties.id
              );
              this.items.splice(featIdx, 1);
              this.$refs['table-data'].$recompute('windowItems'); // update table data
              const featIdxLay = this.activeLayer.features.findIndex(
                el => el.properties.id === this.currentFeature.properties.id
              );
              this.activeLayer.features.splice(featIdxLay, 1);
              this.selectFeature(undefined);
            }
          },
          () => {}
        )
        .set({ title: this.$i18n.t('featureManager.deleteFeatureHeader') })
        .set({
          labels: {
            ok: this.$i18n.t('default.delete'),
            cancel: this.$i18n.t('default.cancel')
          }
        });
    },
    async downloadLayer(rows) {
      let filteredIds;
      if (rows.length === 0) {
        filteredIds = {};
      } else {
        filteredIds = {
          filter_ids: rows.map(el => el.id)
        };
      }
      const r = await this.$store.dispatch('downloadLayer', {
        lid: this.$route.params.layerId,
        body: filteredIds
      });
      if (r.status === 200) {
        this.$i18n.t('default.success');
        this.saveFile(r);
        this.selectedRows = [];
      } else {
        this.$i18n.t('featureManager.downloadError');
      }
    },
    async downloadObjectsArray() {
      const r = await this.$store.dispatch('bufferAnalysis', {
        lid: this.selectedLayer.id,
        body: this.bufferFeatureGeometry,
        responseType: 'xlsx'
      });
      if (r.status === 200) {
        const blob = new Blob([r.data]);
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.setAttribute('download', `${this.selectedLayer.name}_bufor.xlsx`);
        link.click();
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    async generateObjectsArray() {
      const r = await this.$store.dispatch('bufferAnalysis', {
        lid: this.selectedLayer.id,
        body: this.bufferFeatureGeometry,
        responseType: 'json'
      });
      if (r.status === 200) {
        this.isBufferTableShowing = true;
        if (r.body.data.length > 0) {
          Object.keys(r.body.data[0]).forEach(el => {
            this.bufferColumns.push({
              key: el,
              name: el,
              sortable: true,
              filter: true
            });
          });
          r.body.data.forEach(feat => {
            const tempItem = {};
            Object.entries(feat).forEach(([k, v]) => {
              if (this.featureTypes[k] === 'timestamp without time zone') {
                tempItem[k] = moment(v).isValid()
                  ? moment(v)
                      .locale('pl')
                      .format('L')
                  : '';
              } else {
                tempItem[k] = v;
              }
            });
            this.bufferFeatures.push(tempItem);
          });
        }
        this.$modal.hide('buffer');
        this.$modal.show('bufferTable');
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    async generateDistance() {
      const r = await this.$store.dispatch('distanceAnalysisXlsx', {
        lid: this.$route.params.layerId,
        fid: this.currentFeature.properties.id,
        body: {
          buffer: parseFloat(this.bufferValue),
          name: this.selectedFieldName
        }
      });
      if (r.status === 200) {
        this.$modal.hide('distance');
        const blob = new Blob([r.data]);
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.setAttribute('download', `${this.layerName}_dystans.xlsx`);
        link.click();
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    async getLayers() {
      if (this.allOtherLayers.length === 0) {
        try {
          const r = await this.$store.dispatch('getLayers');
          const layers = r.body.layers;
          this.activeLayerName = layers.filter(
            layer => layer.id === this.$route.params.layerId
          )[0].name;
          this.layers = layers.filter(
            layer => layer.id !== this.$route.params.layerId
          );
          this.allOtherLayers = r.body.layers;
        } catch (error) {
          this.$alertify.error(
            // this.$i18n.t('default.errorStyle')
            error
          );
        }
      }
    },
    async getPermissions() {
      const r = await this.$store.dispatch('getPermissions');
      const usersPerms = r.obj.permissions.find(
        el => el.id === this.$route.params.layerId
      );
      this.permission = usersPerms.users[this.user];
    },
    async getServices() {
      const r = await this.$store.dispatch('getServices');
      this.$store.commit('setServices', r.body.services);
    },
    async getProject() {
      const r = await this.$store.dispatch(
        'getProject',
        this.$route.query.projectId
      );
      this.$route.params.layerId = r.obj.data.active_layer_id;
      this.project = r.obj.data;
      if (!this.project.permission_to_each_additional_layer) {
        this.$alertify.error(
          this.$i18n.t('default.additionalLayerAccessDenied')
        );
      }
      this.init();
    },
    async getSettings() {
      const res = await this.$store.dispatch(
        'getCurrentSettings',
        this.$route.params.layerId
      );
      const bbox = new GeoJSON().readFeature(res.obj.settings.bbox, {
        featureProjection: 'EPSG:3857',
        dataProjection: 'EPSG:4326'
      });
      if (this.project) {
        this.map.getView().setCenter(this.project.map_center.coordinates);
        this.map.getView().setZoom(this.project.map_zoom);
      } else {
        this.map.getView().fit(bbox.getGeometry(), {
          maxZoom: 16,
          duration: 500
        });
      }
      this.$store.commit('setCurrentFeaturesTypes', res.obj.settings.columns);
    },
    async getUsers() {
      const r = await this.$store.dispatch('getUsers');
      if (r.status === 200) {
        this.usersGroup = r.obj.users[this.user];
        this.$store.commit('setUsersWithGroups', r.obj.users);
      }
    },
    async saveEditing() {
      const fid = this.currentFeature.properties.id;
      const features = this.getLayerByName('featuresVector')
        .getSource()
        .getFeatures();
      const vectorFeature = features.find(el => el.get('id') === fid).clone();
      this.currentFeature.geometry.coordinates = vectorFeature
        .getGeometry()
        .transform('EPSG:3857', 'EPSG:4326')
        .getCoordinates();
      const tempItem = this.dateToTimestamp(this.currentFeature);
      const payload = {
        body: tempItem,
        lid: this.$route.params.layerId,
        fid
      };
      this.$alertify.warning(this.$i18n.t('default.editInProgress'));
      const r = await this.$store.dispatch('editFeature', payload);
      if (r.status === 200) {
        this.editingEndOperations(fid);
        this.refreshVectorSource(this.getLayerByName('features'));
        const itemsIdx = this.items.findIndex(el => el.id === fid);
        this.items[itemsIdx] = this.formatDate(r.obj).properties;
        this.currentFeature = r.obj;
        this.$refs['table-data'].$recompute('windowItems'); // update table data
        this.$refs['table-data'].$recompute('filteredItems'); // update table data
        this.$refs['table-data'].$recompute('searchedItems'); // update table data
        this.$refs['table-data'].$recompute('sortedItems');
        this.$refs['table-data'].setColumnsLengths(); // update columns lengths in table
        this.$alertify.success(this.$i18n.t('default.editSuccess'));
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    async saveNewFeature() {
      const newFeature = this.getLayerByName('newFeature')
        .getSource()
        .getFeatures()[0];
      const coords = newFeature
        .getGeometry()
        .transform('EPSG:3857', 'EPSG:4326')
        .getCoordinates();
      const featureCopy = JSON.parse(JSON.stringify(this.newFeatureProperties));
      Object.entries(this.newFeatureProperties).forEach(k => {
        if (!this.newFeatureProperties[k[0]]) return;

        if (this.featureTypes[k[0]] === 'integer') {
          featureCopy[k[0]] = parseInt(this.newFeatureProperties[k[0]], 10);
        } else if (this.featureTypes[k[0]] === 'real') {
          featureCopy[k[0]] = parseFloat(this.newFeatureProperties[k[0]]);
        } else if (this.featureTypes[k[0]] === 'timestamp without time zone') {
          featureCopy[k[0]] = parseInt(
            moment(this.newFeatureProperties[k[0]]).format('X')
          );
        }
      });
      const r = await this.$store.dispatch('addFeature', {
        lid: this.$route.params.layerId,
        body: {
          geometry: {
            coordinates: coords,
            type: this.layerGeometry
          },
          properties: featureCopy,
          type: 'Feature'
        }
      });

      if (r.status === 201) {
        this.refreshVectorSource(this.getLayerByName('features'));
        this.clearFeatureAdding();
        const tempItem = this.formatDate(r.obj);
        this.items.push(tempItem.properties);
        this.activeLayer.features.push(r.obj);
        this.$refs['table-data'].$recompute('windowItems'); // update table data
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    async saveProject() {
      const otherLayersIds = [];
      for (let layer of this.otherLayers) {
        otherLayersIds.push(layer.id);
      }
      const payload = {
        active_layer_id: this.$route.params.layerId,
        additional_layers_ids: otherLayersIds.filter(
          id => !Number.isInteger(id)
        ),
        service_layers_ids: otherLayersIds.filter(id => Number.isInteger(id)),
        map_center: {
          coordinates: this.map.getView().getCenter(),
          type: 'Point'
        },
        map_zoom: this.map.getView().getZoom(),
        name: this.projectName
      };
      if (this.project) {
        const data = { pid: this.project.id, payload: payload };
        const r = await this.$store.dispatch('putProject', data);
        if (r.status === 204) {
          this.$alertify.success(this.$i18n.t('featureManager.projectSaved'));
          this.project = data.payload;
          this.project.id = data.pid;
          this.$modal.hide('saveProject');
        } else {
          this.$alertify.error(this.$i18n.t('default.error'));
        }
      } else {
        const r = await this.$store.dispatch('postProject', payload);
        if (r.status === 201) {
          this.$alertify.success(this.$i18n.t('featureManager.projectCreated'));
          this.project = payload;
          this.project.id = r.body.data;
          const newUrl = `../feature_manager?projectId=${r.body.data}`;
          window.history.pushState(null, '', newUrl);
          this.$modal.hide('saveProject');
        } else {
          this.$alertify.error(this.$i18n.t('default.error'));
        }
      }
    },
    addAdditionalLayers() {
      this.layersAll = this.getLayersAll();
      if (this.project) {
        for (let oL of this.project.additional_layers_ids) {
          if (oL !== this.$route.params.layerId) {
            this.addLayer(this.layersOutOfProject.find(l => l.id === oL));
          }
        }
        for (let oL of this.project.service_layers_ids) {
          this.addLayer(this.layersOutOfProject.find(l => l.id === oL));
        }
      }
    },
    addIds(ids) {
      if (this.currentFeature.properties.__attachments) {
        this.currentFeature.properties.__attachments += `;${ids}`;
        this.items.find(
          i => i.id === this.currentFeature.properties.id
        ).__attachments += `;${ids}`;
      } else {
        this.currentFeature.properties.__attachments = ids;
        this.items.find(
          i => i.id === this.currentFeature.properties.id
        ).__attachments = ids;
      }
    },
    formatDate(feature) {
      const copy = JSON.parse(JSON.stringify(feature));
      Object.entries(copy.properties).forEach(([k, v]) => {
        if (this.featureTypes[k] === 'timestamp without time zone') {
          copy.properties[k] = moment(v).isValid()
            ? moment(v)
                .locale('pl')
                .format('L')
            : '';
        } else {
          copy.properties[k] = v;
        }
      });
      return copy;
    },
    dateToTimestamp(feature) {
      let featureCopy = JSON.parse(JSON.stringify(feature));
      Object.entries(feature.properties).forEach(k => {
        if (!feature.properties[k[0]]) return;

        if (this.featureTypes[k[0]] === 'integer') {
          featureCopy.properties[k[0]] = parseInt(feature.properties[k[0]], 10);
        } else if (this.featureTypes[k[0]] === 'real') {
          featureCopy.properties[k[0]] = parseFloat(feature.properties[k[0]]);
        } else if (this.featureTypes[k[0]] === 'timestamp without time zone') {
          featureCopy.properties[k[0]] = parseInt(
            moment.utc(feature.properties[k[0]]).format('X')
          );
        }
      });
      return featureCopy;
    },
    addMeasurementInteraction(layerName, type) {
      let drawInteraction = new Draw({
        source: layerName.getSource(),
        type: type,

        style: feature => {
          const geometry = feature.getGeometry();
          const styles = [];

          if (type === 'LineString' && geometry instanceof LineString) {
            geometry.forEachSegment((start, end) => {
              const line = new LineString([start, end]);
              styles.push(
                new Style({
                  geometry: line,
                  fill: new Fill({
                    color: 'rgba(0, 142, 132, 0.3)'
                  }),
                  stroke: new Stroke({
                    color: 'rgba(0, 0, 0, 0.5)',
                    lineDash: [10, 10],
                    width: 2
                  }),
                  text: new Text({
                    text: this.formatLength(line),
                    font: '15px sans-serif',
                    fill: new Fill({ color: 'black' }),
                    placement: 'line',
                    stroke: new Stroke({
                      color: 'rgba(30, 42, 53, 0.3)',
                      width: 3
                    }),
                    offsetX: -20,
                    offsetY: 20
                  }),
                  image: new Circle({
                    radius: 5,
                    stroke: new Stroke({
                      color: '#1e2a35'
                    }),
                    fill: new Fill({
                      color: 'rgba(30, 42, 53, 0.5)'
                    })
                  })
                })
              );
            });
          } else {
            styles.push(
              new Style({
                fill: new Fill({
                  color: 'rgba(30, 42, 53, 0.3)'
                }),
                stroke: new Stroke({
                  color: 'rgba(0, 0, 0, 0.5)',
                  lineDash: [10, 10],
                  width: 2
                }),
                image: new Circle({
                  radius: 5,
                  stroke: new Stroke({
                    color: '#1e2a35'
                  }),
                  fill: new Fill({
                    color: 'rgba(30, 42, 53, 0.5)'
                  })
                })
              })
            );
          }
          return styles;
        }
      });
      drawInteraction.set('name', 'drawMeasurement');
      this.map.addInteraction(drawInteraction);

      let listener;
      drawInteraction.on('drawstart', evt => {
        this.getLayerByName('measurement')
          .getSource()
          .clear();

        this.sketch = evt.feature;

        listener = this.sketch.getGeometry().on('change', evt => {
          if (evt.target instanceof Polygon) {
            let result = `${this.formatArea(
              evt.target
            )} <br> ${this.formatLength(evt.target)}`;
            this.measureTooltipElement.innerHTML = result;
            this.measureTooltip.setPosition(
              evt.target.getInteriorPoint().getCoordinates()
            );
          } else if (evt.target instanceof LineString) {
            this.measureTooltipElement.innerHTML = this.formatLength(
              evt.target
            );
            this.measureTooltip.setPosition(evt.target.getLastCoordinate());
          }
        });
      });

      drawInteraction.on('drawend', () => {
        this.measureTooltip.setOffset([0, -7]);
        this.sketch = null;
        unByKey(listener);
      });
    },
    cancelEditing() {
      this.currentFeature = this.editingDataCopy;
      this.editingEndOperations();
    },
    clearBufferDialog() {
      this.getLayerByName('buffer')
        .getSource()
        .clear();
      this.selectedLayer = undefined;
      this.isBuffer = false;
    },
    clearFeatureAdding() {
      this.isDrawing = false;
      this.addFeatureDialog = false;
      this.getLayerByName('newFeature')
        .getSource()
        .clear();
      this.getInteractionByName('drawInteraction').setActive(false);
      this.newFeatureProperties = {};
    },
    closeBufferDialog() {
      if (!this.isBufferTableShowing) {
        this.getLayerByName('buffer')
          .getSource()
          .clear();
        this.bufferValue = undefined;
        this.isBuffer = false;
        this.selectedLayer = undefined;
      }
    },
    closeBufferTableDialog() {
      this.getLayerByName('buffer')
        .getSource()
        .clear();
      this.bufferValue = undefined;
      this.isBuffer = false;
      this.selectedLayer = undefined;
      this.bufferFeatureGeometry = undefined;
      this.bufferFeatures = [];
      this.isBufferTableShowing = false;
      this.bufferColumns = [
        {
          head: true,
          sortable: true,
          filter: true
        }
      ];
    },
    changeBaseLayer(layerName) {
      this.map
        .getLayers()
        .getArray()
        .forEach(el => {
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
    createMeasureTooltip() {
      this.measureTooltipElement = document.createElement('div');
      this.measureTooltipElement.style =
        'position: relative; background: rgba(0,0,0,0.8); border-radius: 4px; color: white; padding: 4px 8px; opacity: 0.7; white-space: nowrap; font-weight: bold';
      this.measureTooltip = new Overlay({
        element: this.measureTooltipElement,
        offset: [0, -15],
        positioning: 'bottom-center'
      });
      this.map.addOverlay(this.measureTooltip);
    },
    createModifyInteraction() {
      const modifyInteraction = new Modify({
        source: this.getLayerByName('featuresVector').getSource()
      });
      modifyInteraction.set('name', 'modifyInteraction');
      modifyInteraction.setActive(false);
      this.map.addInteraction(modifyInteraction);
    },
    createSelectInteraction() {
      let active = true;
      this.map.addLayer(
        new VectorLayer({
          name: 'featuresVectorSelection',
          visible: true,
          source: new VectorSource({}),
          style: f => this.styleFeatures(f, false, true)
        })
      );
      this.map.on('click', evt => {
        if (
          !active ||
          this.isInteractionActive('modifyInteraction') ||
          this.isInteractionActive('drawInteraction') ||
          this.isInteractionActive('drawMeasurement')
        )
          return;

        const feature = this.map.forEachFeatureAtPixel(
          evt.pixel,
          feat => feat,
          {
            hitTolerance: 5,
            layerFilter: layer => layer.get('name') === 'features'
          }
        );
        if (!feature) {
          this.selectFeature(feature);
        } else {
          if (this.items.length < 1) {
            this.$alertify.warning(this.$i18n.t('featureManager.waitForData'));
            return;
          } else {
            if (!feature.properties_) return;
            else {
              this.selectFeature(feature);
            }
          }
        }
      });
      return {
        setActive(value) {
          active = value;
        },
        getActive() {
          return active;
        }
      };
    },
    deleteIds(idsToDelete) {
      const ids = this.currentFeature.properties.__attachments.split(';');
      const diff = ids.filter(x => !idsToDelete.includes(x));
      this.currentFeature.properties.__attachments = diff.join(';');
      this.items.find(
        i => i.id === this.currentFeature.properties.id
      ).__attachments = diff.join(';');
    },
    drawFeatureEnd() {
      this.isDrawing = false;
      this.getInteractionByName('drawInteraction').setActive(false);
      // const feature = this.getLayerByName('newFeature').getSource().getFeatures()[0];
      this.addFeatureDialog = true;
    },
    drawNewFeature() {
      this.selectFeature(undefined);
      this.isDrawing = true;
      if (!this.getInteractionByName('drawInteraction')) {
        const source = new VectorSource({ wrapX: false });
        const vector = new VectorLayer({ source, name: 'newFeature' });
        this.map.addLayer(vector);
        let drawType;
        if (this.layerGeometry === 'polygon') {
          drawType = 'Polygon';
        } else if (this.layerGeometry === 'lineString') {
          drawType = 'LineString';
        } else {
          drawType = 'Point';
        }

        const draw = new Draw({
          source,
          type: drawType
        });
        draw.set('name', 'drawInteraction');
        this.map.addInteraction(draw);
        draw.on('drawend', () => {
          this.$nextTick(() => this.drawFeatureEnd());
        });
      } else {
        this.getInteractionByName('drawInteraction').setActive(true);
      }
    },
    editAttributes() {
      this.editing = true;
      this.editingDataCopy = JSON.parse(JSON.stringify(this.currentFeature));
      this.getLayerByName('featuresVectorSelection')
        .getSource()
        .clear();
      this.activeLayer.features.forEach(feature => {
        if (feature.properties.id == this.currentFeature.properties.id) {
          const tempFeature = new GeoJSON().readFeature(feature, {
            featureProjection: 'EPSG:3857',
            dataProjection: 'EPSG:4326'
          });
          this.getLayerByName('featuresVector')
            .getSource()
            .addFeature(tempFeature);
        }
      });
      if (!this.getInteractionByName('modifyInteraction')) {
        this.createModifyInteraction();
      }
      this.getLayerByName('featuresVector').setVisible(true);
      this.getInteractionByName('modifyInteraction').setActive(true);
      this.refreshVectorSource(this.getLayerByName('features'));
    },
    editingEndOperations(edited = false) {
      this.getLayerByName('features').setVisible(true);
      this.getInteractionByName('modifyInteraction').setActive(false);
      this.getLayerByName('featuresVector')
        .getSource()
        .clear();
      this.editing = false;
      this.refreshVectorSource(this.getLayerByName('features'));
      if (edited) {
        this.selectFeatureById(edited);
      }
    },
    formatArea(polygon) {
      var area = getArea(polygon);
      var output;
      if (area > 10000) {
        output =
          Math.round((area / 1000000) * 100) / 100 + ' ' + 'km<sup>2</sup>';
      } else {
        output = Math.round(area * 100) / 100 + ' ' + 'm<sup>2</sup>';
      }
      return output;
    },
    formatLength(line) {
      var length = getLength(line);
      var output;
      if (length > 100) {
        output = Math.round((length / 1000) * 100) / 100 + ' ' + 'km';
      } else {
        output = Math.round(length * 100) / 100 + ' ' + 'm';
      }
      return output;
    },
    getInteractionByName(name) {
      return this.map
        .getInteractions()
        .getArray()
        .find(i => i.get('name') === name);
    },
    getLayerByName(name) {
      const layer = this.map
        .getLayers()
        .getArray()
        .find(l => l.get('name') === name);
      return layer
        ? layer
        : this.map
            .getLayers()
            .getArray()
            .find(l => l.get('name') === 'otherLayers')
            .getLayers()
            .getArray()
            .find(l => l.get('name') === name);
    },
    getLayersAll() {
      let layersAll = [];
      if (this.allOtherLayers && this.services) {
        layersAll = [...this.allOtherLayers, ...this.services].sort((a, b) =>
          a.name > b.name ? 1 : b.name > a.name ? -1 : 0
        );
      } else if (this.allOtherLayers) {
        layersAll = this.allOtherLayers;
      } else if (this.services) {
        layersAll = this.services;
      }
      return layersAll;
    },
    generateBuffer() {
      this.getLayerByName('buffer')
        .getSource()
        .clear();
      let buffer = turfBuffer(this.currentFeature, this.bufferValue / 1000, {
        units: 'kilometers'
      });
      if (buffer) {
        this.bufferFeatureGeometry = { geometry: buffer.geometry };
        let bufferFeature = new GeoJSON().readFeature(buffer, {
          featureProjection: 'EPSG:3857',
          dataProjection: 'EPSG:4326'
        });
        if (bufferFeature) {
          this.getLayerByName('buffer')
            .getSource()
            .addFeature(bufferFeature);
          this.$alertify.success(
            this.$i18n.t('featureManager.bufferGenerateSuccess')
          );
          this.isBuffer = true;
        }
      } else {
        this.$alertify.error(
          this.$i18n.t('featureManager.bufferGenerateError')
        );
      }
    },
    goToSettings() {
      this.$router.push({
        name: 'settings',
        params: {
          layerId: this.$route.params.layerId,
          layer: {
            id: this.$route.params.layerId,
            name: this.$route.params.layerName
          },
          vectorLayersList: this.$route.params.vectorLayersList
        }
      });
    },
    initOrtofotoDwa() {
      return new Promise((resolve, reject) => {
        const parser = new WMTSCapabilities();
        fetch(
          'https://mapy.geoportal.gov.pl/wss/service/WMTS/guest/wmts/ORTO?SERVICE=WMTS&REQUEST=GetCapabilities'
        )
          .then(response => response.text())
          .then(text => {
            const result = parser.read(text);
            const options = optionsFromCapabilities(result, {
              layer: 'ORTOFOTOMAPA',
              matrixSet: 'EPSG:2180'
            });
            resolve(
              this.map.addLayer(
                new TileLayer({
                  opacity: 1,
                  visible: false,
                  name: 'OrtofotomapaDwa',
                  group: 'baselayers',
                  zIndex: -1000,
                  source: new WMTS({
                    url:
                      'https://mapy.geoportal.gov.pl/wss/service/WMTS/guest/wmts/ORTO',
                    matrixSet: 'EPSG:2180',
                    format: 'image/png',
                    projection: getProjection('EPSG:2180'),
                    tileGrid: new WMTSTileGrid({
                      origin: [100000, 850000],
                      matrixIds: options.tileGrid.matrixIds_,
                      resolutions: options.tileGrid.resolutions_,
                      tileSize: 512
                    }),
                    style: 'default',
                    wrapX: true
                  })
                })
              )
            );
          })
          .catch(err => {
            this.$alertify.error(this.$i18n.t('featureManager.ortoError'));
            reject(err);
          });
      });
    },
    initOrtofoto() {
      return new Promise((resolve, reject) => {
        const parser = new WMTSCapabilities();
        fetch(
          'https://mapy.geoportal.gov.pl/wss/service/WMTS/guest/wmts/ORTO?SERVICE=WMTS&REQUEST=GetCapabilities'
        )
          .then(response => response.text())
          .then(text => {
            const result = parser.read(text);
            const options = optionsFromCapabilities(result, {
              layer: 'ORTOFOTOMAPA',
              matrixSet: 'EPSG:4326'
            });
            resolve(
              this.map.addLayer(
                new TileLayer({
                  opacity: 1,
                  visible: false,
                  name: 'Ortofotomapa',
                  group: 'baselayers',
                  zIndex: -1000,
                  source: new WMTS({
                    url:
                      'https://mapy.geoportal.gov.pl/wss/service/WMTS/guest/wmts/ORTO',
                    matrixSet: 'EPSG:4326',
                    format: 'image/png',
                    projection: getProjection('EPSG:4326'),
                    tileGrid: options.tileGrid,
                    style: 'default',
                    wrapX: true
                  })
                })
              )
            );
          })
          .catch(err => {
            this.$alertify.error(this.$i18n.t('featureManager.ortoError'));
            reject(err);
          });
      });
    },
    isFiltersValidated(filters) {
      return filters.every(
        filter =>
          filter.operation !== '' && filter.column !== '' && filter.value !== ''
      );
    },
    isInteractionActive(interaction) {
      if (
        this.getInteractionByName(interaction) &&
        this.getInteractionByName(interaction).getActive()
      ) {
        return true;
      }
      return false;
    },
    openBufferDialog() {
      this.$modal.show('buffer');
    },
    openAddLayerModal() {
      this.$modal.show('addLayer');
    },
    openColumnFilterDecision() {
      const self = this;

      const handle = key => {
        if (key === 'accept') {
          self.currentColumnFilters = JSON.parse(
            JSON.stringify(self.selectedColumnFilters)
          );

          self.columnFilterDecisionDialogView = false;
          self.$off('columnFilterDecision', handle);
          // self.$emit('update-column-filters');
        } else if (key === 'clear') {
          self.selectedColumnFilters = [];
        } else {
          self.selectedColumnFilters = JSON.parse(
            JSON.stringify(self.currentColumnFilters)
          );

          self.columnFilterDecisionDialogView = false;
          self.$off('columnFilterDecision', handle);
        }
      };

      self.$on('columnFilterDecision', handle);
      self.columnFilterDecisionDialogView = true;
    },
    openDistanceDialog() {
      this.$modal.show('distance');
    },
    openRotationDialog() {
      this.$modal.show('rotation');
    },
    refreshVectorSource(layer) {
      const source = layer.getSource();
      source.tileCache.expireCache({});
      source.tileCache.clear();
      source.refresh();
      layer.changed();
    },
    rotateMapByAngle(angle) {
      let radians = (angle * Math.PI * 2) / 360;
      this.map.getView().setRotation(radians);
    },
    saveFile(r) {
      const data = JSON.stringify(r.body);
      const blob = new Blob([data], { type: 'text/plain' });
      const e = document.createEvent('MouseEvents');
      const a = document.createElement('a');
      a.download = `${this.$route.params.layerId}.geojson`;
      a.href = window.URL.createObjectURL(blob);
      a.dataset.downloadurl = ['text/json', a.download, a.href].join(':');
      e.initEvent(
        'click',
        true,
        false,
        window,
        0,
        0,
        0,
        0,
        0,
        false,
        false,
        false,
        false,
        0,
        null
      );
      a.dispatchEvent(e);
    },
    selectFeature(feature) {
      if (feature) {
        // eslint-disable-next-line no-underscore-dangle
        const fid = feature.properties_.id;
        this.selectFeatureById(fid);
        this.$refs['table-data'].getAttachments(fid); // get attachments for feature
        if ('table-data' in this.$refs) {
          this.$refs['table-data'].selectItem(
            this.items.find(item => item.id === fid)
          );
        }
      } else {
        if (this.$refs['table-data']) {
          this.$refs['table-data'].clearSelection();
        }
        this.currentFeature = undefined;
        this.indexActiveTab = 0;
        this.getLayerByName('featuresVectorSelection')
          .getSource()
          .clear();
      }
    },
    selectFeatureById(fid) {
      this.currentFeature = this.activeLayer.features.find(
        el => el.properties.id === fid
      );
      const feature = new GeoJSON().readFeature(this.currentFeature, {
        featureProjection: 'EPSG:3857',
        dataProjection: 'EPSG:4326'
      });
      this.getLayerByName('featuresVectorSelection')
        .getSource()
        .clear();
      this.getLayerByName('featuresVectorSelection')
        .getSource()
        .addFeature(feature);
      this.indexActiveTab = 1; // change tab in sidepanel
    },
    setLayerGeometry(type) {
      if (['dotted', 'dashed', 'line'].includes(type)) {
        this.layerGeometry = 'lineString';
      } else if (['point', 'square', 'triangle'].includes(type)) {
        this.layerGeometry = 'point';
      } else if (['polygon', includes(type)]) {
        this.layerGeometry = 'polygon';
      }
    },
    setLayersOrder(test) {
      const otherLayersOnMap = this.getLayerByName('otherLayers')
        .getLayers()
        .getArray();
      [...this.otherLayers].reverse().forEach((layer, index) => {
        otherLayersOnMap
          .find(l => l.get('name') === layer.name)
          .setZIndex(index);
      });
      this.map.updateSize();
    },
    setLayerVisibility(layerName) {
      if (this.getLayerByName(layerName).getVisible()) {
        this.getLayerByName(layerName).setVisible(false);
      } else {
        this.getLayerByName(layerName).setVisible(true);
      }
      this.map.updateSize();
    },
    showMeasure() {
      if (this.isMeasure) {
        this.isMeasure = false;
        this.measureType = false;
        this.getInteractionByName('drawMeasurement').setActive(false);
        this.getLayerByName('measurement')
          .getSource()
          .clear();

        this.measureTooltipElement.parentNode.removeChild(
          this.measureTooltipElement
        );
      } else {
        if (this.isMeasureShow) {
          this.isMeasureShow = false;
        } else {
          this.isMeasureShow = true;
        }
      }
    },
    startMeasure(type) {
      let drawLayer = this.getLayerByName('measurement');
      let drawInteraction = this.getInteractionByName('drawMeasurement');

      if (drawInteraction && this.measureType != type) {
        this.map.removeInteraction(drawInteraction);
        this.addMeasurementInteraction(drawLayer, type);
      } else {
        this.addMeasurementInteraction(drawLayer, type);
      }
      this.measureType = type;
      this.getInteractionByName('drawMeasurement').setActive(true);

      this.createMeasureTooltip();
      this.isMeasure = true;
      this.isMeasureShow = false;
    },
    styleFeatures(f, mvt = false, selecting = false) {
      const labelsToShow = [];
      this.labels.forEach(el => {
        labelsToShow.push(f.getProperties()[el]);
      });
      const featStyle = new Style({
        text: selecting
          ? null
          : new Text({
              text: labelsToShow.join(' '),
              fill: new Fill({ color: 'white' }),
              stroke: new Stroke({ color: 'black', width: 4 }),
              offsetY: -10
            })
      });
      if (this.layerType) {
        const stroke = new Stroke({
          color: selecting
            ? 'rgba(249, 237, 20, 0.8)'
            : `rgba(${this.layerStyle['stroke-color']})`,
          width: selecting ? 4 : `${this.layerStyle['stroke-width']}`
        });
        const fill = new Fill({
          color: selecting
            ? 'rgba(249, 237, 20, 0.5)'
            : `rgba(${this.layerStyle['fill-color']})`
        });
        if (this.layerType === 'point') {
          featStyle.setImage(
            new Circle({
              fill,
              stroke,
              radius: this.layerStyle.width
            })
          );
        } else if (
          this.layerType === 'square' ||
          this.layerType === 'triangle'
        ) {
          featStyle.setImage(
            new RegularShape({
              fill,
              stroke,
              points: this.layerType === 'square' ? 4 : 3,
              radius: this.layerStyle.width,
              angle: this.layerType === 'square' ? Math.PI / 4 : 0
            })
          );
        } else if (this.layerType === 'polygon' || this.layerType === 'line') {
          featStyle.setFill(fill);
          featStyle.setStroke(stroke);
        } else if (this.layerType === 'dashed' || this.layerType === 'dotted') {
          const lineDash = this.layerType === 'dashed' ? [10, 10] : [1, 10];
          stroke.setLineDash(lineDash);
          featStyle.setStroke(stroke);
        }
      } else {
        const attr = f.get(this.layerStyle.attribute);
        const filteredFeat = this.layerStyle.categories.find(
          el => el.value == attr
        );
        if (filteredFeat) {
          const stroke = new Stroke({
            color: selecting
              ? 'rgba(249, 237, 20, 0.5)'
              : `rgba(${filteredFeat['stroke-color']})`,
            width: selecting ? 4 : `${filteredFeat['stroke-width']}`
          });
          const fill = new Fill({
            color: selecting
              ? 'rgba(249, 237, 20, 0.5)'
              : `rgba(${filteredFeat['fill-color']})`
          });
          // TODO - add triangle/square/dashed/dotted
          if (filteredFeat.type === 'point') {
            featStyle.setImage(
              new Circle({
                fill,
                stroke,
                radius: filteredFeat.width
              })
            );
          } else {
            featStyle.setFill(fill);
            featStyle.setStroke(stroke);
          }
        } else {
          featStyle.setImage(
            new Circle({
              fill: new Fill({
                color: [250, 250, 250, 0.4]
              }),
              stroke: new Stroke({
                color: selecting
                  ? 'rgba(249, 237, 20, 0.5)'
                  : [51, 153, 204, 1],
                width: selecting ? 3 : 1
              }),
              radius: 2
            })
          );
        }
      }
      if (
        mvt == true &&
        this.editing == true &&
        f.get('id') == this.currentFeature.properties.id
      ) {
        return null;
      }
      return featStyle;
    },
    updateSearchCount(count) {
      this.searchCount = count;
    },
    updateSelectedRows(rows) {
      this.selectedRows = rows;
    },
    zoomToSelected() {
      const feature = new GeoJSON().readFeature(this.currentFeature, {
        featureProjection: 'EPSG:3857',
        dataProjection: 'EPSG:4326'
      });
      this.map.getView().fit(feature.getGeometry(), {
        maxZoom: 16,
        duration: 500
      });
    },
    async init() {
      proj4.defs(
        "EPSG:2180",
        "+proj=tmerc +lat_0=0 +lon_0=19 +k=0.9993 +x_0=500000 +y_0=-5300000 +ellps=GRS80 +units=m +no_defs +axis=enu"
      );
      register(proj4);
      this.$store.commit('setAttachmentsLayer', this.$route.params.layerId);
      this.getLayers();
      this.map = new Map({
        target: 'map',
        layers: [
          new TileLayer({
            name: 'OpenStreetMap',
            group: 'baselayers',
            source: new XYZ({
              url: 'https://{a-c}.tile.openstreetmap.org/{z}/{x}/{y}.png'
            })
          }),
          new LayerGroup({
            name: 'otherLayers'
          })
        ],
        view: new View({
          center: fromLonLat([this.mapCenter.lon, this.mapCenter.lat]),
          zoom: this.mapZoom,
          constrainResolution: true
        })
      });

      this.initOrtofoto();
      this.initOrtofotoDwa();
      this.getPermissions();
      await Promise.all([this.getUsers(), this.getSettings()]);

      await this.createStyle();

      this.map.addLayer(
        this.createMVTLayer(this.$route.params.layerId, 'features')
      );
      this.map.addLayer(
        new VectorLayer({
          name: 'featuresVector',
          visible: false,
          source: new VectorSource({}),
          style: feature => {
            const geometry = feature.getGeometry();
            let styles = [
              new Style({
                fill: new Fill({
                  color: 'rgba(255, 77, 77, 0.5)'
                }),
                stroke: new Stroke({
                  color: 'rgba(255, 77, 77, 0.5)',
                  width: 2
                }),
                image: new Circle({
                  radius: 5,
                  stroke: new Stroke({
                    color: 'rgba(255, 0, 0, 1)'
                  }),
                  fill: new Fill({
                    color: 'rgba(255, 77, 77, 1)'
                  })
                })
              })
            ];
            if (
              !(geometry instanceof Point) &&
              !(geometry instanceof MultiPoint)
            ) {
              styles.push(
                new Style({
                  image: new Circle({
                    radius: 5,
                    stroke: new Stroke({
                      color: 'rgba(255, 0, 0, 1)'
                    }),
                    fill: new Fill({
                      color: 'rgba(255, 77, 77, 1)'
                    })
                  }),
                  geometry: () => {
                    let coordinates = geometry.getCoordinates();
                    if (
                      geometry instanceof Polygon ||
                      geometry instanceof MultiLineString
                    ) {
                      coordinates = coordinates.flat();
                    } else if (geometry instanceof MultiPolygon) {
                      coordinates = coordinates.flat(2);
                    }
                    return new MultiPoint(coordinates);
                  }
                })
              );
            }
            return styles;
          }
        })
      );
      this.map.addLayer(
        new VectorLayer({
          name: 'buffer',
          visible: true,
          source: new VectorSource({}),
          style: new Style({
            stroke: new Stroke({
              color: 'rgba(37, 81, 122, 1)',
              width: 2
            }),
            fill: new Fill({
              color: 'rgba(37, 81, 122, 0.3)'
            })
          })
        })
      );
      this.map.addLayer(
        new VectorLayer({
          name: 'measurement',
          source: new VectorSource({}),
          style: feature => {
            const geometry = feature.getGeometry();
            const styles = [];
            if (geometry instanceof LineString) {
              geometry.forEachSegment((start, end) => {
                const line = new LineString([start, end]);
                styles.push(
                  new Style({
                    geometry: line,
                    stroke: new Stroke({
                      color: 'rgba(37, 81, 122, 1)',
                      width: 2
                    }),
                    fill: new Fill({
                      color: 'rgba(37, 81, 122, 0.3)'
                    }),
                    text: new Text({
                      text: this.formatLength(line),
                      font: '15px sans-serif',
                      fill: new Fill({ color: 'black' }),
                      placement: 'line',
                      stroke: new Stroke({
                        color: 'rgba(37, 81, 122, 0.3)',
                        width: 3
                      }),
                      offsetX: -20,
                      offsetY: 20
                    }),
                    image: new Circle({
                      radius: 5,
                      stroke: new Stroke({
                        color: '#25517a'
                      }),
                      fill: new Fill({
                        color: 'rgba(37, 81, 122, 0.5)'
                      })
                    })
                  })
                );
              });
            } else {
              styles.push(
                new Style({
                  stroke: new Stroke({
                    color: 'rgba(37, 81, 122, 1)',
                    width: 2
                  }),
                  fill: new Fill({
                    color: 'rgba(37, 81, 122, 0.3)'
                  })
                })
              );
            }
            return styles;
          }
        })
      );

      this.createSelectInteraction();

      const lDV = await this.$store.dispatch(
        'getLayerDictsValues',
        this.$route.params.layerId
      );
      if (lDV.status === 200) {
        this.dictValues = lDV.obj.data;
      } else {
        this.$alertify.error(this.$i18n.t('default.getDictsValuesError'));
      }
      const r = await this.$store.dispatch(
        'getLayer',
        this.$route.params.layerId
      );
      if (r.status === 200) {
        this.$store.commit('setActiveLayer', r.obj);
        Object.keys(r.obj.features[0].properties).forEach(el => {
          this.columns.push({
            key: el,
            name: el,
            sortable: true,
            filter: true
          });
        });
        r.obj.features.forEach(feat => {
          const tempItem = {};
          Object.entries(feat.properties).forEach(([k, v]) => {
            if (this.featureTypes[k] === 'timestamp without time zone') {
              tempItem[k] = moment(v).isValid()
                ? moment(v)
                    .locale('pl')
                    .format('L')
                : '';
            } else {
              tempItem[k] = v;
            }
          });
          this.items.push(tempItem);
        });
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
      this.searchCount = this.items.length;
    }
  },
  async mounted() {
    if (this.services.length < 1) {
      this.getServices();
    }
    if (this.$route.query.projectId) {
      this.getProject();
    } else {
      this.init();
    }
  },
  watch: {
    services() {
      this.addAdditionalLayers();
    },
    allOtherLayers() {
      this.addAdditionalLayers();
    }
  }
};
</script>

<style scoped>
.dragg-content {
  width: 100%;
  height: 100%;
}
.map-btn {
  position: relative;
  margin: 1px;
  padding: 0;
  color: white;
  font-size: 1.14em;
  font-weight: bold;
  text-decoration: none;
  text-align: center;
  height: 1.375em;
  width: 1.375em;
  line-height: 0.4em;
  background-color: rgba(0, 60, 136, 0.5);
  border: none;
  border-radius: 4px;
}
.map-btn:hover {
  background-color: rgba(0, 60, 136, 0.7);
}
.add-feature-tool {
  top: 59px;
}
.buffer-tool {
  top: 101px;
}
.distance-tool {
  top: 122px;
}
.map-tool-left {
  padding: 2px;
  z-index: 1;
  position: absolute;
  left: 0.5em;
}
.map-tool-right {
  padding: 2px;
  z-index: 1;
  position: absolute;
  right: 0.5em;
}
.measure-tool {
  top: 80px;
}
.rotation-tool {
  top: 28px;
}
.dropdown-menu {
  left: -110px;
}
.modal-new-feature .modal-body {
  height: 70vh;
  overflow-y: auto;
}
.list-group-item:not(.no-item):hover {
  cursor: pointer;
}
.popup {
  position: relative;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 4px;
  color: white;
  padding: 4px 8px;
  opacity: 0.7;
  white-space: nowrap;
}
.popup-measure {
  opacity: 1;
  font-weight: bold;
}
.layer-modal-body {
  height: calc(100% - 120px);
}
.layers-wrapper {
  overflow: auto;
  height: calc(100% - 40px);
}
.list__element--otherLayer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

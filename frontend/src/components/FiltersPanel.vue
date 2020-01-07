<template>
  <div class="filters-panel">
    <template v-if="!value || value.length == 0">
      <button class="btn btn-link" @click="toAddNew">
        <i class="fa fa-plus-circle" aria-hidden="true"/>
        Dodaj filtr
      </button>
    </template>
    <template v-else>
      <div>
        <div v-for="(filter, index) in value" :key="index">
          <SingleFilterPanel ref="filter"
            :value="filter"
            :columns="columns"
            @input="updateValue(filter, $event)"
            @to-delete="deleteFilter(filter, index)"
          />
          <form class="form-horizontal condition">
            <div class="form-group">
              <label class="control-label col-sm-4">Wybierz następny warunek:</label>
              <div class="col-sm-8">
                <select class="form-control" v-model="filter.condition"
                    :value="filter.condition"
                    @input="updateNext(filter, $event.target.value)">
                  <option value="" v-if="filter.condition == ''"/>
                  <option
                    v-for="operation in filterMergeOperations"
                    v-text="operation"
                    :value="operation"
                    :key="operation"/>
                </select>
              </div>
            </div>
          </form>
        </div>
      </div>
      <div>
        <span>Znajdź w tabeli obiekty z warstwy <b v-text="$root.layerName"/>
          które spełniają warunki:
          <template v-for="filter in value">
            <span :key="filter.column"
              v-if="filter.operation != '' && filter.column != '' && filter.value != ''">
            <span>atrybut
              <b v-text="fields[filter.column]"/> jest
              <span v-text="filterOperationsText[filter.operation]"/>&nbsp;
              <b v-text="filter.value"/>&nbsp;
              <span v-text="filterMergeOperationsText[filter.condition]"
                v-if="filter.condition != ''"/>&nbsp;
            </span>
            </span>
          </template>
        </span>
      </div>
    </template>
  </div>
</template>

<script>
import _ from 'lodash';
import SingleFilterPanel from '@/components/SingleFilterPanel.vue';

export default {
  name: 'filtersComponent',
  components: {
    SingleFilterPanel,
  },
  props: {
    columns: {
      type: Array,
      default: () => [],
    },
    value: {
      type: Array,
      required: true,
    },
  },
  data: () => ({
    filterMergeOperations: ['AND', 'OR'],
    filterOperationsText: {
      '=': 'równy',
      '!=': 'nie równy',
      startwith: 'zaczyna się',
      '!startwith': 'nie zaczyna się',
      '!endwith': 'nie kończy się',
      endwith: 'kończy się',
      contains: 'zawiera',
      '!contains': 'nie zawiera',
    },
    filterMergeOperationsText: {
      AND: 'i',
      OR: 'lub',
    },
  }),
  methods: {
    toAddNew() {
      this.value.push({
        column: '',
        operation: '=',
        value: '',
        condition: '',
      });
      this.emitUpdateValue();
    },
    deleteFilter(filter, index) {
      this.$delete(this.value, index);
      if (index === this.value.length) {
        this.value[this.value.length - 1].condition = '';
      }
      this.emitUpdateValue();
    },

    updateNext(filter, condition) {
      const addNew = filter.condition === '';
      // eslint-disable-next-line no-param-reassign
      filter.condition = condition;
      if (addNew) {
        this.toAddNew();
      } else {
        this.emitUpdateValue();
      }
    },
    updateValue(filter, $event) {
      _.each($event, (v, k) => {
        // eslint-disable-next-line no-param-reassign
        filter[k] = v;
      });
      this.emitUpdateValue();
    },
    emitUpdateValue() {
      this.$emit('input', this.value);
    },
  },
  created() {
    this.fields = _(this.$root.fields).keyBy(field => field.key)
      .mapValues(field => field.name).value();
  },
};
</script>

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
              <label class="control-label col-sm-4">Następny warunek:</label>
              <div class="col-sm-8">
                <select class="form-control" v-model="filter.condition"
                    :value="filter.condition"
                    @input="updateNext(filter, $event.target.value)">
                  <option value="" v-if="filter.condition == ''"/>
                  <option
                    v-for="(operation, idx) in filterMergeOperations"
                    v-text="operation"
                    :value="operation"
                    :key="operation + idx"/>
                </select>
              </div>
            </div>
          </form>
        </div>
      </div>
      <div>
        <span>Znajdź w tabeli obiekty z warstwy <b v-text="$route.params.layerName"/>
          które spełniają warunki:
          <ul>
          <template v-for="(filter, idx) in value">
            <span :key="filter.column+idx"
              v-if="filter.operation != '' && filter.column != '' && filter.value != ''">
            <li>atrybut
              <b v-text="filter.column"/>&nbsp;
              <span v-text="filterOperationsText[filter.operation]"/>&nbsp;
              <b v-text="filter.value"/>&nbsp;
              <span v-text="filterMergeOperationsText[filter.condition]"
                v-if="filter.condition != ''"/>&nbsp;
            </li>
            </span>
          </template>
          </ul>
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
      '=': 'równa się',
      '!=': 'nie równa się',
      startwith: 'zaczyna się od',
      '!startwith': 'nie zaczyna się od',
      '!endwith': 'nie kończy się na',
      endwith: 'kończy się na',
      contains: 'zawiera',
      '!contains': 'nie zawiera',
      '<': 'jest mniejszy niż',
      '=<': 'jest mniejszy lub równy',
      '=>': 'jest większy lub równy',
      '>': 'jest większy niż',
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

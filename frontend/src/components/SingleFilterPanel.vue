<template>
  <div class="filter-panel">
    <form class="form-horizontal">
      <div class="form-group">
        <label class="control-label col-sm-4">Wybierz kolumne filtra:</label>
        <div class="col-sm-8">
          <div class="input-group">
            <select
              class="form-control"
              :value="value.column"
              @input="updateValue('column', $event.target.value)"
            >
              <option
                v-for="(field, idx) in fields"
                :key="field + idx"
                :value="field"
                v-text="field"
              />
            </select>
            <span class="input-group-btn">
              <button class="btn btn-danger" type="button" title="Usuń filtr" @click="deleteFilter">
                <i class="fa fa-times" />
              </button>
            </span>
          </div>
        </div>
      </div>
      <div v-if="value.column != ''" class="form-group">
        <label class="control-label col-sm-4">Wartość:</label>
        <div class="col-sm-8">
          <div class="input-group">
            <div class="input-group-btn">
              <button
                type="button"
                class="btn btn-default dropdown-toggle"
                data-toggle="dropdown"
                aria-haspopup="true"
                aria-expanded="false"
              >
                <span
                  v-if="featureTypes[value.column] === 'character varying'"
                  style="position: relative; left: -5px;"
                  v-text="value.operation == '' ? 'Operacja' : filterMap[value.operation]"
                />
                <span
                  v-else
                  style="position: relative; left: -5px;"
                  v-text="value.operation == '' ? 'Operacja' : value.operation"
                />
                <span class="caret" />
              </button>
              <ul class="dropdown-menu dropdown-menu-right">
                <li v-for="(operation, idx) in getOperations(value.column)" :key="operation + idx">
                  <a
                    v-if="featureTypes[value.column] === 'character varying'"
                    href="#"
                    @click="updateValue('operation', operation)"
                    v-text="filterMap[operation]"
                  />
                  <a
                    v-else
                    href="#"
                    @click="updateValue('operation', operation)"
                    v-text="operation"
                  />
                </li>
              </ul>
            </div>
            <input
              type="text"
              class="form-control"
              :value="value.value"
              placeholder="Wpisz wartość"
              @input="updateValue('value', $event.target.value)"
            />
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import _ from 'lodash';

export default {
  props: {
    columns: {
      type: Array,
      default: () => []
    },
    value: {
      type: Object,
      required: true
    }
  },
  data: () => ({
    filterOperations: {
      'character varying': [
        '=',
        '!=',
        'startwith',
        '!startwith',
        '!endwith',
        'endwith',
        'contains',
        '!contains'
      ],
      integer: ['=', '<', '=<', '=>', '>', '!='],
      real: ['=', '<', '=<', '=>', '>', '!='],
      'timestamp without time zone': ['=', '<', '=<', '=>', '>', '!=']
    },
    filterMap: {
      '=': 'Równa się',
      '!=': 'Nie równa się',
      startwith: 'Zaczyna się od',
      '!startwith': 'Nie zaczyna się od',
      endwith: 'Kończy się na',
      '!endwith': 'Nie kończy się na',
      contains: 'Zawiera',
      '!contains': 'Nie zawiera'
    }
  }),
  computed: {
    featureTypes() {
      return this.$store.getters.getCurrentFeaturesTypes;
    },
    fields: {
      get() {
        return this.columns.map(el => el.name).filter(n => n);
      },
      set(newFields) {
        return newFields;
      }
    }
  },
  created() {
    this.fields = this.$root.fields;
  },
  methods: {
    deleteFilter() {
      this.$emit('to-delete');
    },

    getOperations(column) {
      const field = Object.entries(this.featureTypes).find(key => key[0] === column);
      return this.filterOperations[field[1]];
    },

    updateValue(type, _new) {
      const self = this;
      const data = {
        column: self.value.column,
        operation: self.value.operation,
        value: self.value.value
      };
      data[type] = _new;

      if (type === 'column') {
        const operations = self.getOperations(data.column);
        if (!_.includes(operations, data.operation)) {
          // eslint-disable-next-line prefer-destructuring
          data.operation = operations[0];
        }
      }

      self.$emit('input', data);
    }
  }
};
</script>

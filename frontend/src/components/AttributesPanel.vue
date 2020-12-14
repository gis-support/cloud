<template>
  <div class="attr-wrapper">
    <div v-for="(value, key) in fields.properties" :key="key">
      <label>{{ key }}:</label>
      <br />
      <template v-if="!editing">
        <span v-if="value || value === 0" style="word-wrap: break-word">{{
          value | formatDate(featureTypes[key])
        }}</span>
        <span v-else style="color: lightgrey">{{ $i18n.t('default.noData') }}</span>
      </template>
      <template v-else>
        <input
          v-if="key === 'id' || key === '__attachments'"
          v-model="attributes.properties[key]"
          class="form-control"
          type="text"
          disabled
        />
        <span v-else>
          <InputNumber
            v-if="featureTypes[key] === 'integer' || featureTypes[key] === 'real'"
            v-model.number="attributes.properties[key]"
            :type="featureTypes[key]"
          />
          <input
            v-else-if="featureTypes[key] === 'character varying'"
            v-model="attributes.properties[key]"
            class="form-control col-sm-7"
            type="text"
          />
          <Datepicker
            v-else-if="featureTypes[key] === 'timestamp without time zone'"
            v-model="attributes.properties[key]"
            format="dd-MM-yyyy"
          ></Datepicker>
          <select
            v-else-if="featureTypes[key] === 'dict'"
            v-model="attributes.properties[key]"
            class="form-control"
          >
            <option :value="null"></option>
            <option
              v-for="(dV, idx) in dictValues.find(d => d.column_name === key).values"
              :key="idx"
              :value="dV"
              v-text="dV"
            />
          </select>
          <!--
          <input
            class="form-control col-sm-7"
            v-model="attributes.properties[key]"
            v-else-if="featureTypes[key] === 'timestamp without time zone'"
            type="datetime-local"
          />
          -->
        </span>
      </template>
      <hr />
    </div>
  </div>
</template>

<script>
import Datepicker from 'vuejs-datepicker';
import InputNumber from '@/components/InputNumber';
import moment from 'moment';

export default {
  filters: {
    formatDate(value, type) {
      if (type == 'timestamp without time zone') {
        return value
          ? moment(value)
              .locale('pl')
              .format('L')
          : null;
      }
      return value;
    }
  },
  components: { Datepicker, InputNumber },
  props: {
    dictValues: {
      type: Array,
      required: true
    },
    editing: {
      type: Boolean,
      required: true
    },
    fields: {
      type: Object,
      required: true
    }
  },
  computed: {
    attributes() {
      return this.fields;
    },
    featureTypes() {
      return this.$store.getters.getCurrentFeaturesTypes;
    }
  }
};
</script>

<style scoped>
.attr-wrapper {
  max-height: calc(100% - 120px);
}
</style>

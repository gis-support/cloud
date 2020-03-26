<template>
  <div class="attr-wrapper">
    <div
      v-for="(value, key) in fields.properties"
      :key="key"
    >
      <label>{{ key }}:</label>
      <br />
      <template v-if="!editing">
        <span v-if="value">{{ value }}</span>
        <span
          v-else
          style="color: lightgrey"
        >{{ $i18n.t('default.noData') }}</span>
      </template>
      <template v-else>
        <input
          class="form-control"
          type="text"
          v-model="attributes.properties[key]"
          disabled
          v-if="key === 'id'"
        />
        <span v-else>
          <input
            class="form-control col-sm-7"
            v-model="attributes.properties[key]"
            v-if="featureTypes[key] === 'real' || featureTypes[key] === 'integer'"
            @keypress="isNumber($event)"
            type="number"
          />
          <input
            class="form-control col-sm-7"
            v-model="attributes.properties[key]"
            v-else-if="featureTypes[key] === 'character varying'"
            type="text"
          />
          <input
            class="form-control col-sm-7"
            v-model="attributes.properties[key]"
            v-else-if="featureTypes[key] === 'timestamp without time zone'"
            type="datetime-local"
          />
        </span>
      </template>
      <hr />
    </div>
  </div>
</template>

<script>
export default {
  props: {
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
  },
  methods: {
    isNumber(evt) {
      const e = evt || window.event;
      const charCode = e.which ? e.which : e.keyCode;
      if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        e.preventDefault();
        return false;
      }
      return true;
    }
  }
};
</script>

<style scoped>
.attr-wrapper {
  max-height: calc(100% - 120px);
}
</style>

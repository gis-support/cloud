<template>
  <div class="attr-wrapper">
    <div v-for="(value, key) in fields.properties" :key="key">
      <label>{{key}}:</label>
      <br/>
      <template v-if="!editing">
        <span v-if="value">{{ value }}</span>
        <span v-else style="color: lightgrey">Brak danych</span>
      </template>
      <template v-else>
        <input
          class="form-control"
          type="text"
          v-model="attributes.properties[key]"
          disabled
          v-if="key === 'id'"/>
        <input class="form-control" type="text" v-model="attributes.properties[key]" v-else/>
      </template>
      <hr/>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    editing: {
      type: Boolean,
      required: true,
    },
    fields: {
      type: Object,
      required: true,
    },
  },
  computed: {
    attributes() {
      return this.fields;
    },
  },
};
</script>

<style scoped>
.attr-wrapper {
  max-height: calc(100% - 120px);
}
</style>

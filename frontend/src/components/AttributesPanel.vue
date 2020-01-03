<template>
  <div class="attr-wrapper">
    <div v-for="(value, key) in fields.properties" :key="key">
      <label>{{key}}:</label>
      <br/>
      <span v-if="value">{{ value }}</span>
      <span v-else style="color: lightgrey">Brak danych</span>
      <hr/>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    fields: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style scoped>
.attr-wrapper {
  max-height: calc(100% - 120px);
}
</style>

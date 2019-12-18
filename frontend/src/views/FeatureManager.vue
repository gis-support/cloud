<template>
  <div class="content">
    <!-- {{ $route.params.layerId }} -->
    <FeatureManagerTable
      :items="items"
      :columns="columns"
    />

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
          ></virtual-table> -->
  </div>
</template>

<script>
import FeatureManagerTable from '@/components/FeatureManagerTable.vue';

export default {
  components: {
    FeatureManagerTable,
  },
  data: () => ({
    columns: [],
    items: [],
  }),
  methods: {
  },
  async mounted() {
    const r = await this.$store.dispatch('getLayer', this.$route.params.layerId);
    if (r.status === 200) {
      r.obj.features.forEach((feat) => {
        Object.keys(feat.properties).forEach((el) => {
          this.columns.push({
            key: el, name: el, sortable: true, filter: true,
          });
        });
        const tempItem = {};
        Object.entries(feat.properties).forEach(([k, v]) => {
          tempItem[k] = v;
        });
        this.items.push(tempItem);
        console.log(this.items, this.columns);
      });
    } else {
      this.$alertify.error(this.$i18n.t('default.error'));
    }
  },
};
</script>

<style scoped>
</style>

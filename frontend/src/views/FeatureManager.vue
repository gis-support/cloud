<template>
  <div class="content">
    <!-- {{ $route.params.layerId }} -->
    <FeatureManagerTable
      v-if="items.length > 0"
      :items="items"
      :columns="columns"
    />
    <div class="loading-overlay pt-10 pb-10" style="text-align: center;" v-else>
      <div class="loading-indicator mb-10"><h4>{{$i18n.t('default.loading')}}</h4>
      <i class="fa fa-lg fa-spin fa-spinner"></i></div>
    </div>

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
    columns: [{
      head: true, sortable: true, filter: true,
    }],
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
      });
    } else {
      this.$alertify.error(this.$i18n.t('default.error'));
    }
  },
};
</script>

<style scoped>
</style>

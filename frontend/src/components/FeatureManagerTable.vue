<template>
  <div class="table-content">
    <div>


      <div class="loading-overlay pt-10 pb-10" style="text-align: center;" v-if="items.length < 1">
        <div class="loading-indicator mb-10"><h4>{{$i18n.t('default.loading')}}</h4>
        <i class="fa fa-lg fa-spin fa-spinner"></i></div>
      </div>
      <div class="vscroll" v-else>
        <div class="table-data table-responsive">
          <table class="table table-bordered table-hover table-striped">
            <thead>
              <tr>
                <template v-for="(column, i) in columns">
                  <th
                    v-if="column.head"
                    class="first"
                    :key="i"
                  >#</th>
                  <th
                    v-else-if="!column.head"
                    :key="i"
                  >
                    <div>
                      <span v-text="column.name" />
                      <span
                        v-show="!editing"
                        :class="{
                        'filter' : column.filter,
                        'filtered' : isFiltredColumn(column),
                        }"
                      />
                      <span
                        v-show="!editing"
                        :class="{
                        'sorting' : column.sortable &&
                          (!sortedColumn || sortedColumn != column.key),
                        'sorting_asc' : sortedColumn == column.key && sortedColumnType == 'asc',
                        'sorting_desc' : sortedColumn == column.key && sortedColumnType == 'desc',
                        }"
                        @click.capture="column.sortable ? sort($event, column.key) : false"
                      />
                    </div>
                  </th>
                </template>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(item, index) in windowItems"
                :key="index"
              >
                <template v-for="(column, idx2) in columns">
                  <th
                    v-if="column.head"
                    scope="row"
                    v-text="indexFirstItem + index + 1"
                    :key="idx2 + 'col'"
                  />
                  <td
                    v-else
                    v-text="item[column.key]"
                    :key="idx2 + 'item'"
                    :class="{'active-cell' : selectedIndex == indexFirstItem + index}"
                    @click="selectItemIndex(indexFirstItem + index, item)"
                  />
                </template>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="table-scroll-bar" :style="{top: `${itemHeight}px`}"
          v-show="filteredItems.length > windowItems.length">
          <div :style="{height : `${filteredItems.length * (itemHeight)}px`}" style="width: 1px;">

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import ValueFilterMap from '@/assets/js/value-filters';
import recomputeMixin from '@/components/mixins/recomputeMixin';

export default {
  mixins: [recomputeMixin],
  props: {
    items: {
      type: Array,
      required: true,
    },
    columns: {
      type: Array,
      default: () => [],
    },
    search: {
      type: String,
      default: '',
    },
    columnFilters: {
      type: Array,
      default: () => [],
    },
    editing: {
      type: Boolean,
      default: true,
    },
    layId: {
      type: String,
    },
  },
  data: () => ({
    arenaHeight: 0,
    currentFeatureId: undefined,
    maxItems: 1,
    indexFirstItem: 0,
    itemHeight: 0,
    sortedColumn: false,
    sortedColumnType: 'asc',

    selectedIndex: -1,
  }),
  computed: {
    searchedItems() {
      const self = this;
      if (!self.search) {
        return self.items;
      }

      return self.wyszukaj(self.items, self.search);
    },
    filteredItems() {
      const self = this;

      if (_.isEmpty(self.columnFilters)) {
        return self.searchedItems;
      }
      return self.filtrowanie(self.searchedItems);
    },
    sortedItems() {
      const self = this;

      if (!self.sortedColumn) {
        return self.filteredItems;
      }

      return _.orderBy(self.filteredItems, [self.sortedColumn], [self.sortedColumnType]);
    },
    windowItems() {
      const self = this;
      if (self.maxItems === 0) {
        return [];
      }
      return _.slice(self.sortedItems, self.indexFirstItem, self.indexFirstItem + self.maxItems);
    },

    filteredColumns() {
      const self = this;

      if (_.isEmpty(self.columnFilters)) {
        return {};
      }

      return _(self.columnFilters).map(filter => filter.column).uniq().keyBy()
        .mapValues(() => true)
        .value();
    },
    selectedItem() {
      return this.selectedIndex === -1 ? null : this.sortedItems[this.selectedIndex];
    },
    featureAttachments() {
      return this.$store.getters.getFeatureAttachments;
    },
  },
  watch: {
    searchedItems() {
      // this._computedWatchers.filteredItems.update();
      this.$recompute('filteredItems');
    },
    filteredItems(_new) {
      this.$emit('update-filtred-count', _new.length);
      // this._computedWatchers.sortedItems.update();
      this.$recompute('sortedItems');
    },
    sortedItems() {
      // this._computedWatchers.windowItems.update();
      this.$recompute('windowItems');
    },
    items() {
      this.scrollEl.scrollTop = 0;
      this.indexFirstItem = 0;
      // this._computedWatchers.searchedItems.update();
      this.$recompute('searchedItems');
    },
    search() {
      // this._computedWatchers.searchedItems.update();
      this.$recompute('searchedItems');
    },

    columnFilters() {
      // this._computedWatchers.filteredColumns.update();
      // this._computedWatchers.filteredItems.update();
      this.$recompute('filteredItems');
    },
  },
  methods: {
    async getAttachments(prop) {
      const fid = prop.id;
      if (!this.featureAttachments[this.layId]) {
        const payload = { lid: this.layId, fid };
        const r = await this.$store.dispatch('getFeatureAttachments', payload);
        if (r.status === 200) {
          this.$store.commit('setFeatureAttachments', { lid: this.layId, fid, attachments: r.body.attachments });
        } else {
          this.$alertify.error(this.$i18n.t('featureManager.errorAttachmentsFetch'));
        }
      }
    },
    filtrowanie(items) {
      const self = this;

      if (!ValueFilterMap) {
        return items;
      }

      const filtersGroup = [];
      let condition = '';
      _.each(self.columnFilters, (filter) => {
        if (filtersGroup.length === 0) {
          filtersGroup.push([filter]);
        } else if (condition === 'OR') {
          filtersGroup.push([filter]);
        } else if (condition === 'AND') {
          filtersGroup[filtersGroup.length - 1].push(filter);
        }
        ({ condition } = filter);
      });

      const result = [];
      _.each(filtersGroup, (filters) => {
        let items2 = items;
        _.each(filters, (filter) => {
          items2 = _.filter(
            items2, item => ValueFilterMap[filter.operation](filter.value)
              .isFiltered(item[filter.column]),
          );
        });
        result.push(items2);
      });
      return _.concat(...result);
    },
    updateSelectedItem(emit) {
      // this._computedWatchers.selectedItem.update();
      this.$recompute('selectedItem');
      if (emit && this.selectedIndex !== -1) {
        this.$emit('update-select-item', this.selectedItem);
      }
    },
    selectFeatureFromId(id) {
      this.currentFeatureId = id;
      this.$emit('selectFeatureById', id);
    },
    selectItemIndex(index, prop) {
      if (this.editing) {
        return;
      }
      this.selectedIndex = index;
      this.updateSelectedItem(true);
      this.selectFeatureFromId(prop.id, true);
      this.getAttachments(prop);
    },
    clearSelection() {
      this.selectedIndex = -1;
      this.updateSelectedItem();
    },
    selectItem(item) {
      if (!item) {
        this.$alertify.warning('Dany element nie znajduje się w cześci załadowanych danych z serwera');
        return;
      }
      this.selectedIndex = _.findIndex(this.sortedItems, o => o === item);
      this.updateSelectedItem();
      if (this.selectedIndex !== -1) {
        this.scrollTo(this.selectedIndex);
      }
    },
    scrollTo(index) {
      const self = this;
      if (index < 0 || index >= self.sortedItems.length) {
        return;
      }

      let indexScroll = index;
      const y = self.selectedIndex + self.maxItems - (self.sortedItems.length - 1);
      if (y > 0) {
        indexScroll = index - y;
      }

      self.scrollEl.scrollTop = indexScroll * self.itemHeight;
    },
    wyszukaj(items, wartosc) {
      return _.filter(items, item => _.some(
        item, value => value && value.toString().indexOf(wartosc) !== -1,
      ));
    },

    initVirtualTable() {
      const self = this;

      // self._computedWatchers.sortedItems.update();
      this.$recompute('sortedItems');

      const tableEl = self.$el.querySelector('.table-data');
      self.scrollEl = self.$el.querySelector('.table-scroll-bar');
      const theadTrhEl = tableEl.querySelector('thead tr');

      self.itemHeight = theadTrhEl.offsetHeight - 1;
      self.arenaHeight = tableEl.offsetHeight - self.itemHeight;
      self.maxItems = Math.floor((self.arenaHeight) / self.itemHeight);
      // self._computedWatchers.windowItems.update();
      this.$recompute('windowItems');

      new ResizeObserver(() => {
        self.arenaHeight = tableEl.offsetHeight - self.itemHeight;

        const newMaxItems = Math.floor((self.arenaHeight) / self.itemHeight);

        if (newMaxItems !== self.maxItems) {
          self.maxItems = newMaxItems;
          // self._computedWatchers.windowItems.update();
          this.$recompute('windowItems');
        }
      }).observe(tableEl);

      function checkScrollPosition() {
        self.indexFirstItem = Math.floor(self.scrollEl.scrollTop / self.itemHeight + 0.6);
        // self._computedWatchers.windowItems.update();
        self.$recompute('windowItems');
      }
      self.scrollEl.addEventListener('scroll', checkScrollPosition);

      function checkScrollPosition2(e) {
        if (!e.shiftKey) {
          self.scrollEl.scrollTop -= e.wheelDeltaY || (e.deltaY * -40);
        }
      }
      tableEl.addEventListener('wheel', checkScrollPosition2);
    },

    sort($event, kolumn) {
      const self = this;
      if (self.sortedColumn === kolumn) {
        self.sortedColumnType = self.sortedColumnType === 'asc' ? 'desc' : 'asc';
      } else {
        self.sortedColumn = kolumn;
        self.sortedColumnType = 'asc';
      }
      // self._computedWatchers.sortedItems.update();
      this.$recompute('sortedItems');
    },
    isFiltredColumn(column) {
      return column.key in this.filteredColumns && this.filteredColumns[column.key];
    },

    updateColumnFilters() {
      // this._computedWatchers.filteredColumns.update();
      this.$recompute('filteredColumns');
      // this._computedWatchers.filteredItems.update();
      this.$recompute('filteredItems');
    },
  },
  beforeCreate() {},
  created() {
    this.$root.$on('update-column-filters', this.updateColumnFilters);
  },
  mounted() {
    const self = this;
    self.initVirtualTable();
  },
  updated() {},
  activated() {},
  deactivated() {},
  beforeDestroy() {
    this.$root.$off('update-column-filters', this.updateColumnFilters);
  },
  destroyed() {},
};
</script>

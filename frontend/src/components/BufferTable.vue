<template>
  <div class="table-content">
    <div>
      <div class="vscroll">
        <div class="table-data table-responsive" style="margin-right: 30px">
          <table class="table table-bordered table-hover table-striped" style="margin-right: 20px">
            <thead>
              <tr>
                <template v-for="(column, i) in columns">
                  <th v-if="column.head" :key="i" class="first" :style="{ 'min-width': '50px' }">
                    #
                  </th>
                  <th
                    v-else-if="!column.head"
                    :key="i"
                    :style="{
                      'min-width': columnsLengths[column.name] + 'px',
                      'max-width': columnsLengths[column.name] + 'px'
                    }"
                  >
                    <div>
                      <span v-text="column.name" />
                      <span
                        :class="{
                          sorting: column.sortable && (!sortedColumn || sortedColumn != column.key),
                          sorting_asc: sortedColumn == column.key && sortedColumnType == 'asc',
                          sorting_desc: sortedColumn == column.key && sortedColumnType == 'desc'
                        }"
                        @click.capture="column.sortable ? sort($event, column.key) : false"
                      />
                    </div>
                  </th>
                </template>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in windowItems" :key="index">
                <template v-for="(column, idx2) in columns">
                  <th
                    v-if="column.head"
                    :key="idx2 + 'col'"
                    scope="row"
                    v-text="indexFirstItem + index + 1"
                  />
                  <td
                    v-else
                    :key="idx2 + 'item'"
                    :class="{
                      'overflow-title': columnsLengths[column.name] >= 750
                    }"
                    :style="{
                      'min-width': columnsLengths[column.name] + 'px',
                      'max-width': columnsLengths[column.name] + 'px'
                    }"
                    :title="
                      item[column.key] != null && item[column.key].toString().length >= 100
                        ? item[column.key]
                        : false
                    "
                    v-text="item[column.key]"
                  />
                </template>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="table-scroll-bar-modal" :style="{ top: `${itemHeight}px` }">
          <div :style="{ height: `${items.length * itemHeight}px` }" style="width: 1px" />
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import recomputeMixin from '@/components/mixins/recomputeMixin';
import _ from 'lodash';

export default {
  mixins: [recomputeMixin],
  props: {
    items: {
      type: Array,
      required: true
    },
    columns: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      arenaHeight: 0,
      columnsLengths: {},
      maxItems: 0,
      indexFirstItem: 0,
      itemHeight: 0,
      sortedColumn: false,
      sortedColumnType: 'asc'
    };
  },
  computed: {
    sortedItems() {
      const self = this;

      if (!self.sortedColumn) {
        return self.items;
      }

      return _.orderBy(
        self.items,
        [
          item => {
            if (typeof item[self.sortedColumn] === 'string') {
              const value = _.deburr(item[self.sortedColumn]);
              return value ? value.toLowerCase() : '';
            }
            return item[self.sortedColumn];
          }
        ],
        [self.sortedColumnType]
      );
    },
    windowItems() {
      const self = this;
      if (self.maxItems === 0) {
        return [];
      }
      return _.slice(self.sortedItems, self.indexFirstItem, self.indexFirstItem + self.maxItems);
    }
  },
  watch: {
    items() {
      this.scrollEl.scrollTop = 0;
      this.indexFirstItem = 0;
      this.$recompute('windowItems');
    },
    sortedItems() {
      this.$recompute('windowItems');
    }
  },
  mounted() {
    for (let column of this.columns) {
      if (!column.head) {
        this.columnsLengths[column.name] = column.name.length * 7.5 + 30;
      }
    }
    for (let item of this.items) {
      for (let column in item) {
        if (item[column]) {
          if (item[column].toString().length * 7.5 > this.columnsLengths[column]) {
            this.columnsLengths[column] =
              item[column].toString().length * 7.5 >= 750
                ? 750
                : item[column].toString().length * 7.5;
          }
        }
      }
    }
    const self = this;
    self.initVirtualTable();
  },
  methods: {
    initVirtualTable() {
      const self = this;

      this.$recompute('sortedItems');

      const tableEl = self.$el.querySelector('.table-data');
      self.scrollEl = self.$el.querySelector('.table-scroll-bar-modal');
      const theadTrhEl = tableEl.querySelector('thead tr');

      self.itemHeight = theadTrhEl.offsetHeight - 1;
      self.arenaHeight = tableEl.offsetHeight - self.itemHeight;
      self.maxItems = Math.floor(self.arenaHeight / self.itemHeight);
      this.$recompute('windowItems');

      new ResizeObserver(() => {
        self.arenaHeight = tableEl.offsetHeight - self.itemHeight;

        const newMaxItems = Math.floor(self.arenaHeight / self.itemHeight);

        if (newMaxItems !== self.maxItems) {
          self.maxItems = newMaxItems;
          this.$recompute('windowItems');
        }
      }).observe(tableEl);

      function checkScrollPosition() {
        self.indexFirstItem = Math.floor(self.scrollEl.scrollTop / self.itemHeight + 0.78);
        self.$recompute('windowItems');
      }
      self.scrollEl.addEventListener('scroll', checkScrollPosition);

      function checkScrollPosition2(e) {
        if (!e.shiftKey) {
          self.scrollEl.scrollTop -= e.wheelDeltaY || e.deltaY * -40;
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
      this.$recompute('sortedItems');
    }
  }
};
</script>

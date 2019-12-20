/* eslint-disable */
import Vue from 'vue';

export default {
  created() {
    const recomputed = Object.create(null);
    const watchers = this._computedWatchers; // Warning: Vue internal

    if (!watchers) return;

    for (const key in watchers) this.makeRecomputable(watchers[key], key, recomputed);

    this.$recompute = key => recomputed[key] = !recomputed[key];
    Vue.observable(recomputed);
  },
  methods: {
    makeRecomputable(watcher, key, recomputed) {
      const original = watcher.getter;
      // eslint-disable-next-line no-param-reassign
      recomputed[key] = true;
      // eslint-disable-next-line no-param-reassign
      watcher.getter = vm => (recomputed[key], original.call(vm, vm));
    },
  },
};

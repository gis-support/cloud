<template>
  <div class="colorPicker wrapper">
    <div class="dot__wrapper text-center">
      <span
        class="dot"
        :style="{backgroundColor: computedValue}"
        @click.stop="open"
      ></span>
    </div>
    <chrome-picker
      v-click-outside="hide"
      class="picker"
      v-model="computedValue"
      v-if="isPickerVisible"
    />
  </div>
</template>

<script>
import { Chrome } from 'vue-color';
export default {
  props: {
    value: {
      required: true
    }
  },
  components: {
    'chrome-picker': Chrome
  },
  directives: {
    'click-outside': {
      bind: function(el, binding, vnode) {
        el.clickOutsideEvent = function(event) {
          // here I check that click was outside the el and his childrens
          if (!(el == event.target || el.contains(event.target))) {
            // and if it did, call method provided in attribute value
            vnode.context[binding.expression](event);
          }
        };
        document.body.addEventListener('click', el.clickOutsideEvent);
      },
      unbind: function(el) {
        document.body.removeEventListener('click', el.clickOutsideEvent);
      }
    }
  },
  data: () => ({
    colors: '',
    isPickerVisible: false
  }),
  computed: {
    computedValue: {
      get() {
        if (!this.value) {
          return `rgba(0,0,0,1)`;
        }
        return this.value;
      },
      set(nV) {
        const { r, g, b, a } = nV.rgba;
        this.$emit('input', `rgba(${r},${g},${b},${a})`);
      }
    }
  },
  methods: {
    open() {
      this.isPickerVisible = true;
    },
    hide() {
      this.isPickerVisible = false;
    }
  }
};
</script>

<style scoped>
.dot {
  height: 25px;
  width: 25px;
  border-radius: 50%;
  display: inline-block;
  cursor: pointer;
  border: 1px solid rgb(158, 158, 158);
}
.picker {
  z-index: 10;
  position: absolute;
}
</style>
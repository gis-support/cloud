<template>
  <input
    class="form-control col-sm-7"
    :value="value"
    @change="checkNumber($event)"
    @input="$emit('input', $event.target.value)"
    @keydown="isNumber($event)"
    @paste.prevent
  />
</template>
<script>
export default {
  props: {
    type: {
      required: true,
      type: String
    },
    value: {
      required: true
    }
  },
  methods: {
    checkNumber(e) {
      //Sprawdzenie czy użytkownik nie zostawił w inpucie kropki na końcu albo samego minusa
      const inputValue = e.target.value;
      if (inputValue.slice(-1) === '-') {
        e.target.value = inputValue + '1';
        this.$emit('input', parseInt(inputValue + '1'));
      }
      if (this.type === 'real' && inputValue.slice(-1) === '.') {
        e.target.value = inputValue.slice(0, -1);
        this.$emit('input', parseInt(inputValue.slice(0, -1)));
      }
    },
    isNumber(e) {
      //Zdefiniowanie zmiennych i pobranie wartości inputa do przeprowadzenia walidacji
      const inputValue = e.target.value.toString();
      const selectionStart = e.target.selectionStart;
      const selectionEnd = e.target.selectionEnd;
      const { keyCode, key } = e;
      const allowedKeyCodes = [8, 9, 37, 39];

      //Dodanie dopuszczalnych znaków w zależności od typu i wartości
      if (
        selectionStart === 0 &&
        (selectionEnd > 0 || !inputValue.includes('-'))
      ) {
        allowedKeyCodes.push(173);
      }
      if (this.type === 'real' && !inputValue.includes('.')) {
        if (inputValue.includes('-') && selectionStart > 1) {
          allowedKeyCodes.push(190);
        } else if (!inputValue.includes('-') && selectionStart > 0) {
          allowedKeyCodes.push(190);
        }
      }

      //Obsłużenie wpisanego znaku
      if (allowedKeyCodes.includes(keyCode)) {
        return;
      }
      if (!/[0-9]/.test(key)) {
        e.preventDefault();
      }
    }
  }
};
</script>
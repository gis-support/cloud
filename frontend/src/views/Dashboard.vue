<template>
  <div class="dashboard container align-center">
    <div class="col-sm-12 pl-0 pr-0 container__border--bottom container__border--grey section">
      <h2 class="flex-center mb-0">
        <div class="p-0 container__border--bottom container__border--red section__header">
          <i class="fa fa-database"></i>
          <span data-i18n="dashboard.title"> Lista warstw wektorowych</span>
        </div>
        <div class="p-0">
          <input type="text" class="form-control container__input">
        </div>
      </h2>
    </div>

    <div class="col-sm-12 pl-0 pr-0 container__border--bottom container__border--grey section">
      <h2 class="flex-center mb-0">
        <div class="p-0 container__border--bottom container__border--red section__header">
          <i class="fa fa-database"></i>
          <span data-i18n="dashboard.title"> Lista ze źródeł zewnętrznych</span>
        </div>
        <div class="p-0">
          <input type="text" class="form-control container__input">
        </div>
      </h2>
    </div>
  </div>
</template>

<script>

export default {
  name: 'dashboard',
};
</script>

<style scoped>
.container {
  top: 20px;
}
.container__input {
  width: 300px;
}
.dashboard.container {
  height: calc(100% - 76px);
  padding-left: 0px;
  padding-right: 0px;
}
.section {
  margin-top: 20px;
}
.section__header {
  padding-bottom: 15px;
  margin-bottom: -1px;
}
</style>

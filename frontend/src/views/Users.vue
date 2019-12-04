<template>
  <div class="container align-center">
    <div class="col-sm-12 pl-0 pr-0 section">
      <h2 class="flex-center container__border--bottom container__border--grey mb-0">
        <div class="p-0 container__border--bottom container__border--red section__header">
          <i class="fa fa-user-plus"></i>
          <span data-i18n="dashboard.title"> {{$i18n.t('users.title.addUser')}}</span>
        </div>
      </h2>
      <div class="section__content heading-block heading-block-main pt-10" style="display: flex;">
        <input type="text" class="form-control container__input mr-5" v-model="email"
          :placeholder="$i18n.t('default.email')">
        <input type="password" class="form-control container__input mr-5" v-model="password"
          :placeholder="$i18n.t('default.password')">
        <button type="button" class="btn btn-success" @click="registerRequest">
          {{$i18n.t('default.add')}}
        </button>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  data: () => ({
    email: undefined,
    password: undefined,
  }),
  methods: {
    async registerRequest() {
      if (!this.email || !this.password) {
        this.$alertify.error(this.$i18n.t('users.responses.noEmailOrPassword'));
        return;
      }
      const payload = { user: this.email, password: this.password };
      const r = await this.$store.dispatch('register', payload);
      if (r.status === 201) {
        this.$alertify.success(this.$i18n.t('users.responses.userCreated'));
        this.email = undefined;
        this.password = undefined;
      } else if (r.status === 409) {
        this.$alertify.error(this.$i18n.t('users.responses.userExists'));
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
  },
};
</script>

<style scoped>
.btn-upload {
  margin-right: 20px;
}
.container {
  top: 20px;
}
.container__input {
  width: 300px;
}
.control-label {
  line-height: 29px;
  font-size: 12px;
}
.container {
  height: calc(100% - 76px);
  padding-left: 0px;
  padding-right: 0px;
}
.desc-sm {
  color: #b5b5b5;
  font-family: "Open Sans","Trebuchet MS",arial,sans-serif;
  font-size: 12px;
  letter-spacing: -1px;
  line-height: 1.75em;
  margin-left: 5px;
}
.files-list li {
  width: 120px;
  list-style: none;
}
.heading-block:after, .heading-block:before {
  display: none;
}
.loading-overlay {
  width: 100%;
  text-align: center;
}
.panel-title__names {
  font-size: 14px;
}
.panel-title__tools i:not(:last-child) {
  margin-right: 5px;
}
.section {
  height: 50%;
}
.section__content.heading-block.heading-block-main {
  overflow-y: auto;
  max-height: calc(100% - 50px);
}
.section__header {
  padding-bottom: 15px;
  margin-bottom: -1px;
}
.text-centered {
  text-align: center;
}
.text-left {
  text-align: left;
}
</style>

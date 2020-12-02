<template>
  <div class="content content-login" @keyup.enter="loginRequest">
    <div class="container">
      <div class="account-wrapper">
        <div class="account-body">
          <h3 class="text-center">{{ $i18n.t('login.loginTitle') }}</h3>
          <div class="form-group">
            <input
              id="login-username"
              ref="login-username"
              v-model="email"
              type="text"
              name="email"
              class="form-control"
              :placeholder="$i18n.t('default.login')"
              tabindex="1"
            />
          </div>
          <div class="form-group">
            <input
              id="login-password"
              v-model="password"
              type="password"
              name="password"
              class="form-control"
              :placeholder="$i18n.t('default.password')"
              tabindex="2"
            />
          </div>
          <div class="form-group">
            <button
              id="loginButton"
              type="submit"
              class="btn btn-primary btn-block btn-lg"
              tabindex="4"
              @click="loginRequest"
            >
              <span>{{ $i18n.t('login.logIn') }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data: () => ({
    email: '',
    password: ''
  }),
  mounted() {
    this.$refs['login-username'].focus();
  },
  methods: {
    async loginRequest() {
      const payload = { user: this.email, password: this.password };
      const r = await this.$store.dispatch('logIn', payload);
      if (r && r.status === 200) {
        this.$alertify.success(this.$i18n.t('default.loginSuccess'));
        this.$router.push({ name: 'dashboard' });
      } else if (r && r.status === 403) {
        this.$alertify.error(this.$i18n.t('default.loginError'));
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    }
  }
};
</script>

<style scoped>
.content-login {
  height: calc(100% - 56px);
  display: flex;
  align-items: center;
  margin-bottom: 0;
}
</style>

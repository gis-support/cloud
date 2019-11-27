<template>
  <div class="content content-login">
      <div class="container">
        <div class="account-wrapper">
          <div class="account-body">
            <h3 class="text-center">{{$i18n.t('login.loginTitle')}}</h3>
              <div class="form-group">
                <input type="text" name="email" class="form-control" id="login-username"
                :placeholder="$i18n.t('default.email')" tabindex="1" v-model="email">
              </div>
              <div class="form-group">
                <input type="password" name="password" class="form-control"
                id="login-password" :placeholder="$i18n.t('default.password')"
                tabindex="2" v-model="password">
              </div>

              <div class="form-group clearfix" v-if="loginError">
                  <div class="alert alert-danger">{{ loginErrorMsg }}</div>
              </div>

              <div class="form-group">
                <button type="submit" id="loginButton" class="btn btn-primary btn-block btn-lg"
                tabindex="4" @click="loginRequest">
                  <span>{{$i18n.t('login.logIn')}}</span>
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
    email: 'docker',
    loginError: false,
    loginErrorMsg: '',
    password: 'docker',
  }),
  methods: {
    async loginRequest() {
      const payload = { user: this.email, password: this.password };
      const r = await this.$store.dispatch('logIn', payload);
      if (r.status === 200) {
        this.$alertify.success('Zalogowano');
        this.$router.push({ name: 'dashboard' });
      } else if (r.status === 403) {
        this.$alertify.error('Nieprawidłowa nazwa użytkownika lub hasło');
      } else {
        this.$alertify.error('Wystąpił błąd - skontaktuj się z administratorem');
      }
    },
  },
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

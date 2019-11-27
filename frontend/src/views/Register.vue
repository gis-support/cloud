<template>
  <div class="content content-register">
      <div class="container">
        <div class="account-wrapper">
          <div class="account-body">
            <h3 class="text-center">{{$i18n.t('register.registerTitle')}}</h3>
              <div class="form-group">
                <input type="text" name="email" class="form-control" id="register-username"
                :placeholder="$i18n.t('default.email')" tabindex="1" v-model="email">
              </div>
              <div class="form-group">
                <input type="password" name="password" class="form-control"
                id="register-password" :placeholder="$i18n.t('default.password')"
                tabindex="2" v-model="password">
              </div>
              <div class="form-group">
                <button type="submit" id="registerButton" class="btn btn-primary btn-block btn-lg"
                tabindex="4" @click="registerRequest">
                  <span>{{$i18n.t('register.register')}}</span>
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
    password: '',
  }),
  methods: {
    async registerRequest() {
      const payload = { user: this.email, password: this.password };
      const r = await this.$store.dispatch('register', payload);
      if (r.status === 201) {
        this.$alertify.success('Utworzono użytkownika - można przystąpić do logowania');
        this.$router.push({ name: 'login' });
      } else if (r.status === 409) {
        this.$alertify.error('Użytkownik o podanym adresie email istnieje');
      } else {
        this.$alertify.error('Wystąpił błąd - skontaktuj się z administratorem');
      }
    },
  },
};
</script>

<style scoped>
.content-register {
  height: calc(100% - 56px);
  display: flex;
  align-items: center;
  margin-bottom: 0;
}
</style>

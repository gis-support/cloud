<template>
  <div id="app">
    <div id="nav">
      <header
        class="navbar"
        role="banner"
      >
        <div class="container">
          <div class="navbar-header">
            <button
              class="navbar-toggle"
              type="button"
              data-toggle="collapse"
              data-target=".navbar-collapse"
            >
              <span class="sr-only">Toggle navigation</span>
              <i class="fa fa-cog" />
            </button>
            <a
              class="navbar-brand navbar-brand-img"
              @click="redirectToDashboard()"
            >
              <img
                id="logo"
                alt="GIS Support logo"
                :src="`${this.$store.getters.getApiUrl}/logo`"
              />
            </a>
          </div>
          <nav
            v-if="user"
            class="collapse navbar-collapse"
            role="navigation"
          >
            <ul class="nav navbar-nav navbar-right">
              <!-- <li class="navbar-profile" :disabled="$i18n.locale == 'en'"
                :class="{ btnActive: $i18n.locale == 'en'}" @click="changeLanguage('en')">
                <a>EN</a>
              </li>
              <li class="navbar-profile" :disabled="$i18n.locale == 'pl'"
                :class="{ btnActive: $i18n.locale == 'pl'}" @click="changeLanguage('pl')">
                <a>PL</a>
              </li>-->
              <li class="dropdown navbar-profile">
                <a
                  class="dropdown-toggle"
                  style="padding-left: 15px;"
                  data-toggle="dropdown"
                  href="javascript:;"
                >
                  <span>{{ user }} &nbsp;</span>
                  <i class="fa fa-caret-down" />
                </a>
                <ul
                  class="dropdown-menu"
                  role="menu"
                >
                  <li @click="changePage('dashboard')">
                    <a>
                      <i class="fa fa-dashboard" />
                      &nbsp;&nbsp;
                      <span
                        v-bind:class="{'active-route':this.$route.name==='dashboard'}"
                      >{{ $i18n.t('default.dashboard') }}</span>
                    </a>
                  </li>
                  <li @click="changePage('users')">
                    <a>
                      <i class="fa fa-users" />
                      &nbsp;&nbsp;
                      <span
                        v-bind:class="{'active-route':this.$route.name==='users'}"
                      >{{ $i18n.t('default.users') }}</span>
                    </a>
                  </li>
                  <li @click="changePage('appSettings')">
                    <a>
                      <i class="fa fa-cog" />
                      &nbsp;&nbsp;
                      <span
                        v-bind:class="{'active-route':this.$route.name==='appSettings'}"
                      >{{ $i18n.t('default.settings') }}</span>
                    </a>
                  </li>
                  <li @click="changePage('help')">
                    <a>
                      <i class="fa fa-question-circle" />
                      &nbsp;&nbsp;
                      <span
                        v-bind:class="{'active-route':this.$route.name==='help'}"
                      >{{ $i18n.t('default.help') }}</span>
                    </a>
                  </li>
                  <li @click="logout">
                    <a>
                      <i class="fa fa-sign-out" />
                      &nbsp;&nbsp;
                      <span>{{ $i18n.t('default.logout') }}</span>
                    </a>
                  </li>
                </ul>
              </li>
            </ul>
          </nav>
        </div>
      </header>
    </div>
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    user() {
      return this.$store.getters.getUser;
    }
  },
  methods: {
    changeLanguage(lang) {
      this.$i18n.locale = lang;
    },
    changePage(pageName) {
      if (this.$route.name !== pageName) {
        this.$router.push({ name: pageName });
      }
    },
    logout() {
      this.$store.commit('logOut');
      this.$router.push({ name: 'login' });
    },
    redirectToDashboard() {
      this.$router.push({ name: 'dashboard' });
    }
  },
  async mounted() {
    this.changeLanguage('pl');
  }
};
</script>

<style>
#app {
  height: 100%;
}
.active-route {
  font-weight: bold;
}
.align-center {
  text-align: center;
  align-items: center;
}
.bold {
  font-weight: 600;
}
.btnActive {
  background-color: #283846;
}
.btnActive a {
  color: #fff !important;
}
.container__border--bottom {
  border-bottom: 1px solid;
}
.container__border--grey {
  border-color: #e3e3e3;
}
.container__border--red {
  border-color: #d74b4b;
}
.d-flex {
  display: flex;
}
.dropdown-menu:hover {
  cursor: default;
}
.flex-center {
  display: flex !important;
  justify-content: space-between !important;
}
.full-width {
  width: 100%;
}
.green {
  color: #1e5b22 !important;
}
.icon-hover {
  opacity: 0.3;
  padding: 2px;
  transition: all 0.2s;
}
.icon-hover:hover {
  opacity: 1;
  padding: 2px;
  cursor: pointer;
}
.navbar-brand-img:hover {
  cursor: pointer;
}
.mb-0 {
  margin-bottom: 0px !important;
}
.mb-5 {
  margin-bottom: 5px !important;
}
.mb-10 {
  margin-bottom: 10px !important;
}
.mr-5 {
  margin-right: 5px !important;
}
.p-0 {
  padding: 0px;
}
.pl-0 {
  padding-left: 0px !important;
}
.pr-0 {
  padding-right: 0px !important;
}
.pb-10 {
  padding-bottom: 10px !important;
}
.pt-10 {
  padding-top: 10px !important;
}
.py-5 {
  padding: 5px 0 !important;
}
.red {
  color: #f22a1f !important;
}
.yellow {
  color: #bf822c !important;
}
#logo {
  height: 50px;
}
</style>

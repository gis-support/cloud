<template>
  <div id="app">
    <div id="nav">
      <header class="navbar" role="banner">
        <div class="container">
          <div class="navbar-header">
            <button class="navbar-toggle" type="button" data-toggle="collapse"
            data-target=".navbar-collapse">
              <span class="sr-only">Toggle navigation</span>
              <i class="fa fa-cog"></i>
            </button>
            <a class="navbar-brand navbar-brand-img">
              <img id="logo" alt="GIS Support logo" src="@/assets/logo.png">
            </a>
          </div>
          <nav class="collapse navbar-collapse" role="navigation">
            <ul class="nav navbar-nav navbar-right">
              <!-- <li class="navbar-profile" :disabled="$i18n.locale == 'en'"
                :class="{ btnActive: $i18n.locale == 'en'}" @click="changeLanguage('en')">
                <a>EN</a>
              </li>
              <li class="navbar-profile" :disabled="$i18n.locale == 'pl'"
                :class="{ btnActive: $i18n.locale == 'pl'}" @click="changeLanguage('pl')">
                <a>PL</a>
              </li> -->
              <li class="dropdown navbar-profile">
                <a class="dropdown-toggle" style="padding-left: 15px;" data-toggle="dropdown"
                href="javascript:;" >
                  <span>username &nbsp;</span>
                  <i class="fa fa-caret-down"></i>
                </a>
                <ul class="dropdown-menu" role="menu">
                  <li>
                    <a>
                      <i class="fa fa-sign-out"></i>
                      &nbsp;&nbsp;<span>Wyloguj się</span>
                    </a>
                  </li>
                </ul>
              </li>
            </ul>
          </nav>
        </div>
      </header>
    </div>
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App',
  methods: {
    changeLanguage(lang) {
      this.$i18n.locale = lang;
    },
  },
  mounted() {
    this.changeLanguage('pl');
  },
};
</script>

<style>
#app {
  height: 100%;
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
.flex-center {
  display: flex;
  justify-content: space-between;
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
.mb-0 {
  margin-bottom: 0px !important;
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

<template>
  <div class="container-fluid">
    <div class="row">
      <div
        style="overflow:auto"
        class="sidebar"
      >
        <ul class="nav nav-layout-sidebar">
          <li
            v-for="(header,idx) in headers"
            :key="idx"
            @click="activateHeader(header.name)"
          >
            <a>
              <i
                v-bind:class="{'fa-angle-right':!header.visible, 'fa-angle-down':header.visible}"
                class="fa"
              />
              &nbsp;&nbsp;
              <span style="font-weight: bold">{{ header.name }}</span>
            </a>
            <ul
              id="myTab"
              class="nav nav-layout-sidebar"
              v-show="header.visible"
            >
              <li
                v-for="(subheader,idx2) in helpItems[header.name]"
                :key="idx2"
                @click.stop
              >
                <a
                  style="padding-left:40px"
                  v-bind:class="{'active':subheader['Tytul'] === activeTitle}"
                  @click="activateSubheader(subheader)"
                >
                  &nbsp;&nbsp;
                  <span>{{ subheader.Tytul }}</span>
                </a>
              </li>
            </ul>
          </li>
        </ul>
      </div>
      <div class="column">
        <div v-if="activeSubheader">
          <div class="help-title">
            <h1>{{activeTitle}}</h1>
          </div>
          <div
            v-if="activeLink"
            class="help-yt"
          >
            <youtube
              :fitParent="true"
              :video-id="activeLink"
            />
          </div>
          <div class="help-desc">
            <h5>{{activeDescription}}</h5>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { HELP } from '@/help';
export default {
  name: 'Help',
  data: () => ({
    activeSubheader: false,
    activeTitle: '',
    activeDescription: '',
    activeLink: '',
    headers: [],
    helpItems: [],
    isCollapsed: false
  }),
  methods: {
    activateHeader(name) {
      for (let idx in this.headers) {
        if (this.headers[idx].name !== name) {
          this.headers[idx].visible = false;
        } else {
          this.headers[idx].visible = !this.headers[idx].visible;
        }
      }
    },
    activateSubheader(subheader) {
      this.activeTitle = subheader['Tytul'];
      this.activeDescription = subheader['OPIS'];
      this.activeLink = this.$youtube.getIdFromUrl(subheader['LINK YOUTUBE']);
      this.activeSubheader = true;
    },
    toggleCollapsation() {
      this.isCollapsed = !this.isCollapsed;
    }
  },
  mounted() {
    this.helpItems = HELP;
    for (let header of Object.keys(this.helpItems)) {
      this.headers.push({ name: header, visible: false });
    }
  }
};
</script>
<style scoped>
.active {
  color: black;
  background-color: #e5e5e5;
}
.column {
  float: left;
  width: 76%;
  padding: 10px;
  padding-top: 40px;
  height: calc(100vh - 56px);
}
.help-title {
  text-align: center;
}
.help-yt {
  margin: auto;
  width: 90vh;
  min-height: 55vh;
}
.help-desc {
  text-align: center;
  margin-top: 50px;
  white-space: pre-line;
}
.nav-layout-sidebar {
  border: none;
}
.nav-layout-sidebar > li > a {
  border: none;
}
.nav-layout-sidebar > li > a:hover {
  background-color: #e5e5e5;
  cursor: pointer;
}
.sidebar {
  float: left;
  width: 24%;
  padding: 10px;
  height: calc(100vh - 56px);
  background-color: #f5f5f5;
}
</style>
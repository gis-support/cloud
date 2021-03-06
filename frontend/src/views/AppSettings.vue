<template>
  <div class="container">
    <div class="col-md-3 layout-sidebar">
      <ul id="myTab" class="nav nav-layout-sidebar nav-stacked">
        <li v-if="isAdmin" :class="{ active: isAdmin }">
          <a href="#tabLogo" data-toggle="tab" @click="setActiveTab('logo')">
            <i class="fa fa-image" />
            &nbsp;&nbsp;
            <span>{{ $i18n.t('settings.tabLogo') }}</span>
          </a>
        </li>
        <li v-if="isAdmin">
          <a href="#favicon" data-toggle="tab" @click="setActiveTab('tabFavicon')">
            <i class="fa fa-fonticons" />
            &nbsp;&nbsp;
            <span>{{ $i18n.t('settings.tabFavicon') }}</span>
          </a>
        </li>
        <li :class="{ active: !isAdmin }">
          <a href="#qgisLogo" data-toggle="tab" @click="setActiveTab('qgis')">
            <i class="fa">Q</i>
            &nbsp;&nbsp;
            <span>{{ $i18n.t('settings.tabQgis') }}</span>
          </a>
        </li>
        <li>
          <a href="#tags" data-toggle="tab" @click="setActiveTab('tags')">
            <i class="fa fa-tumblr" />
            &nbsp;&nbsp;
            <span>{{ $i18n.t('settings.tags') }}</span>
          </a>
        </li>
      </ul>
    </div>
    <div class="col-md-9 col-sm-8 layout-main">
      <div id="settings-content" class="tab-content stacked-content">
        <div class="heading-block">
          <h3>
            <span data-i18n="settings.title">{{ $i18n.t('default.settings') }}:</span>
            <span class="red">{{ $i18n.t(`settings.${activeTab}`) }}</span>
          </h3>
        </div>
        <div v-if="activeTab === 'logo'" id="tabLogo" class="tab-pane in active">
          <div>
            <h4 class="text-left">{{ $i18n.t('settings.addNewLogo') }}</h4>
            <FileUpload
              ref="uploadLogo"
              v-model="logo"
              accept="image/*"
              :post-action="postLogo"
              :multiple="false"
              :drop="true"
              :drop-directory="true"
              @input-filter="inputFilter"
              @input-file="inputFile"
            >
              {{ this.$i18n.t('upload.uploadLogoMessage') }}
              <ul>
                <li v-if="logo" style="color:green;list-style-position: inside">
                  {{ logo[0].name }}
                </li>
              </ul>
            </FileUpload>
          </div>
          <button
            type="button"
            class="btn btn-success"
            :disabled="!logo"
            style="float:right"
            @click="addLogo()"
          >
            {{ $i18n.t('default.add') }}
          </button>
        </div>
        <div v-if="activeTab === 'qgis'" id="tabQgis" class="tab-pane in active">
          <div>
            <h4>Twoje dane połączenia się do Cloud przez QGIS</h4>
            <table class="qgis-data-list">
              <tr>
                <td>
                  <h5>{{ this.$i18n.t('settings.host') }}:</h5>
                </td>
                <td>{{ host }}</td>
              </tr>
              <tr>
                <td>
                  <h5>{{ this.$i18n.t('settings.database') }}:</h5>
                </td>
                <td>cloud</td>
              </tr>
              <tr>
                <td>
                  <h5>{{ this.$i18n.t('settings.port') }}:</h5>
                </td>
                <td>{{ port }}</td>
              </tr>
            </table>
          </div>
        </div>
        <div v-if="activeTab === 'tabFavicon'" id="tabFavicon" class="tab-pane in active">
          <div>
            <h4 class="text-left">{{ $i18n.t('settings.addNewFavicon') }}</h4>
            <FileUpload
              ref="uploadFavicon"
              v-model="favicon"
              accept="image/*"
              :post-action="postFavicon"
              :multiple="false"
              :drop="true"
              :drop-directory="true"
              @input-filter="inputFilter"
              @input-file="inputFile"
            >
              {{ this.$i18n.t('upload.uploadLogoMessage') }}
              <ul>
                <li v-if="favicon" style="color:green;list-style-position: inside">
                  {{ favicon[0].name }}
                </li>
              </ul>
            </FileUpload>
          </div>
          <button
            type="button"
            class="btn btn-success"
            :disabled="!favicon"
            style="float:right"
            @click="addFavicon()"
          >
            {{ $i18n.t('default.add') }}
          </button>
        </div>
        <div v-if="activeTab === 'tags'" id="tabTags" class="tab-pane in active">
          <Tags />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import FileUpload from 'vue-upload-component';
import Tags from '@/components/Tags';

export default {
  name: 'AppSettings',
  components: {
    FileUpload,
    Tags
  },
  data: vm => ({
    activeTab: '',
    favicon: undefined,
    logo: undefined,
    postLogo: `${vm.$store.getters.getApiUrl}/logo?token=${localStorage.getItem('token')}`,
    postFavicon: `${vm.$store.getters.getApiUrl}/favicon?token=${localStorage.getItem('token')}`
  }),
  computed: {
    host() {
      return process.env.VUE_APP_PROD_HOST_URL;
    },
    port() {
      return process.env.VUE_APP_PROD_DB_PORT;
    },
    isAdmin() {
      const jwtDecode = require('jwt-decode');
      return jwtDecode(this.$store.getters.getToken).admin;
    }
  },
  mounted() {
    if (this.isAdmin) {
      this.setActiveTab('logo');
    } else {
      this.setActiveTab('qgis');
    }
  },
  methods: {
    addFavicon() {
      this.$refs.uploadFavicon.active = true;
    },
    addLogo() {
      this.$refs.uploadLogo.active = true;
    },
    inputFile(newFile, oldFile) {
      if (newFile && oldFile) {
        if (newFile.error && !oldFile.error) {
          this.$alertify.error(this.$i18n.t('upload.uploadError'));
          this.logo = undefined;
        }
        if (newFile.success && !oldFile.success) {
          this.$alertify.success(this.$i18n.t('upload.uploadSuccess'));
          this.logo = undefined;
          this.favicon = undefined;
        }
      }
    },
    inputFilter(newFile, oldFile, prevent) {
      if (newFile && !oldFile) {
        if (!/\.(jpeg|jpe|jpg|gif|png|ico)$/i.test(newFile.name)) {
          this.$alertify.error(this.$i18n.t('upload.uploadExtensionError'));
          return prevent();
        }
      }
    },
    setActiveTab(tab) {
      this.activeTab = tab;
    }
  }
};
</script>

<style scoped>
.control-label {
  position: relative;
  top: 8px;
}
.color-picker__container {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.disabled {
  cursor: not-allowed !important;
}
.file-uploads {
  overflow: hidden;
  position: relative;
  text-align: center;
  display: inline-block;
  min-height: 100px;
  width: 100%;
  border: 1px solid lightgray;
}
.file-uploads.file-uploads-html4 input[type='file'] {
  opacity: 0;
  font-size: 20em;
  z-index: 1;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  position: absolute;
  width: 100%;
  height: 100%;
}
.file-uploads.file-uploads-html5 input[type='file'] {
  overflow: hidden;
  position: fixed;
  width: 1px;
  height: 1px;
  z-index: -1;
  opacity: 0;
}
.mb-10 {
  margin-bottom: 10px;
}
.ml-10 {
  margin-left: 10px;
}
.mt-15 {
  margin-top: 15px;
}
.picker__container {
  display: flex;
}
.pr-30 {
  padding-right: 30px;
}
.qgis-data-list > tr > td {
  vertical-align: top;
  padding: 5px;
  padding-right: 40px;
}
.text-centered {
  text-align: center;
}
.text-left {
  text-align: left;
}
</style>

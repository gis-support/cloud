<template>
  <div class="container">
    <div class="col-md-3 layout-sidebar">
      <ul
        id="myTab"
        class="nav nav-layout-sidebar nav-stacked"
      >
        <li class="active">
          <a
            href="#logo-tab"
            data-toggle="tab"
            @click="setActiveTab('logo-tab')"
          >
            <i class="fa fa-image" />
            &nbsp;&nbsp;
            <span>{{ $i18n.t('settings.logo') }}</span>
          </a>
        </li>
      </ul>
    </div>
    <div class="col-md-9 col-sm-8 layout-main">
      <div
        id="settings-content"
        class="tab-content stacked-content"
      >
        <div class="heading-block">
          <h3>
            <span data-i18n="settings.title">{{ $i18n.t('default.settings') }}:</span>
            <span class="red">{{ $i18n.t('settings.logo') }}</span>
          </h3>
        </div>
        <div
          class="tab-pane in active"
          id="logo-tab"
          v-if="activeTab === 'logo-tab'"
        >
          <div>
            <h4 class="text-left">{{ $i18n.t('settings.addNewLogo') }}</h4>
            <file-upload
              ref="upload"
              v-model="logo"
              accept="image/*"
              :post-action="postAction"
              :multiple="false"
              :drop="true"
              :drop-directory="true"
              @input-filter="inputFilter"
              @input-file="inputFile"
            >
              {{this.$i18n.t('upload.uploadLogoMessage')}}
              <ul>
                <li
                  style="color:green"
                  v-if="logo"
                >{{logo[0].name}}</li>
              </ul>
            </file-upload>
          </div>
          <button
            type="button"
            class="btn btn-success"
            @click="addLogo()"
            :disabled="!logo"
            style="float:right"
          >{{ $i18n.t('default.add') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import FileUpload from 'vue-upload-component';

export default {
  name: 'AppSettings',
  data: () => ({
    activeTab: 'logo-tab',
    logo: undefined,
    postAction: `${
      vm.$store.getters.getApiUrl
    }/logo?token=${localStorage.getItem('token')}`
  }),
  components: {
    FileUpload
  },
  methods: {
    addLogo() {
      this.$refs.upload.active = true;
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
        }
      }
    },
    inputFilter(newFile, oldFile, prevent) {
      if (newFile && !oldFile) {
        if (!/\.(jpeg|jpe|jpg|gif|png)$/i.test(newFile.name)) {
          this.$alertify.error(this.$i18n.t('upload.uploadExtensionError'));
          return prevent();
        }
      }
    },
    removeLogo() {
      this.logo = undefined;
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
.text-centered {
  text-align: center;
}
.text-left {
  text-align: left;
}
.verte {
  display: flex;
  justify-content: center;
  top: 5px;
}
</style>
<template>
  <div class="attachments-panel right-sub-panel">
    <div v-if="filesAttachments">
      <!-- Początek załączników plikowych -->
      <span>
        <div v-if="isfilesAttachmentsLoaded" class="pt-10 pb-10">
          <h4>{{ 'Załączniki' }}:</h4>
          <div style="overflow-y: auto; max-height: 50vh">
            <div v-if="filesAttachments.length < 1" class="empty-sub-panel">
              <i class="fa fa-paperclip" aria-hidden="true" />
              {{ $i18n.t('default.noAttachments') }}
            </div>
            <template v-for="att in filesAttachments" v-else>
              <div :key="att.id" class="media">
                <div class="media-left">
                  <h3>
                    <i class="fa fa-paperclip" aria-hidden="true" />
                  </h3>
                </div>
                <div class="media-body">
                  <h5 class="media-heading">
                    <span>
                      <input
                        id="checkbox"
                        v-model="checkedIds"
                        class="mr-5"
                        type="checkbox"
                        :value="att.id"
                      />
                      <span
                        class="mr-5"
                        style="cursor: pointer"
                        @click="downloadFileAttachments(att.id.toString())"
                        >{{ att.file_name }}</span
                      >
                      <i
                        class="fa fa-trash"
                        aria-hidden="true"
                        style="cursor: pointer"
                        :title="$i18n.t('featureManager.deleteAttachment')"
                        @click="deleteFileAttachments(att.id)"
                      />
                    </span>
                  </h5>
                  <h6 class="media-heading">
                    <span>{{ 'Autor: ' + att.added_by }}</span>
                  </h6>
                  <h6 class="media-heading">
                    <span>{{
                      'Data: ' + new Date(Date.parse(att.added_at)).toLocaleDateString('pl-PL')
                    }}</span>
                  </h6>
                </div>
              </div>
            </template>
          </div>
        </div>
        <div v-else class="loading-overlay pt-10 pb-10" style="text-align: center">
          <div class="loading-indicator mb-10">
            <h4>{{ $i18n.t('default.loading') }}</h4>
            <i class="fa fa-lg fa-spin fa-spinner" />
          </div>
        </div>

        <div class="btn-group btn-group-justified" role="group">
          <div class="btn-group" role="group">
            <button
              v-if="permission === 'write' && isfilesAttachmentsLoaded"
              class="btn btn-link"
              @click="toggleFileAttachmentAdding(true)"
            >
              <i class="fa fa-plus-circle" aria-hidden="true" />
              {{ $i18n.t(`featureManager.addAttachment`) }}
            </button>
          </div>
          <div class="btn-group" role="group">
            <button
              v-if="permission === 'write' && filesAttachments.length > 0"
              class="btn btn-link green"
              :disabled="checkedIds.length < 1"
              @click="downloadFileAttachments(checkedIds.join(','))"
            >
              <i class="fa fa-download" aria-hidden="true" />
              {{ $i18n.t(`featureManager.checkedDownload`) }}
            </button>
          </div>
          <div class="btn-group" role="group">
            <button
              v-if="permission === 'write' && filesAttachments.length > 0"
              class="btn btn-link red"
              :disabled="checkedIds.length < 1"
              @click="deleteFileAttachments(checkedIds.join(','))"
            >
              <i class="fa fa-trash" aria-hidden="true" />
              {{ $i18n.t(`featureManager.checkedDelete`) }}
            </button>
          </div>
        </div>
      </span>
      <!-- Koniec załączników plikowych -->
    </div>
    <!-- Modal załączników plikowych -->
    <div v-if="isFileAttachmentAdding" class="modal-mask">
      <div class="modal-wrapper">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h4 class="modal-title">
                {{ $i18n.t('featureManager.addAttachmentTitle') }}
              </h4>
            </div>
            <div class="modal-body">
              <div class="pt-10">
                <FileUpload
                  ref="upload"
                  v-model="files"
                  :multiple="true"
                  :drop="true"
                  :drop-directory="true"
                  @input-filter="fileFilter"
                >
                  {{ this.$i18n.t('upload.defaultMessage') }}
                  <ul>
                    <li v-for="(file, idx) in files" :key="idx" style="list-style-position: inside">
                      {{ file.name }}
                      <i
                        class="icon-li fa fa-times fa-lg ml-5 delete-file-icon"
                        @click.stop="removeFile(file)"
                      />
                    </li>
                  </ul>
                </FileUpload>
              </div>
            </div>
            <div class="modal-footer">
              <button
                ref="closeModalBtn"
                type="button"
                class="btn btn-default"
                data-dismiss="modal"
                @click="clearUploadFiles"
              >
                {{ $i18n.t('default.cancel') }}
              </button>
              <button
                type="button"
                class="btn btn-success"
                :disabled="files.length < 1"
                @click="sendFiles"
              >
                {{ $i18n.t('default.save') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import FileUpload from 'vue-upload-component';
export default {
  components: {
    FileUpload
  },
  props: {
    attachmentsIds: {
      type: String,
      default: ''
    },
    lid: {
      type: String,
      default: ''
    },
    fid: {
      type: Number,
      default: 0
    },
    permission: {
      type: String,
      default: ''
    },
    usersGroup: {
      type: String,
      default: ''
    }
  },
  data: vm => ({
    attachmentLink: undefined,
    // attachmentModes: ['public', 'default'],
    attachementsData: [],
    attachmentName: undefined,
    checkedIds: [],
    dataFiles: [],
    files: [],
    filesAttachments: [],
    isAttachmentAdding: false,
    isFileAttachmentAdding: false,
    isAttachmentPublic: '',
    isfilesAttachmentsLoaded: true,
    isFilePrepared: false,
    postAction: `${vm.$store.getters.getApiUrl}/attachments_qgis?token=${localStorage.getItem(
      'token'
    )}`
    // usersGroup: undefined,
  }),
  computed: {
    defaultGroup() {
      return this.$store.getters.getDefaultGroup;
    },
    user() {
      return this.$store.getters.getUser;
    },
    usersWithGroups() {
      return this.$store.getters.getUsersWithGroups;
    }
  },
  watch: {
    isFilePrepared(newValue) {
      if (newValue) {
        this.$http
          .post(
            this.postAction,
            { data: this.dataFiles },
            { params: { feature_id: this.fid, layer_id: this.lid } }
          )
          .then(r => {
            if (r.status === 201) {
              this.clearUploadFiles();
              this.$alertify.success(this.$i18n.t('upload.uploadSuccess'));
              const dateNow = new Date(Date.now());
              const idsToAdd = [];
              const newAtts = [];
              const user = this.$store.getters.getUser;
              for (let idx in r.data.data) {
                const newAtt = r.data.data[idx];
                newAtt.added_at = dateNow;
                newAtt.added_by = user;
                newAtt.file_name = newAtt.saved_as;
                newAtt.id = newAtt.attachment_id;
                newAtts.push(newAtt);
                idsToAdd.push(newAtt.attachment_id);
              }
              this.$emit('addIds', idsToAdd.join(';'));
              this.filesAttachments = this.filesAttachments.concat(newAtts);
            } else {
              this.$alertify.error(this.$i18n.t('upload.uploadError'));
            }
          })
          .catch(err => {
            if (err.response.data.error === 'layer does not contain column __attachments') {
              this.$alertify.error(this.$i18n.t('upload.noColumnError'));
            } else {
              this.$alertify.error(this.$i18n.t('upload.uploadError'));
            }
          });
      }
    }
  },
  mounted() {
    this.getUsers();
    this.$store.commit('setDefaultGroup', process.env.VUE_APP_DEFAULT_GROUP);
  },
  methods: {
    async addAttachment() {
      const r = await this.$store.dispatch('addAttachment', {
        lid: this.lid,
        fid: this.fid,
        body: {
          link: this.attachmentLink,
          name: this.attachmentName,
          public: this.isAttachmentPublic
        }
      });
      if (r.status === 201) {
        const { group } = r.obj.attachments;
        const params = {};
        params[group] = [r.obj.attachments];
        this.$store.commit('addAttachmentToFeature', {
          lid: this.lid,
          fid: this.fid,
          attachments: params
        });
        this.toggleAttachmentAdding(false);
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    async deleteFileAttachments(ids) {
      this.$alertify
        .confirm(
          ids.length > 1
            ? this.$i18n.t('featureManager.deleteAttachmentsConfirm')
            : this.$i18n.t('featureManager.deleteAttachmentConfirm'),
          async () => {
            const r = await this.$store.dispatch('deleteFileAttachments', {
              ids: ids,
              lid: this.lid,
              fid: this.fid
            });
            if (r.status === 204) {
              const idsToDelete = ids.toString().split(',');
              this.filesAttachments = this.filesAttachments.filter(fA => {
                return !idsToDelete.includes(fA.id.toString());
              });
              this.$emit('deleteIds', idsToDelete);
            } else {
              this.$alertify.error(this.$i18n.t('default.error'));
            }
          },
          () => {}
        )
        .set({ title: this.$i18n.t('featureManager.deleteAttachmentHeader') })
        .set({
          labels: {
            ok: this.$i18n.t('default.delete'),
            cancel: this.$i18n.t('default.cancel')
          }
        });
    },
    async downloadFileAttachments(ids) {
      let name = undefined;
      if (ids.split(',').length === 1) {
        name = this.filesAttachments.find(fA => fA.id == ids).file_name;
      }
      const r = await this.$store.dispatch('downloadFileAttachments', ids);
      if (r.status === 200) {
        const blob = new Blob([r.data]);
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        name ? link.setAttribute('download', name) : link.setAttribute('download', `${ids}.zip`);
        link.click();
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    async getAttachmentsMeta() {
      this.isfilesAttachmentsLoaded = false;
      this.filesAttachments = [];
      if (this.attachmentsIds) {
        const r = await this.$store.dispatch(
          'getAttachmentsMeta',
          this.attachmentsIds.split(';').join(',')
        );
        if (r.status === 200) {
          this.filesAttachments = r.obj.data;
          this.isfilesAttachmentsLoaded = true;
        } else {
          this.$alertify.error(this.$i18n.t('default.error'));
          this.isfilesAttachmentsLoaded = true;
        }
      } else {
        this.isfilesAttachmentsLoaded = true;
      }
    },
    async getUsers() {
      if (Object.keys(this.usersWithGroups).length > 0) {
        this.usersGroup = this.usersWithGroups[this.user];
      }
    },
    clearUploadFiles() {
      this.files = [];
      this.isFileAttachmentAdding = false;
    },
    deleteLink(item) {
      this.$alertify
        .confirm(
          this.$i18n.t('featureManager.deleteAttachmentConfirm'),
          async () => {
            const r = await this.$store.dispatch('deleteAttachment', {
              lid: this.lid,
              fid: this.fid,
              aid: item.id
            });
            if (r.status === 200) {
              this.$store.commit('deleteFeatureAttachment', {
                lid: this.lid,
                fid: this.fid,
                aid: item.id,
                attachType: item.group
              });
            } else if (r.status === 403) {
              if (r.body.error === 'access denied, not an owner') {
                this.$alertify.error(this.$i18n.t('upload.accessDenied'));
              }
            } else {
              this.$alertify.error(this.$i18n.t('default.error'));
            }
          },
          () => {}
        )
        .set({ title: this.$i18n.t('featureManager.deleteAttachmentHeader') })
        .set({
          labels: {
            ok: this.$i18n.t('default.delete'),
            cancel: this.$i18n.t('default.cancel')
          }
        });
    },
    fileFilter: function(newFile, oldFile, prevent) {
      // let ext = newFile.name.substr(newFile.name.lastIndexOf('.'));
      if (newFile && !oldFile) {
        for (const file of this.files) {
          if (newFile.name === file.name && newFile.size === file.size) {
            this.$alertify.error(this.$i18n.t('upload.uploadDuplicate'));
            return prevent();
          }
        }
      }
    },
    getBase64(file) {
      return new Promise(function(resolve, reject) {
        var reader = new FileReader();
        reader.onload = function() {
          resolve(reader.result);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    },
    removeFile(file) {
      let fileIndex = this.files.indexOf(file);
      if (fileIndex > -1) {
        this.files = this.files.filter(f => f != file);
      }
    },
    sendFiles() {
      this.isFilePrepared = false;
      let data = [];
      for (let file of this.files) {
        const name = file.file.name;
        var promise = this.getBase64(file.file);
        promise
          .then(function(result) {
            data.push({ content: result.split(',')[1], name: name });
          })
          .then(() => {
            if (this.files.length === data.length) {
              this.dataFiles = data;
              this.isFilePrepared = true;
            }
          });
      }
    },
    toggleAttachmentAdding(vis) {
      this.isAttachmentAdding = vis;

      this.attachmentLink = '';
      this.attachmentName = '';
      this.isAttachmentPublic = '';
    },
    toggleFileAttachmentAdding(vis) {
      this.isFileAttachmentAdding = vis;
    }
  }
};
</script>

<style scoped>
.control-label {
  position: relative;
  top: 8px;
}
.delete-file-icon {
  z-index: 2;
  position: relative;
}
.files-list li {
  width: 120px;
  list-style: none;
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
</style>

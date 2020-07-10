<template>
  <div class="attachments-panel right-sub-panel">
    <div v-if="featureAttachments || filesAttachments">
      <!-- Początek załączników publicznych -->
      <span v-if="isRdos">
        <h4>{{ $i18n.t(`featureManager.attachmentsTitlepublic`) }}:</h4>
        <div
          v-if="
          !Object.keys(featureAttachments).includes(defaultGroup) ||
            featureAttachments[defaultGroup].length === 0
        "
          class="empty-sub-panel"
        >
          <i
            class="fa fa-paperclip"
            aria-hidden="true"
          />
          {{ $i18n.t("default.noAttachments") }}
        </div>
        <!-- Lista załączników publicznych -->
        <span v-else>
          <template v-for="(item, idx) in featureAttachments[defaultGroup]">
            <div
              class="media"
              :key="idx"
            >
              <div class="media-left">
                <h3>
                  <i
                    class="fa fa-paperclip"
                    aria-hidden="true"
                  />
                </h3>
              </div>
              <div class="media-body">
                <h5 class="media-heading">
                  <a
                    :href="item.link"
                    target="_blank"
                  >
                    <span>{{ item.name }}</span>
                  </a>
                </h5>
                <span
                  style="opacity:0.4;"
                  v-if="permission === 'write'"
                >
                  <button
                    class="btn btn-link action"
                    :title="$i18n.t('featureManager.deleteLink')"
                    @click="deleteLink(item)"
                  >
                    <i
                      class="fa fa-trash"
                      aria-hidden="true"
                    />
                  </button>
                </span>
              </div>
            </div>
          </template>
        </span>
        <hr />
        <!-- Lista załączników grupowych -->
        <div v-if="usersGroup !== 'default'">
          <h4>
            <span>{{ $i18n.t(`featureManager.attachmentsTitleGroup`) + ": "}}</span>
            <span style="color:#d74b4b">{{ usersGroup }}</span>
          </h4>
          <div
            v-if="featureAttachments &&
          !Object.keys(featureAttachments).includes(usersGroup) ||
          featureAttachments[usersGroup].filter(el => el.group !== defaultGroup).length === 0
        "
            class="empty-sub-panel"
          >
            <i
              class="fa fa-paperclip"
              aria-hidden="true"
            />
            {{ $i18n.t("default.noAttachments") }}
          </div>
          <span v-else>
            <template
              v-for="(item, idx) in featureAttachments[usersGroup].filter(el => el.group !== defaultGroup)"
            >
              <div
                class="media"
                :key="idx"
              >
                <div class="media-left">
                  <h3>
                    <i
                      class="fa fa-paperclip"
                      aria-hidden="true"
                    />
                  </h3>
                </div>
                <div class="media-body">
                  <h5 class="media-heading">
                    <a
                      :href="item.link"
                      target="_blank"
                    >
                      <span>{{ item.name }}</span>
                    </a>
                  </h5>
                  <span style="opacity:0.4;">
                    <button
                      class="btn btn-link action"
                      :title="$i18n.t('featureManager.deleteLink')"
                      @click="deleteLink(item)"
                    >
                      <i
                        class="fa fa-trash"
                        aria-hidden="true"
                      />
                    </button>
                  </span>
                </div>
              </div>
            </template>
          </span>
          <hr />
        </div>
        <div
          class="btn-group"
          role="group"
        >
          <div
            class="btn-group"
            role="group"
          >
            <button
              class="btn btn-link"
              @click="toggleAttachmentAdding(true)"
              v-if="permission === 'write' && isfilesAttachmentsLoaded"
            >
              <i
                class="fa fa-plus-circle"
                aria-hidden="true"
              />
              {{ $i18n.t(`featureManager.addAttachment`) }}
            </button>
          </div>
        </div>
      </span>
      <!-- Koniec załączników publicznych -->

      <!-- Początek załączników plikowych -->
      <span v-else>
        <div
          class="pt-10 pb-10"
          v-if="isfilesAttachmentsLoaded"
        >
          <h4>{{ "Załączniki" }}:</h4>
          <div style="overflow-y: auto; max-height: 50vh">
            <div
              v-if="filesAttachments.length < 1"
              class="empty-sub-panel"
            >
              <i
                class="fa fa-paperclip"
                aria-hidden="true"
              />
              {{ $i18n.t("default.noAttachments") }}
            </div>
            <template
              v-else
              v-for="att in filesAttachments"
            >
              <div
                class="media"
                :key="att.id"
              >
                <div class="media-left">
                  <h3>
                    <i
                      class="fa fa-paperclip"
                      aria-hidden="true"
                    />
                  </h3>
                </div>
                <div class="media-body">
                  <h5 class="media-heading">
                    <span>
                      <input
                        class="mr-5"
                        type="checkbox"
                        id="checkbox"
                        :value="att.id"
                        v-model="checkedIds"
                      />
                      <span
                        class="mr-5"
                        style="cursor:pointer"
                        @click="downloadFileAttachments(att.id.toString())"
                      >{{ att.file_name }}</span>
                      <i
                        class="fa fa-trash"
                        aria-hidden="true"
                        style="cursor:pointer"
                        :title="$i18n.t('featureManager.deleteAttachment')"
                        @click="deleteFileAttachments(att.id)"
                      />
                    </span>
                  </h5>
                  <h6 class="media-heading">
                    <span>{{"Autor: " + att.added_by }}</span>
                  </h6>
                  <h6 class="media-heading">
                    <span>{{"Data: " + (new Date(Date.parse(att.added_at))).toLocaleDateString("pl-PL") }}</span>
                  </h6>
                </div>
              </div>
            </template>
          </div>
        </div>
        <div
          class="loading-overlay pt-10 pb-10"
          style="text-align: center"
          v-else
        >
          <div class="loading-indicator mb-10">
            <h4>{{ $i18n.t("default.loading") }}</h4>
            <i class="fa fa-lg fa-spin fa-spinner" />
          </div>
        </div>

        <div
          class="btn-group btn-group-justified"
          role="group"
        >
          <div
            class="btn-group"
            role="group"
          >
            <button
              class="btn btn-link"
              @click="toggleFileAttachmentAdding(true)"
              v-if="permission === 'write' && isfilesAttachmentsLoaded"
            >
              <i
                class="fa fa-plus-circle"
                aria-hidden="true"
              />
              {{ $i18n.t(`featureManager.addAttachment`) }}
            </button>
          </div>
          <div
            class="btn-group"
            role="group"
          >
            <button
              class="btn btn-link green"
              v-if="permission === 'write' && filesAttachments.length > 0"
              :disabled="checkedIds.length < 1"
              @click="downloadFileAttachments(checkedIds.join(','))"
            >
              <i
                class="fa fa-download"
                aria-hidden="true"
              />
              {{ $i18n.t(`featureManager.checkedDownload`) }}
            </button>
          </div>
          <div
            class="btn-group"
            role="group"
          >
            <button
              class="btn btn-link red"
              v-if="permission === 'write' && filesAttachments.length > 0"
              :disabled="checkedIds.length < 1"
              @click="deleteFileAttachments(checkedIds.join(','))"
            >
              <i
                class="fa fa-trash"
                aria-hidden="true"
              />
              {{ $i18n.t(`featureManager.checkedDelete`) }}
            </button>
          </div>
        </div>
      </span>
      <!-- Koniec załączników plikowych -->
    </div>

    <!-- Modal załączników publicznych -->
    <div
      class="modal-mask"
      v-if="isAttachmentAdding"
    >
      <div class="modal-wrapper">
        <div class="modal-dialog modal-md">
          <div class="modal-content">
            <div class="modal-header">
              <h4 class="modal-title">{{ $i18n.t("featureManager.addAttachmentTitle") }}</h4>
            </div>
            <div class="modal-body">
              <div
                class="form-group d-flex"
                style="flex-direction: column; margin-bottom: 0"
              >
                <div class="full-width pb-10">
                  <label class="control-label col-sm-4">{{ $i18n.t("default.name") }}</label>
                  <div class="col-sm-8">
                    <input
                      class="full-width form-control"
                      type="text"
                      v-model="attachmentName"
                    />
                  </div>
                </div>

                <div class="full-width pb-10">
                  <label
                    class="control-label col-sm-4"
                  >{{ $i18n.t("featureManager.attachmentGroup") }}</label>
                  <div class="col-sm-8">
                    <select
                      class="form-control"
                      v-model="isAttachmentPublic"
                    >
                      <option
                        v-if="usersGroup !== defaultGroup"
                        :value="false"
                      >{{ usersGroup }}</option>
                      <option :value="true">{{ defaultGroup }}</option>
                    </select>
                  </div>
                </div>

                <div class="full-width pb-10">
                  <label
                    class="control-label col-sm-4"
                  >{{ $i18n.t("featureManager.attachmentLink") }}</label>
                  <div class="col-sm-8">
                    <input
                      class="full-width form-control"
                      type="text"
                      v-model="attachmentLink"
                    />
                  </div>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <div
                class="btn-group btn-group-justified"
                role="group"
              >
                <div
                  class="btn-group"
                  role="group"
                >
                  <button
                    type="button"
                    class="btn btn-success"
                    :disabled="!attachmentName || !attachmentLink"
                    @click="addAttachment"
                  >{{ $i18n.t("default.save") }}</button>
                </div>
                <div
                  class="btn-group"
                  role="group"
                >
                  <button
                    type="button"
                    class="btn btn-primary"
                    @click="toggleAttachmentAdding(false)"
                  >{{ $i18n.t("default.cancel") }}</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Modal załączników plikowych -->
    <div
      class="modal-mask"
      v-if="isFileAttachmentAdding"
    >
      <div class="modal-wrapper">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h4 class="modal-title">{{ $i18n.t("featureManager.addAttachmentTitle") }}</h4>
            </div>
            <div class="modal-body">
              <div class="pt-10">
                <file-upload
                  ref="upload"
                  v-model="files"
                  :multiple="true"
                  :drop="true"
                  :drop-directory="true"
                  @input-filter="fileFilter"
                >
                  {{this.$i18n.t('upload.defaultMessage')}}
                  <ul>
                    <li
                      v-for="(file,idx) in files"
                      :key="idx"
                    >
                      {{file.name}}
                      <i
                        class="icon-li fa fa-times fa-lg ml-5 delete-file-icon"
                        @click.stop="removeFile(file)"
                      />
                    </li>
                  </ul>
                </file-upload>
              </div>
            </div>
            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-default"
                data-dismiss="modal"
                @click="clearUploadFiles"
                ref="closeModalBtn"
              >{{ $i18n.t('default.cancel') }}</button>
              <button
                type="button"
                class="btn btn-success"
                @click="sendFiles"
                :disabled="files.length < 1"
              >{{ $i18n.t('default.save') }}</button>
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
  data: () => ({
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
    postAction: `${
      vm.$store.getters.getApiUrl
    }/attachments_qgis?token=${localStorage.getItem('token')}`
    // usersGroup: undefined,
  }),
  computed: {
    defaultGroup() {
      return this.$store.getters.getDefaultGroup;
    },
    featureAttachments() {
      if (!this.$store.getters.getFeatureAttachments[this.lid][this.fid]) {
        return [];
      }
      return this.$store.getters.getFeatureAttachments[this.lid][this.fid];
    },
    isRdos() {
      return this.$store.getters.getIsRdos;
    },
    user() {
      return this.$store.getters.getUser;
    },
    usersWithGroups() {
      return this.$store.getters.getUsersWithGroups;
    }
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
        name
          ? link.setAttribute('download', name)
          : link.setAttribute('download', `${ids}.zip`);
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
          this.attachmentsIds.replaceAll(';', ',')
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
      let ext = newFile.name.substr(newFile.name.lastIndexOf('.'));
      if (newFile && !oldFile) {
        for (file of this.files) {
          if (newFile.name === file.name && newFile.size === file.size) {
            this.$alertify.error(this.$i18n.t('upload.uploadDuplicate'));
            return prevent();
          }
        }
      }
    },
    getBase64(file, onLoadCallback) {
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
      for (file of this.files) {
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
              vm.$alertify.success(vm.$i18n.t('upload.uploadSuccess'));
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
              vm.$alertify.error(vm.$i18n.t('upload.uploadError'));
            }
          })
          .catch(err => {
            if (
              err.response.data.error ===
              'layer does not contain column __attachments'
            ) {
              vm.$alertify.error(vm.$i18n.t('upload.noColumnError'));
            } else {
              vm.$alertify.error(vm.$i18n.t('upload.uploadError'));
            }
          });
      }
    }
  },
  mounted() {
    this.getUsers();
    this.$store.commit('setDefaultGroup', process.env.VUE_APP_DEFAULT_GROUP);
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

<template>
  <div class="attachments-panel right-sub-panel">
    <hr />
    <button
      class="btn btn-link"
      @click="toggleAttachmentAdding(true)"
      v-if="permission === 'write'"
    >
      <i
        class="fa fa-plus-circle"
        aria-hidden="true"
      />
      {{ $i18n.t(`featureManager.addAttachment`) }}
    </button>
    <div v-if="featureAttachments">
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
      <span v-else>
        <template v-for="item in featureAttachments[defaultGroup]">
          <div
            class="media"
            :key="item.link"
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
    </div>
    <div v-if="usersGroup !== 'default'">
      <h4>{{ $i18n.t(`featureManager.attachmentsTitleGroup`) }}{{ usersGroup }}:</h4>
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
          v-for="item in featureAttachments[usersGroup].filter(el => el.group !== defaultGroup)"
        >
          <div
            class="media"
            :key="item.link"
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
    </div>

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
  </div>
</template>

<script>
export default {
  props: {
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
    attachmentName: undefined,
    isAttachmentAdding: false,
    isAttachmentPublic: ''
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
    async getUsers() {
      if (Object.keys(this.usersWithGroups).length > 0) {
        this.usersGroup = this.usersWithGroups[this.user];
      }
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
    toggleAttachmentAdding(vis) {
      this.isAttachmentAdding = vis;

      this.attachmentLink = '';
      this.attachmentName = '';
      this.isAttachmentPublic = '';
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
</style>

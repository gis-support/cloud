<template>
  <div class="attachments-panel right-sub-panel">
    <div v-for="mode in attachmentModes" :key="mode">
      <h4>{{$i18n.t(`featureManager.attachmentsTitle${mode}`)}}:</h4>
      <button class="btn btn-link" @click="toggleAttachmentAdding(true, mode)">
        <i class="fa fa-plus-circle" aria-hidden="true"/>
        {{$i18n.t(`featureManager.addAttachment${mode}`)}}
      </button>
      <div>
        <div v-if="!featureAttachments[lid] || featureAttachments[lid][fid][mode].length === 0"
          class="empty-sub-panel">
          <i class="fa fa-paperclip" aria-hidden="true"/>
          {{$i18n.t('default.noAttachments')}}
        </div>
        <span v-else>
          <template v-for="item in featureAttachments[lid][fid][mode]">
            <div class="media" :key="item.link">
              <div class="media-left">
                <h3><i class="fa fa-paperclip" aria-hidden="true"/></h3>
              </div>
              <div class="media-body">
                <h5 class="media-heading">
                  <a :href="item.link" target="_blank">
                    <span>{{item.name}}</span>
                  </a>
                </h5>
                <span style="opacity:0.4;">
                  <button
                    class="btn btn-link action"
                    :title="$i18n.t('featureManager.deleteLink')"
                    @click="deleteLink(item.url)"
                  >
                    <i class="fa fa-trash" aria-hidden="true"/>
                  </button>
                </span>
              </div>
            </div>
          </template>
        </span>
      </div>
      <hr/>
    </div>

    <div class="modal-mask" v-if="isAttachmentAdding">
      <div class="modal-wrapper">
        <div class="modal-dialog modal-md">
          <div class="modal-content">
            <div class="modal-header">
              <h4 class="modal-title">
                {{$i18n.t('featureManager.addAttachmentTitle')}}
              </h4>
            </div>
            <div class="modal-body">
              <div class="form-group d-flex" style="flex-direction: column; margin-bottom: 0">
                <div class="full-width pb-10">
                  <label class="control-label col-sm-4">{{$i18n.t('default.name')}}</label>
                  <div class="col-sm-8">
                    <input class="full-width form-control"
                    type="text"
                    v-model="attachmentName">
                  </div>
                </div>

                <div class="full-width pb-10">
                  <label class="control-label col-sm-4">
                    {{$i18n.t('featureManager.attachmentType')}}</label>
                  <div class="col-sm-8">
                    <select
                      class="form-control"
                      :value="$i18n.t(`default.${mode}`)"
                      v-model="isAttachmentPublic">
                      <option :value="false">{{$i18n.t('default.private')}}</option>
                      <option :value="true">{{$i18n.t('default.public')}}</option>
                    </select>
                  </div>
                </div>

                <div class="full-width pb-10">
                  <label class="control-label col-sm-4">
                    {{$i18n.t('featureManager.attachmentLink')}}</label>
                  <div class="col-sm-8">
                    <input class="full-width form-control"
                    type="text"
                    v-model="attachmentLink">
                  </div>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <div class="btn-group btn-group-justified" role="group">
                <div class="btn-group" role="group">
                  <button
                    type="button"
                    class="btn btn-success"
                    :disabled="!attachmentName || !attachmentLink"
                    @click="addAttachment"
                  >
                    {{$i18n.t('default.save')}}
                  </button>
                </div>
                <div class="btn-group" role="group">
                  <button type="button"
                    class="btn btn-primary"
                    @click="toggleAttachmentAdding(false)"
                  >
                    {{$i18n.t('default.cancel')}}
                  </button>
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
    },
    fid: {
      type: Number,
    },
  },
  data: () => ({
    addingMode: undefined,
    attachmentLink: undefined,
    attachmentModes: ['public', 'default'],
    attachmentName: undefined,
    isAttachmentAdding: false,
    isAttachmentPublic: false,
  }),
  computed: {
    featureAttachments() {
      return this.$store.getters.getFeatureAttachments;
    },
  },
  methods: {
    async addAttachment() {
      const r = await this.$store.dispatch('addAttachment', {
        lid: this.lid,
        fid: this.fid,
        body: {
          link: this.attachmentLink,
          name: this.attachmentName,
          public: this.isAttachmentPublic,
        },
      });

      if (r.status === 201) {
        this.toggleAttachmentAdding(false);
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    deleteLink(itemUrl) {
      this.$alertify.confirm(this.$i18n.t('featureManager.deleteAttachmentConfirm'), () => {
        const linkIdx = this.items.findIndex(el => el.url === itemUrl);
        this.items.splice(linkIdx, 1);
      }, () => {})
        .set({ title: this.$i18n.t('featureManager.deleteAttachmentHeader') })
        .set({ labels: { ok: this.$i18n.t('default.delete'), cancel: this.$i18n.t('default.cancel') } });
    },
    toggleAttachmentAdding(vis, mode) {
      this.isAttachmentAdding = vis;
      this.addingMode = mode;
    },
  },
};
</script>

<style scoped>
.control-label {
  position: relative;
  top: 8px;
}
</style>

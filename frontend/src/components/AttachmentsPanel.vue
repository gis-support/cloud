<template>
  <div class="attachments-panel right-sub-panel">
    <div v-for="mode in attachmentModes" :key="mode">
      <h4>{{$i18n.t(`featureManager.attachmentsTitle${mode}`)}}:</h4>
      <button class="btn btn-link"><i class="fa fa-plus-circle" aria-hidden="true"/>
        {{$i18n.t(`featureManager.addAttachment${mode}`)}}
      </button>
      <div>
        <div v-if="!featureAttachments[lid]" class="empty-sub-panel">
          <i class="fa fa-paperclip" aria-hidden="true"/>
          {{$i18n.t('default.noAttachments')}}
        </div>
        <span v-else>
          <template v-for="item in featureAttachments[lid][fid][mode]">
            <div class="media" :key="item.url">
              <div class="media-left">
                <h3><i class="fa fa-paperclip" aria-hidden="true"/></h3>
              </div>
              <div class="media-body">
                <h5 class="media-heading">
                  <a target="_blank">
                    <!-- <span>{{item.url}}</span> -->
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
    attachmentModes: ['public', 'default'],
  }),
  computed: {
    featureAttachments() {
      return this.$store.getters.getFeatureAttachments;
    },
  },
  methods: {
    deleteLink(itemUrl) {
      this.$alertify.confirm(this.$i18n.t('featureManager.deleteAttachmentConfirm'), () => {
        const linkIdx = this.items.findIndex(el => el.url === itemUrl);
        this.items.splice(linkIdx, 1);
      }, () => {})
        .set({ title: this.$i18n.t('featureManager.deleteAttachmentHeader') })
        .set({ labels: { ok: this.$i18n.t('default.delete'), cancel: this.$i18n.t('default.cancel') } });
    },
  },
};
</script>

<template>
  <div class="comments-panel right-sub-panel">
    <div>
      <h4>{{$i18n.t('featureManager.commentsTitle')}}:</h4>
      <span v-if="!isAddingVisible">
        <button class="btn btn-link" @click="toggleCommentAdding(true, 'add')">
          <i class="fa fa-plus-circle" aria-hidden="true"/>
          {{$i18n.t('featureManager.addComment')}}
        </button>
        <div v-if="isEmpty" class="empty-sub-panel"><i class="fa fa-comment-o" aria-hidden="true"/>
          {{$i18n.t('default.noComments')}}
        </div>
        <div v-else>
          <template v-for="item in comments">
            <div class="media" :key="item.id">
              <div class="media-left">
                <h3><i class="fa fa-comment-o" aria-hidden="true"/></h3>
              </div>
              <div class="media-body">
                <h5 class="media-heading" v-text="item.content"/>
                <span style="opacity:0.4;">
                  <button
                    class="btn btn-link action"
                    @click="toggleCommentAdding(true, 'edit', item)"
                  >
                    <i class="fa fa-pencil" aria-hidden="true"/></button>&nbsp;•&nbsp;
                  <button class="btn btn-link action" @click="deleteComment(item)">
                    <i class="fa fa-trash" aria-hidden="true"/></button>
                </span>
              </div>
            </div>
          </template>
        </div>
      </span>
      <div v-else>
        <div>
          <div class="body">
            <form>
              <div class="form-group">
                <label>Treść komentarza:</label>
                <textarea class="form-control" rows="5" v-model="currentContent"></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <div class="btn-group btn-group-justified" role="group">
              <div class="btn-group" role="group">
                <button type="button" class="btn btn-success"
                  :disabled="currentContent.length == 0"
                  @click="addComment"
                  v-if="addingMode === 'add'"
                >{{$i18n.t('default.save')}}</button>
                <button type="button" class="btn btn-success"
                  :disabled="currentContent.length == 0"
                  @click="editComment"
                  v-else
                >{{$i18n.t('default.save')}}</button>
              </div>
              <div class="btn-group" role="group">
                <button
                  type="button"
                  class="btn btn-default"
                   @click="toggleCommentAdding(false)"
                >{{$i18n.t('default.cancel')}}</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <hr/>
    </div>
  </div>
</template>

<script>
export default {
  data: () => ({
    addingMode: '',
    comments: [
      { id: 1, content: 'Pierwszy komentarz' },
      { id: 2, content: 'Drugi komentarz' },
    ],
    currentContent: '',
    isAddingVisible: false,
  }),
  computed: {
    isEmpty() {
      return this.comments.length < 1;
    },
  },
  methods: {
    addComment() {
      // adding request
      this.comments.push({
        id: this.comments.length + 1,
        content: this.currentContent,
      });
      this.toggleCommentAdding(false);
    },
    deleteComment(item) {
      // deleting request
      this.$alertify.confirm(this.$i18n.t('featureManager.deleteCommentConfirm'), () => {
        const commentIdx = this.comments.findIndex(el => el.id === item.id);
        this.comments.splice(commentIdx, 1);
      }, () => {})
        .set({ title: this.$i18n.t('featureManager.deleteCommentHeader') })
        .set({ labels: { ok: this.$i18n.t('default.delete'), cancel: this.$i18n.t('default.cancel') } });
    },
    editComment() {
      // editing request
      this.toggleCommentAdding(false);
    },
    toggleCommentAdding(vis, mode, item) {
      this.isAddingVisible = vis;
      this.addingMode = mode;
      this.currentContent = (mode === 'edit') ? item.content : '';
    },
  },
};
</script>

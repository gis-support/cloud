<template>
  <div class="col-sm-12 pl-0 pr-0 section">
    <h2 class="flex-center container__border--bottom container__border--grey mb-0">
      <div class="p-0 container__border--bottom container__border--red section__header">
        <span data-i18n="dashboard.title">{{ $i18n.t('settings.tagsList') }}</span>
      </div>
    </h2>

    <div class="col-sm-7 section__content heading-block heading-block-main pt-10 d-flex pl-0 pr-0">
      <table id="permissions-table" class="table table-striped table-bordered table-hover">
        <thead>
          <tr role="row">
            <th v-for="column of columns" :key="column" class="text-center">
              <p class="text-vertical align-center">
                {{ $i18n.t(`settings.tagsTable.${column}`) }}
              </p>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(tag, index) of tags" :key="tag.id" role="row">
            <td
              v-for="column of filteredColumns"
              :key="`${tag.id}_${column}`"
              style="max-width: 300px;"
              class="text-center"
            >
              <div class="text-overflow" :title="tag[column]" v-text="tag[column]"></div>
            </td>
            <td :key="`${tag.id}_color`" style="max-width: 100px;" class="text-center">
              <span class="dot" :title="tag.color" :style="{ backgroundColor: tag.color }"></span>
            </td>
            <td :key="`${tag.id}_actions`" class="text-center">
              <i
                class="fa fa-pencil fa-lg yellow icon-hover"
                :title="$i18n.t('default.edit')"
                @click="editTag(tag, index)"
              />
              <i
                class="fa fa-trash fa-lg red icon-hover"
                :title="$i18n.t('default.delete')"
                @click="deleteTag(index, tag.id)"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="col-sm-4 pl-0 pr-0 pt-10 section form__wrapper">
      <h4 class="flex-center container__border--bottom container__border--grey mb-0 py-5">
        <div class="p-0 section__header">
          <span
            data-i18n="dashboard.title"
            v-text="editing ? $i18n.t('settings.editTag') : $i18n.t('settings.newTag')"
          ></span>
        </div>
      </h4>
      <form class="form-inline">
        <div class="form-group">
          <div class="form__row form__row--name row py-5">
            <label class="col-sm-2">{{ $i18n.t('settings.tagName') }}</label>
            <div class="col-sm-10">
              <input v-model="tag.name" style="width: 100%" class="form-control" />
            </div>
          </div>
          <div class="form__row--color form__row row py-5">
            <label class="col-sm-2">{{ $i18n.t('settings.tagColor') }}</label>
            <div class="col-sm-10">
              <ColorPicker v-model="tag.color"></ColorPicker>
            </div>
          </div>
        </div>
        <button
          :disabled="!isValidTagName"
          class="btn btn-default"
          @click.prevent="editing ? saveEditing() : saveTag()"
        >
          {{ $i18n.t('settings.saveTag') }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import ColorPicker from '@/components/ColorPicker';

export default {
  name: 'Tags',
  components: {
    ColorPicker
  },
  data: () => ({
    editing: false,
    tag: {
      name: '',
      color: 'rgba(0,0,0,1)'
    },
    tags: [],
    columns: ['id', 'name', 'color', 'actions']
  }),
  computed: {
    filteredColumns() {
      return this.columns.filter(col => col !== 'actions' && col !== 'color');
    },
    isValidTagName() {
      return this.tag.name.length > 0;
    }
  },
  created() {
    this.getTags();
  },
  methods: {
    editTag(tag) {
      this.editing = true;
      this.tag = { ...tag };
    },
    async saveEditing() {
      await this.$store.dispatch('editTag', {
        body: this.tag,
        tag_id: this.tag.id
      });
      this.tags[this.tags.map(tag => tag.id).indexOf(this.tag.id)] = this.tag;
      this.tag = { name: '', color: 'rgba(0,0,0,1)' };
      this.editing = false;
    },
    async saveTag() {
      const r = await this.$store.dispatch('addTag', this.tag);
      this.tags.push(Object.assign(this.tag, { id: r.body.data }));
      this.tag = { name: '', color: 'rgba(0,0,0,1)' };
    },
    async deleteTag(index, id) {
      this.$alertify
        .confirm(
          this.$i18n.t('settings.deleteTagConfirm'),
          async () => {
            const r = await this.$store.dispatch('deleteTag', id);
            if (r.status === 204) {
              this.$alertify.success(this.$i18n.t('default.deleted'));
              this.tags.splice(index, 1);
            } else {
              this.$alertify.error(this.$i18n.t('settings.deleteTagError'));
            }
          },
          () => {}
        )
        .set({ title: this.$i18n.t('settings.deleteTagTitle') })
        .set({
          labels: {
            ok: this.$i18n.t('default.delete'),
            cancel: this.$i18n.t('default.cancel')
          }
        });
    },
    async getTags() {
      const r = await this.$store.dispatch('getTags');
      this.tags = r.body.data;
    }
  }
};
</script>

<style scoped>
.form__row {
  display: flex;
  align-items: center;
}
.form__wrapper {
  float: right;
}
.heading-block:after {
  content: unset;
}
.dot {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  display: inline-block;
}
.text-overflow {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

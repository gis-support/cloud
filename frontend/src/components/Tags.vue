<template>
  <div class="col-sm-12 pl-0 pr-0 section">
    <h2 class="flex-center container__border--bottom container__border--grey mb-0">
      <div class="p-0 container__border--bottom container__border--red section__header">
        <span data-i18n="dashboard.title">{{$i18n.t('settings.tagsList')}}</span>
      </div>
    </h2>

    <div class="col-sm-7 section__content heading-block heading-block-main pt-10 d-flex pl-0 pr-0">
      <table
        class="table table-striped table-bordered table-hover"
        id="permissions-table"
      >
        <thead>
          <tr role="row">
            <th
              class="text-center"
              v-for="column of columns"
              :key="column"
            >
              <p class="text-vertical align-center">{{ $i18n.t(`settings.tagsTable.${column}`) }}</p>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            role="row"
            v-for="(tag, index) of tags"
            :key="tag.id"
          >
            <td
              class="text-center"
              v-for="column of filteredColumns"
              :key="`${tag.id}_${column}`"
            >{{tag[column]}}</td>
            <td
              class="text-center"
              :key="`${tag.id}_color`"
            >
              <span
                class="dot"
                :style="{backgroundColor: tag.color}"
              ></span>
            </td>
            <td
              class="text-center"
              :key="`${tag.id}_actions`"
            >
              <i
                class="fa fa-pencil fa-lg yellow icon-hover"
                :title="$i18n.t('default.edit')"
                @click="editTag(tag, index)"
              />
              <i
                class="fa fa-trash fa-lg red icon-hover"
                :title="$i18n.t('default.delete')"
                @click="deleteTag(index)"
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
              <input
                style="width: 100%"
                class="form-control"
                v-model="tag.tag"
              />
            </div>
          </div>
          <div class="form__row--color form__row row py-5">
            <label class="col-sm-2">{{ $i18n.t('settings.tagColor') }}</label>
            <div class="col-sm-10">
              <verte
                picker="square"
                model="rgb"
                :value="tag.color"
                v-model="tag.color"
              />
            </div>
          </div>
        </div>
        <button
          @click.prevent="editing ? saveEditing() : saveTag()"
          class="btn btn-default"
        >{{ $i18n.t('settings.saveTag') }}</button>
      </form>
    </div>
  </div>
</template>

<script>
import verte from 'verte';
import 'verte/dist/verte.css';

export default {
  name: 'Tags',
  components: {
    verte
  },
  data: () => ({
    editing: false,
    tag: {
      tag: '',
      color: 'rgb(0,0,0)'
    },
    tags: [],
    columns: ['id', 'tag', 'color', 'actions']
  }),
  computed: {
    filteredColumns() {
      return this.columns.filter(col => col !== 'actions' && col !== 'color');
    }
  },
  methods: {
    editTag(tag) {
      this.editing = true;
      this.tag = { ...tag };
    },
    saveEditing() {
      this.tags[this.tags.map(tag => tag.id).indexOf(this.tag.id)] = this.tag;
      this.tag = { name: '', color: '' };
      this.editing = false;
    },
    saveTag() {
      this.tags.push(
        Object.assign(this.tag, { id: Math.ceil(Math.random() * 10) })
      );
      this.tag = { name: '', color: 'rgb(0,0,0)' };
    },
    deleteTag(index) {
      this.tags.splice(index, 1);
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
</style>
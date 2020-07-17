<template>
  <div class="col-sm-4 col-sm-push-8 layout-sidebar projects-panel">
    <div
      v-if="projects.length < 1"
      style="font-weight: 600"
    >{{"Brak projektów"}}</div>
    <div
      v-else
      v-for="(project, idx) in projects"
      :key="idx"
      class="well well-sm project-element flex-center"
      @click="openProject(project)"
    >
      <span class="project-text">{{project.name}}</span>
      <span
        id="layers-list-icons"
        class="panel-title__tools"
      >
        <i
          class="fa fa-trash fa-lg red icon-hover"
          :title="$i18n.t('default.delete')"
          @click="deleteProject(project.id)"
        />
      </span>
    </div>
  </div>
</template>
<script>
export default {
  name: 'ProjectsPanel',
  props: {
    projects: {
      required: true,
      type: Array
    }
  },
  methods: {
    deleteProject(pid) {
      this.$alertify
        .confirm(
          this.$i18n.t('dashboard.modal.deleteProjectContent'),
          async () => {
            const r = await this.$store.dispatch('deleteProject', pid);
            if (r.status === 204) {
              this.$emit('deleteProject', pid);
              this.$alertify.success(this.$i18n.t('default.deleted'));
            } else {
              this.$alertify.error(this.$i18n.t('default.error'));
            }
          },
          () => {}
        )
        .set({ title: this.$i18n.t('dashboard.modal.deleteProjectTitle') })
        .set({
          labels: {
            ok: this.$i18n.t('default.delete'),
            cancel: this.$i18n.t('default.cancel')
          }
        });
    },
    openProject(project) {
      this.$router.push({
        name: 'feature_manager',
        query: {
          projectId: project.id
        }
      });
    }
  }
};
</script>
<style scoped>
.project-element {
  margin-bottom: 5px;
}
.projects-panel {
  min-height: calc(100vh - 56px);
}
.project-text {
  font-weight: 600;
  cursor: pointer;
}
</style> 
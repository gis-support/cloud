<template>
  <div class="col-sm-4 col-sm-push-8 layout-sidebar projects-panel">
    <h2 class="flex-center container__border--bottom container__border--grey mb-12">
      <div class="p-0 container__border--bottom container__border--red section__header">
        <i class="fa fa-database" />
        <span data-i18n="dashboard.title">{{ $i18n.t('dashboard.title.projectsList') }}</span>
      </div>
    </h2>
    <div v-if="projects.length < 1" style="font-weight: 600">{{ 'Brak projektów' }}</div>
    <div
      v-for="(project, idx) in projects"
      v-else
      :key="idx"
      :class="{
        'project-disabled': !project.permission_to_active_layer,
        'project-enabled': project.permission_to_active_layer
      }"
      :title="
        project.permission_to_active_layer ? project.name : $i18n.t('default.mainLayerAccessDenied')
      "
      class="well well-sm project-element flex-center"
      @click="project.permission_to_active_layer ? openProject(project) : ''"
    >
      <span
        style="overflow:hidden"
        class="project-text"
        :class="{ 'project-title-disabled': !project.permission_to_active_layer }"
        @click="project.permission_to_active_layer ? openProject(project) : ''"
        >{{ project.name }}</span
      >
      <span id="layers-list-icons" class="panel-title__tools">
        <i
          class="fa fa-trash fa-lg red icon-hover"
          :title="$i18n.t('default.delete')"
          @click.stop="deleteProject(project.id)"
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
        name: 'project_manager',
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
  border-left: 0;
  box-shadow: none;
}
.project-text {
  font-weight: 600;
  cursor: pointer;
}
.section__header {
  padding-bottom: 15px;
  margin-bottom: -1px;
}
.project-disabled {
  cursor: not-allowed;
  border: solid 1px rgba(207, 26, 26, 0.5);
}
.project-title-disabled {
  cursor: not-allowed;
}
.project-enabled {
  cursor: pointer;
}
</style>

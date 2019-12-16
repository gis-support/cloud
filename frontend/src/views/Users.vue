<template>
  <div class="container align-center">
    <div class="col-sm-12 pl-0 pr-0 section">
      <h2 class="flex-center container__border--bottom container__border--grey mb-0">
        <div class="p-0 container__border--bottom container__border--red section__header">
          <i class="fa fa-user-plus"></i>
          <span data-i18n="dashboard.title"> {{$i18n.t('users.title.addUser')}}</span>
        </div>
      </h2>
      <div class="section__content heading-block heading-block-main pt-10" style="display: flex;">
        <input type="text" class="form-control container__input mr-5" v-model="email"
          :placeholder="$i18n.t('default.email')">
        <input type="password" class="form-control container__input mr-5" v-model="password"
          :placeholder="$i18n.t('default.password')">
        <button type="button" class="btn btn-success" @click="addNewUser">
          {{$i18n.t('default.add')}}
        </button>
      </div>
    </div>
    <div class="col-sm-12 pl-0 pr-0 section">
      <h2 class="flex-center container__border--bottom container__border--grey mb-0">
        <div class="p-0 container__border--bottom container__border--red section__header">
          <i class="fa fa-lock"></i>
          <span data-i18n="dashboard.title"> {{$i18n.t('users.title.permissions')}}</span>
        </div>
      </h2>
      <div class="section__content heading-block heading-block-main pt-10 d-flex">
        <table class="table table-striped table-bordered table-hover" id="permissions-table">
          <thead>
            <tr role="row">
              <div>
                <div class="legend-square legend-edit"></div>
                <div class="legend-square legend-read"></div>
                <div class="legend-square legend-noaccess"></div>
              </div>
              <th
                v-for="perm of permissions"
                :key="perm.id"
              >
                <p class="text-vertical full-width d-flex align-center">
                  <i class="fa fa-map-o fa-lg"
                  style="transform: rotate(90deg); padding-top: 5px; padding-right: 10px"></i>
                  {{perm.name}}
                </p>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr role="row" v-for="user of users" :key="user">
              <td class="text-centered">{{user}}</td>
              <td
                class="text-centered"
                v-for="perm of permissions"
                :style="{'background': mapPermissionColors[perm.users[user]]}"
                :key="perm.id"
              >
                <i class="fa handler"
                  :class="perm.users[user] == 'write' ? 'fa-pencil' :
                    (perm.users[user] == 'read' ? 'fa-eye' : 'fa-times')"
                  data-toggle="modal"
                  data-target="#permissionsModal"
                  :title="$i18n.t('users.modal.changePermissions')"
                  @click="saveCurrentPermissions(perm.users[user], perm.id, user)"
                ></i>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!--MODAL UPRAWNIEŃ-->
    <div class="modal fade" data-backdrop="static" id="permissionsModal" tabindex="-1" role="dialog"
      aria-hidden="true" ref="permissionsModal">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">{{$i18n.t('users.modal.changePermissions')}}</h4>
          </div>
          <div class="modal-body" style="display: flex">
            <label class="control-label col-sm-4">{{$i18n.t('users.modal.permissionType')}}</label>
            <select class="form-control mr-5" name="column-types-select"
              v-model="currentPermissions.permission">
              <option value="write">{{$i18n.t('default.edit')}}</option>
              <option value="read">{{$i18n.t('default.read')}}</option>
              <option value="">{{$i18n.t('default.noAccess')}}</option>
            </select>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default" ref="closeModalBtn" data-dismiss="modal">
              {{$i18n.t('default.cancel')}}
            </button>
            <button type="button" class="btn btn-success" @click="editPermissions">
              {{$i18n.t('default.save')}}
            </button>
          </div>
        </div>
      </div>
    </div>
    <!--KONIEC MODALA-->
  </div>
</template>

<script>
export default {
  data: () => ({
    currentPermissions: {},
    email: undefined,
    mapPermissionColors: {
      write: '#48B343',
      read: '#F9A122',
      '': '#EC3C36',
    },
    password: undefined,
    permissions: undefined,
    users: undefined,
  }),
  methods: {
    async addNewUser() {
      if (!this.email || !this.password) {
        this.$alertify.error(this.$i18n.t('users.responses.noEmailOrPassword'));
        return;
      }
      const payload = { user: this.email, password: this.password };
      const r = await this.$store.dispatch('register', payload);
      if (r.status === 201) {
        this.$alertify.success(this.$i18n.t('users.responses.userCreated'));
        this.getPermissions(); // update permissions table
        this.email = undefined;
        this.password = undefined;
      } else if (r.status === 409) {
        this.$alertify.error(this.$i18n.t('users.responses.userExists'));
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    async editPermissions() {
      const payload = {
        lid: this.currentPermissions.layId,
        body: {
          permission: this.currentPermissions.permission,
          user: this.currentPermissions.username,
        },
      };

      const r = await this.$store.dispatch('editPermissions', payload);
      if (r.status === 200) {
        this.$alertify.success(this.$i18n.t('users.responses.permissionsChanged'));
        const layer = this.permissions.find(el => el.id === this.currentPermissions.layId);
        this.$set(layer.users, r.obj.permissions.user, r.obj.permissions.permission);
        this.$refs.closeModalBtn.click();
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    async getPermissions() {
      const r = await this.$store.dispatch('getPermissions');
      this.permissions = r.obj.permissions;
      this.users = r.obj.users;
    },
    saveCurrentPermissions(permission, layerId, username) {
      this.$set(this.currentPermissions, 'permission', permission);
      this.$set(this.currentPermissions, 'layId', layerId);
      this.$set(this.currentPermissions, 'username', username);
    },
  },
  mounted() {
    this.getPermissions();
  },
};
</script>

<style scoped>
.btn-upload {
  margin-right: 20px;
}
.container {
  top: 20px;
}
.container__input {
  width: 300px;
}
.control-label {
  line-height: 29px;
  font-size: 12px;
}
.container {
  height: calc(100% - 76px);
  padding-left: 0px;
  padding-right: 0px;
}
.desc-sm {
  color: #b5b5b5;
  font-family: "Open Sans","Trebuchet MS",arial,sans-serif;
  font-size: 12px;
  letter-spacing: -1px;
  line-height: 1.75em;
  margin-left: 5px;
}
.files-list li {
  width: 120px;
  list-style: none;
}
.handler:hover {
  cursor: pointer;
}
.heading-block:after, .heading-block:before {
  display: none;
}
.legend-edit {
  background: #48B343;
  margin: 5px;
}
.legend-edit::after {
  content: "- Edycja";
  display: block;
  margin-left: 25px;
  width: 200px;
}
.legend-noaccess {
  background: #EC3C36;
  margin: 5px;
}
.legend-noaccess::after {
  content: "- Brak dostępu";
  display: block;
  margin-left: 25px;
  width: 200px;
}
.legend-read {
  background: #F9A122;
  margin: 5px;
}
.legend-read::after {
  content: "- Podgląd";
  display: block;
  margin-left: 25px;
  width: 200px;
}
.legend-square {
  height: 20px;
  width: 20px;
}
.loading-overlay {
  width: 100%;
  text-align: center;
}
.panel-title__names {
  font-size: 14px;
}
.panel-title__tools i:not(:last-child) {
  margin-right: 5px;
}
#permissions-table {
  max-width: calc(100% - 1px);
}
.section__content.heading-block.heading-block-main {
  overflow-y: auto;
  max-height: calc(100% - 50px);
}
.section__header {
  padding-bottom: 15px;
  margin-bottom: -1px;
}
.text-centered {
  text-align: center;
}
.text-vertical {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  transform: rotate(180deg);
}
.text-left {
  text-align: left;
}
</style>

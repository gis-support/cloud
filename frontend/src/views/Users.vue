<template>
  <div class="container align-center">
    <div class="col-sm-12 pl-0 pr-0 section">
      <h2 class="flex-center container__border--bottom container__border--grey mb-0">
        <div class="p-0 container__border--bottom container__border--red section__header">
          <i class="fa fa-user-plus" />
          <span data-i18n="dashboard.title">{{ $i18n.t('users.title.addUser') }}</span>
        </div>
      </h2>
      <div
        class="section__content heading-block heading-block-main pt-10"
        style="display: flex;"
      >
        <input
          type="text"
          class="form-control container__input mr-5"
          v-model="username"
          :placeholder="$i18n.t('default.username')"
        />
        <input
          type="password"
          class="form-control container__input mr-5"
          v-model="password"
          :placeholder="$i18n.t('default.password')"
        />
        <select
          class="form-control mr-5"
          style="width: 300px"
          v-model="newUserGroup"
        >
          <option
            value="undefined"
            disabled
            hidden
          >{{ $i18n.t('default.groupName') }}</option>
          <option
            v-for="group in groups"
            v-text="group"
            :key="`${group}_assign_user`"
            :value="group"
          />
        </select>
        <button
          type="button"
          class="btn btn-success"
          @click="addNewUser"
          :disabled="!username || !password"
        >{{ $i18n.t('default.add') }}</button>
      </div>
    </div>
    <div class="col-sm-12 pl-0 pr-0 section">
      <h2 class="flex-center container__border--bottom container__border--grey mb-0">
        <div class="p-0 container__border--bottom container__border--red section__header">
          <i class="fa fa-lock" />
          <span data-i18n="dashboard.title">{{ $i18n.t('users.title.permissions') }}</span>
        </div>
      </h2>
      <div class="section__content heading-block heading-block-main pt-10 d-flex">
        <table
          class="table table-striped table-bordered table-hover"
          id="permissions-table"
        >
          <thead>
            <tr role="row">
              <div id="perms-legend">
                <div class="legend-square legend-edit" />
                <div class="legend-square legend-read" />
                <div class="legend-square legend-noaccess" />
              </div>
              <th
                v-for="perm of permissions"
                :key="perm.id"
              >
                <p class="text-vertical full-width d-flex align-center">
                  <i
                    class="fa fa-map-o fa-lg"
                    style="transform: rotate(90deg); padding-top: 5px; padding-right: 10px"
                  />
                  {{ perm.name }}
                </p>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              role="row"
              v-for="user of usersPerm"
              :key="user"
            >
              <td class="text-centered">
                <i
                  v-if="user != 'admin'"
                  class="fa fa-trash"
                  @click="deleteUser(user)"
                />
                {{ user }}
              </td>
              <td
                class="text-centered"
                v-for="perm of permissions"
                :style="{'background': mapPermissionColors[perm.users[user]]}"
                :key="perm.id"
              >
                <i
                  class="fa handler"
                  :class="perm.users[user] == 'write' ? 'fa-pencil' :
                    (perm.users[user] == 'read' ? 'fa-eye' : 'fa-times')"
                  data-toggle="modal"
                  data-target="#permissionsModal"
                  :title="$i18n.t('users.modal.changePermissions')"
                  @click="saveCurrentPermissions(perm.users[user], perm.id, user)"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="col-sm-12 pl-0 pr-0 section">
      <h2 class="flex-center container__border--bottom container__border--grey">
        <div class="p-0 container__border--bottom container__border--red section__header">
          <i class="fa fa-group" />
          <span>{{ $i18n.t('users.title.groups') }}</span>
        </div>
      </h2>
      <div class="section__content heading-block heading-block-main pt-10">
        <span class="col-sm-12 pl-0">
          <h4 class="flex-center mb-0">
            <div class="p-0 container__border--bottom container__border--red section__header">
              <span>{{ $i18n.t('users.title.assignUser') }}</span>
            </div>
          </h4>
          <span style="display: flex;">
            <select
              class="form-control mr-5"
              style="width: 300px"
              v-model="userToAssign"
            >
              <option
                value="undefined"
                disabled
                hidden
              >{{ $i18n.t('default.username') }}</option>
              <option
                v-for="user in users"
                v-text="user"
                :key="`${user}_assign`"
                :value="user"
              />
            </select>
            <select
              class="form-control mr-5"
              style="width: 300px"
              v-model="groupToAssign"
            >
              <option
                value="undefined"
                disabled
                hidden
              >{{ $i18n.t('default.groupName') }}</option>
              <option
                v-for="group in groups"
                v-text="group"
                :key="`${group}_assign`"
                :value="group"
              />
            </select>
            <button
              type="button"
              class="btn btn-success"
              :disabled="!groupToAssign || !userToAssign"
              @click="assignUser"
            >{{ $i18n.t('users.assignUser') }}</button>
          </span>
          <p v-if="userToAssign">Obecna grupa: {{ usersWithGroups[userToAssign] }}</p>
        </span>
      </div>
      <div class="section__content heading-block heading-block-main pt-10">
        <span class="col-sm-6 pl-0">
          <h4 class="flex-center mb-0">
            <div class="p-0 container__border--bottom container__border--red section__header">
              <span>{{ $i18n.t('users.title.groupAdd') }}</span>
            </div>
          </h4>
          <span style="display: flex;">
            <input
              type="text"
              class="form-control container__input mr-5"
              :placeholder="$i18n.t('default.groupName')"
              v-model="newGroupName"
            />
            <button
              type="button"
              class="btn btn-success"
              @click="addGroup"
              :disabled="!newGroupName"
            >{{ $i18n.t('default.add') }}</button>
          </span>
        </span>
        <span class="col-sm-6 pl-0">
          <h4 class="flex-center mb-0">
            <div class="p-0 container__border--bottom container__border--red section__header">
              <span>{{ $i18n.t('users.title.groupDelete') }}</span>
            </div>
          </h4>
          <span style="display: flex;">
            <select
              class="form-control mr-5"
              style="width: 300px"
              v-model="usersGroup"
            >
              <option
                value="undefined"
                disabled
                hidden
              >{{ $i18n.t('users.title.chooseGroupToDelete') }}</option>
              <option
                v-for="group in groups"
                v-text="group"
                :key="group"
                :value="group"
              />
            </select>
            <button
              type="button"
              class="btn btn-primary"
              :disabled="!usersGroup"
              @click="deleteGroup"
            >{{ $i18n.t('default.delete') }}</button>
          </span>
        </span>
      </div>
    </div>

    <!--MODAL UPRAWNIEŃ-->
    <div
      class="modal fade"
      data-backdrop="static"
      id="permissionsModal"
      tabindex="-1"
      role="dialog"
      aria-hidden="true"
      ref="permissionsModal"
    >
      <div
        class="modal-dialog modal-dialog-centered"
        role="document"
      >
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">{{ $i18n.t('users.modal.changePermissions') }}</h4>
          </div>
          <div
            class="modal-body"
            style="display: flex"
          >
            <label class="control-label col-sm-4">{{ $i18n.t('users.modal.permissionType') }}</label>
            <select
              class="form-control mr-5"
              name="column-types-select"
              v-model="currentPermissions.permission"
            >
              <option value="write">{{ $i18n.t('default.edit') }}</option>
              <option value="read">{{ $i18n.t('default.read') }}</option>
              <option value>{{ $i18n.t('default.noAccess') }}</option>
            </select>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-default"
              ref="closeModalBtn"
              data-dismiss="modal"
            >{{ $i18n.t('default.cancel') }}</button>
            <button
              type="button"
              class="btn btn-success"
              @click="editPermissions"
            >{{ $i18n.t('default.save') }}</button>
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
    username: undefined,
    groups: [],
    groupToAssign: undefined,
    mapPermissionColors: {
      write: '#48B343',
      read: '#F9A122',
      '': '#EC3C36'
    },
    newGroupName: undefined,
    newUserGroup: undefined,
    password: undefined,
    permissions: undefined,
    users: undefined,
    usersGroup: undefined,
    usersPerm: [],
    userToAssign: undefined
  }),
  computed: {
    defaultGroup() {
      return this.$store.getters.getDefaultGroup;
    },
    usersWithGroups() {
      return this.$store.getters.getUsersWithGroups;
    }
  },
  methods: {
    async addGroup() {
      const r = await this.$store.dispatch('addGroup', {
        group: this.newGroupName
      });
      if (r.status === 201) {
        this.$alertify.success(this.$i18n.t('default.newGroupAdded'));
        this.groups.push(this.newGroupName);
        this.newGroupName = '';
      } else if (r.status === 400) {
        this.$alertify.error(this.$i18n.t('users.responses.groupExists'));
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    async addNewUser() {
      const payload = {
        user: this.username,
        password: this.password,
        group: this.newUserGroup
      };
      if (!this.newUserGroup) {
        delete payload.group;
      }
      const r = await this.$store.dispatch('register', payload);
      if (r.status === 201) {
        this.$alertify.success(this.$i18n.t('users.responses.userCreated'));
        this.getPermissions(); // update permissions table
        this.getUsers();
        this.username = undefined;
        this.password = undefined;
        this.newUserGroup = undefined;
      } else if (r.status === 409) {
        this.$alertify.error(this.$i18n.t('users.responses.userExists'));
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    async assignUser() {
      this.$alertify
        .confirm(
          this.$i18n.t('users.assignUserConfirm'),
          async () => {
            const r = await this.$store.dispatch('assignUserToGroup', {
              group: this.groupToAssign,
              user: this.userToAssign
            });
            if (r.status === 200) {
              this.$alertify.success(this.$i18n.t('default.success'));
              this.groupToAssign = undefined;
              this.userToAssign = undefined;
            }
          },
          () => {}
        )
        .set({ title: this.$i18n.t('users.title.assignUserTitle') })
        .set({
          labels: {
            ok: this.$i18n.t('default.yes'),
            cancel: this.$i18n.t('default.cancel')
          }
        });
    },
    async deleteGroup() {
      this.$alertify
        .confirm(
          this.$i18n.t('users.deleteGroupConfirm'),
          async () => {
            const r = await this.$store.dispatch('deleteGroup', {
              group: this.usersGroup
            });
            if (r.status === 200) {
              this.$alertify.success(this.$i18n.t('default.deleted'));
              this.usersGroup = undefined;
              const groupIdx = this.groups.findIndex(
                el => el === this.usersGroup
              );
              this.groups.splice(groupIdx, 1);
            } else if (r.status === 400) {
              this.$alertify.error(this.$i18n.t('users.deleteDefaultGroup'));
            }
          },
          () => {}
        )
        .set({ title: this.$i18n.t('users.title.deleteGroupTitle') })
        .set({
          labels: {
            ok: this.$i18n.t('default.delete'),
            cancel: this.$i18n.t('default.cancel')
          }
        });
    },
    async editPermissions() {
      const payload = {
        lid: this.currentPermissions.layId,
        body: {
          permission: this.currentPermissions.permission,
          user: this.currentPermissions.username
        }
      };

      const r = await this.$store.dispatch('editPermissions', payload);
      if (r.status === 200) {
        this.$alertify.success(
          this.$i18n.t('users.responses.permissionsChanged')
        );
        const layer = this.permissions.find(
          el => el.id === this.currentPermissions.layId
        );
        this.$set(
          layer.users,
          r.obj.permissions.user,
          r.obj.permissions.permission
        );
        this.$refs.closeModalBtn.click();
      } else {
        this.$alertify.error(this.$i18n.t('default.error'));
      }
    },
    async deleteUser(user) {
      const payload = {
        user: user
      };
      this.$alertify
        .confirm(
          this.$i18n.t('users.modal.deleteUserContent'),
          async () => {
            const r = await this.$store.dispatch('deleteUser', payload);
            if (r.status === 200) {
              this.users = this.users.filter(u => u !== user);
              this.$alertify.success(this.$i18n.t('default.deleted'));
            } else {
              this.$alertify.error(this.$i18n.t('default.error'));
            }
          },
          () => {}
        )
        .set({ title: this.$i18n.t('users.modal.deleteUserTitle') })
        .set({
          labels: {
            ok: this.$i18n.t('default.delete'),
            cancel: this.$i18n.t('default.cancel')
          }
        });
    },
    async getGroups() {
      const r = await this.$store.dispatch('getGroups');
      this.groups = r.body.groups;
    },
    async getPermissions() {
      const r = await this.$store.dispatch('getPermissions');
      this.permissions = r.obj.permissions;
      this.usersPerm = r.obj.users;
    },
    async getUsers() {
      const r = await this.$store.dispatch('getUsers');
      if (r.status === 200) {
        this.$store.commit('setUsersWithGroups', r.obj.users);
        this.users = Object.keys(r.obj.users);
      }
    },
    saveCurrentPermissions(permission, layerId, username) {
      this.$set(this.currentPermissions, 'permission', permission);
      this.$set(this.currentPermissions, 'layId', layerId);
      this.$set(this.currentPermissions, 'username', username);
    }
  },
  mounted() {
    this.getPermissions();
    this.getGroups();
    this.getUsers();
  }
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
  font-family: 'Open Sans', 'Trebuchet MS', arial, sans-serif;
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
.heading-block:after,
.heading-block:before {
  display: none;
}
.legend-edit {
  background: #48b343;
  margin: 5px;
}
.legend-edit::after {
  content: '- Edycja';
  display: block;
  margin-left: 25px;
  width: 200px;
}
.legend-noaccess {
  background: #ec3c36;
  margin: 5px;
}
.legend-noaccess::after {
  content: '- Brak dostępu';
  display: block;
  margin-left: 25px;
  width: 200px;
}
.legend-read {
  background: #f9a122;
  margin: 5px;
}
.legend-read::after {
  content: '- Podgląd';
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
#perms-legend {
  min-width: 125px;
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

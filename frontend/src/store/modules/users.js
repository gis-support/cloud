import Swagger from "swagger-client";
import api from "@/docs/api.json";

const swagger = new Swagger({
  spec: api,
  requestInterceptor: r => {
    const request = r;
    if (!request.url.includes("https") && process.env.VUE_APP_PROD_HOST_URL != "localhost") {
      request.url = request.url.replace("http", "https");
    }
    if (request.url.includes("/login") || request.url.includes("/register")) {
      return request;
    }
    request.headers.Authorization = localStorage.getItem("token");
    return request;
  }
}).client;

export default {
  state: {
    usersWithGroups: {}
  },
  actions: {
    async addGroup(ctx, payload) {
      try {
        const response = await swagger.apis.Auth.post_api_users_groups({
          body: payload
        });
        return response;
      } catch (err) {
        return err;
      }
    },
    async assignUserToGroup(ctx, payload) {
      try {
        const response = await swagger.apis.Auth.put_api_users({
          body: payload
        });
        return response;
      } catch (err) {
        return err;
      }
    },
    async deleteGroup(ctx, payload) {
      try {
        const response = await swagger.apis.Auth.delete_api_users_groups({
          body: payload
        });
        return response;
      } catch (err) {
        return err;
      }
    },
    async deleteUser(ctx, payload) {
      try {
        const response = await swagger.apis.Auth.delete_api_users({ body: payload });
        return response;
      } catch (err) {
        return err;
      }
    },
    async editPermissions(ctx, payload) {
      try {
        // eslint-disable-next-line no-underscore-dangle
        const response = await swagger.apis.Permissions.put_api_permissions__lid_({
          body: payload.body,
          lid: payload.lid
        });
        return response;
      } catch (err) {
        return err;
      }
    },
    async getGroups() {
      try {
        const response = await swagger.apis.Auth.get_api_users_groups();
        return response;
      } catch (err) {
        return err;
      }
    },
    async getPermissions() {
      try {
        const response = await swagger.apis.Permissions.get_api_permissions();
        return response;
      } catch (err) {
        return err;
      }
    },
    async getUsers() {
      try {
        const response = await swagger.apis.Auth.get_api_users();
        return response;
      } catch (err) {
        return err;
      }
    }
  },
  getters: {
    getUsersWithGroups(state) {
      return state.usersWithGroups;
    }
  },
  mutations: {
    setUsersWithGroups(state, users) {
      state.usersWithGroups = users;
    }
  }
};

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
    tags: []
  },
  actions: {
    async addTag(ctx, payload) {
      try {
        const response = await swagger.apis["Layers tags"].post_api_tags({
          body: payload
        });
        return response;
      } catch (err) {
        return err;
      }
    },
    async getTags(ctx, payload) {
      try {
        const response = await swagger.apis["Layers tags"].get_api_tags();
        return response;
      } catch (err) {
        return err;
      }
    },
    async deleteTag(ctx, id) {
      try {
        const response = await swagger.apis["Layers tags"].delete_api_tags__tag_id_({
          tag_id: id
        });
        return response;
      } catch (err) {
        return err;
      }
    }
  },
  getters: {
    getTags(state) {
      return state["Layers tags"];
    }
  },
  mutations: {
    setTags(state, value) {
      state["Layers tags"] = value;
    }
  }
};

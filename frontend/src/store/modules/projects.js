import Swagger from 'swagger-client';
import api from '@/docs/api.json';

const swagger = new Swagger({
  spec: api,
  requestInterceptor: r => {
    const request = r;
    if (!request.url.includes('https') && process.env.VUE_APP_PROD_HOST_URL != 'localhost') {
      request.url = request.url.replace('http', 'https');
    }
    if (request.url.includes('/login') || request.url.includes('/register')) {
      return request;
    }
    request.headers.Authorization = localStorage.getItem('token');
    return request;
  }
}).client;

export default {
  actions: {
    async deleteProject(ctx, id) {
      try {
        const response = await swagger.apis.Projects.delete_api_projects__project_id_({
          project_id: id
        });
        return response;
      } catch (err) {
        return err;
      }
    },
    async getActiveLayerUsers(ctx, id) {
      try {
        const response = await swagger.apis.Projects.get_api_projects__active_layer_id__users({
          active_layer_id: id
        });
        return response;
      } catch (err) {
        return err;
      }
    },
    async getProject(ctx, id) {
      try {
        const response = await swagger.apis.Projects.get_api_projects__project_id_({
          project_id: id
        });
        return response;
      } catch (err) {
        return err;
      }
    },
    async getProjects() {
      try {
        const response = await swagger.apis.Projects.get_api_projects();
        return response;
      } catch (err) {
        return err;
      }
    },
    async postProject(ctx, payload) {
      try {
        const response = await swagger.apis.Projects.post_api_projects({
          body: payload
        });
        return response;
      } catch (err) {
        return err;
      }
    },
    async putProject(ctx, data) {
      try {
        const response = await swagger.apis.Projects.put_api_projects__project_id_({
          project_id: data.pid,
          body: data.payload
        });
        return response;
      } catch (err) {
        return err;
      }
    }
  }
};

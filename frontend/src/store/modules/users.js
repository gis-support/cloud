import Swagger from 'swagger-client';
import api from '@/docs/api.json';

const swagger = new Swagger({
  spec: api,
  requestInterceptor: (r) => {
    const request = r;
    if (!request.url.includes('https')) {
      request.url = request.url.replace('http', 'https');
    }
    if (request.url.includes('/login') || request.url.includes('/register')) {
      return request;
    }
    request.headers.Authorization = localStorage.getItem('token');
    return request;
  },
}).client;

export default {
  actions: {
    async editPermissions(ctx, payload) {
      try {
        // eslint-disable-next-line no-underscore-dangle
        const response = await swagger.apis.Permissions
          .put_api_permissions__lid_({ body: payload.body, lid: payload.lid });
        return response;
      } catch (err) {
        return err;
      }
    },
    async getPermissions() {
      try {
        const response = await swagger.apis.Permissions
          .get_api_permissions();
        return response;
      } catch (err) {
        return err;
      }
    },
  },
};

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
  state: {
    apiUrl: 'https://cloud.gis.support/api',
  },
  actions: {
    async getLayers() {
      try {
        const response = await swagger.apis.Layers.get_api_layers();
        return response;
      } catch (err) {
        return err.response;
      }
    },
  },
  getters: {
    getApiUrl(state) {
      return state.apiUrl;
    },
  },
};
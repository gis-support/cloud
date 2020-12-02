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
  state: {
    apiUrl:
      process.env.VUE_APP_PROD_HOST_URL == 'localhost'
        ? `http://localhost:5001/api`
        : `https://${process.env.VUE_APP_PROD_HOST_URL}/api`,
    columnTypes: ['character varying', 'real', 'integer', 'timestamp without time zone', 'dict'],
    services: []
  },
  actions: {
    async getLayerMaxNameLength() {
      try {
        const response = await swagger.apis.Layers.get_api_layers_max_name_length();
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async addService(ctx, payload) {
      try {
        const response = await swagger.apis.Services.post_api_services({
          body: payload
        });
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async changeLayer(ctx, payload) {
      try {
        const response = await swagger.apis.Layers.post_api_layers__lid__settings({
          body: payload.body,
          lid: payload.lid
        });
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async deleteColumn(ctx, payload) {
      try {
        const response = await swagger.apis.Layers.delete_api_layers__lid__settings({
          body: payload.body,
          lid: payload.lid
        });
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async deleteLayer(ctx, lid) {
      try {
        // eslint-disable-next-line no-underscore-dangle
        const response = await swagger.apis.Layers.delete_api_layers__lid_({
          lid
        });
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async deleteService(ctx, sid) {
      try {
        // eslint-disable-next-line no-underscore-dangle
        const response = await swagger.apis.Services.delete_api_services__sid_({
          sid
        });
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async getLayer(ctx, lid) {
      try {
        // eslint-disable-next-line no-underscore-dangle
        const response = await swagger.apis.Layers.get_api_layers__lid_({
          lid
        });
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async getLayers() {
      try {
        const response = await swagger.apis.Layers.get_api_layers();
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async getLayerColumns(ctx, lid) {
      try {
        const response = await swagger.apis.Layers.get_api_layers__lid__settings({
          lid
        });
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async getServices() {
      try {
        const response = await swagger.apis.Services.get_api_services();
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async saveStyle(ctx, payload) {
      try {
        const response = await swagger.apis.Layers.put_api_layers__lid__style({
          lid: payload.lid,
          body: payload.body
        });
        return response;
      } catch (err) {
        return err.response;
      }
    }
  },
  mutations: {
    addService(state, service) {
      state.services.push(service);
    },
    deleteService(state, sid) {
      const serviceIdx = state.services.findIndex(el => el.id === sid);
      state.services.splice(serviceIdx, 1);
    },
    setServices(state, service) {
      state.services = service;
    }
  },
  getters: {
    getApiUrl(state) {
      return state.apiUrl;
    },
    getColumnTypes(state) {
      return state.columnTypes;
    },
    getServices(state) {
      return state.services;
    }
  }
};

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
    activeLayer: undefined,
    currentFeaturesTypes: undefined,
    mapCenter: {
      lat: 51.919438,
      lon: 19.145136,
    },
    mapZoom: 6,
  },
  actions: {
    async editFeature(ctx, payload) {
      try {
        // eslint-disable-next-line no-underscore-dangle
        const response = await swagger.apis.Features.put_api_layers__lid__features__fid_({
          body: payload.body,
          lid: payload.lid,
          fid: payload.fid,
        });
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async getCurrentFeatures(ctx, lid) {
      try {
        const response = await swagger.apis.Layers
          .get_api_layers__lid__settings({ lid });
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async getLayerStyle(ctx, lid) {
      try {
        const response = await swagger.apis.Layers
          .get_api_layers__lid__style({ lid });
        return response;
      } catch (err) {
        return err.response;
      }
    },
  },
  getters: {
    getActiveLayer(state) {
      return state.activeLayer;
    },
    getCurrentFeaturesTypes(state) {
      return state.currentFeaturesTypes;
    },
    getMapCenter(state) {
      return state.mapCenter;
    },
    getMapZoom(state) {
      return state.mapZoom;
    },
  },
  mutations: {
    setActiveLayer(state, activeLayer) {
      state.activeLayer = activeLayer;
    },
    setCurrentFeaturesTypes(state, types) {
      state.currentFeaturesTypes = types;
    },
  },
};

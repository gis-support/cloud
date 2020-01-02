/* import Swagger from 'swagger-client';
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
}).client; */

export default {
  state: {
    activeLayer: undefined,
    mapCenter: {
      lat: 51.919438,
      lon: 19.145136,
    },
    mapZoom: 6,
  },
  getters: {
    getActiveLayer(state) {
      return state.activeLayer;
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
  },
};

import Vue from 'vue';
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
    featureAttachments: {},
    mapCenter: {
      lat: 51.919438,
      lon: 19.145136,
    },
    mapZoom: 6,
  },
  actions: {
    async addAttachment(ctx, payload) {
      try {
        const response = await swagger.apis.Attachments
          .post_api_layers__lid__features__fid__attachments({
            body: payload.body,
            lid: payload.lid,
            fid: payload.fid,
          });
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async addFeature(ctx, payload) {
      try {
        // eslint-disable-next-line no-underscore-dangle
        const response = await swagger.apis.Features
          .post_api_layers__lid__features({
            lid: payload.lid,
            body: payload.body,
          });
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async deleteAttachment(ctx, payload) {
      try {
        // eslint-disable-next-line no-underscore-dangle
        const response = await swagger.apis.Attachments
          .delete_api_layers__lid__features__fid__attachments__aid_({
            lid: payload.lid,
            fid: payload.fid,
            aid: payload.aid,
          });
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async deleteFeature(ctx, payload) {
      try {
        // eslint-disable-next-line no-underscore-dangle
        const response = await swagger.apis.Features
          .delete_api_layers__lid__features__fid_({
            lid: payload.lid,
            fid: payload.fid,
          });
        return response;
      } catch (err) {
        return err.response;
      }
    },
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
    async getCurrentSettings(ctx, lid) {
      try {
        const response = await swagger.apis.Layers
          .get_api_layers__lid__settings({ lid });
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async getFeatureAttachments(ctx, payload) {
      try {
        const response = await swagger.apis.Attachments
          .get_api_layers__lid__features__fid__attachments({
            lid: payload.lid,
            fid: payload.fid,
          });
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
    getFeatureAttachments(state) {
      return state.featureAttachments;
    },
    getMapCenter(state) {
      return state.mapCenter;
    },
    getMapZoom(state) {
      return state.mapZoom;
    },
  },
  mutations: {
    addAttachmentToFeature(state, params) {
      const groups = Object.keys(params.attachments);
      groups.forEach((el) => {
        const attachArr = [
          ...state.featureAttachments[params.lid][params.fid][el],
          ...params.attachments[el].filter(att => att.group === el),
        ];
        Vue.set(state.featureAttachments[params.lid][params.fid], el, attachArr);
      });
    },
    deleteFeatureAttachment(state, params) {
      const attachmentIdx = state
        .featureAttachments[params.lid][params.fid][params.attachType]
        .findIndex(el => el.id === params.aid);
      state.featureAttachments[params.lid][params.fid][params.attachType]
        .splice(attachmentIdx, 1);
    },
    setActiveLayer(state, activeLayer) {
      state.activeLayer = activeLayer;
    },
    setAttachmentsFeature(state, params) {
      Vue.set(state.featureAttachments[params.lid], params.fid, { public: [], default: [] });
    },
    setAttachmentsLayer(state, lid) {
      Vue.set(state.featureAttachments, lid, {});
    },
    setCurrentFeaturesTypes(state, types) {
      state.currentFeaturesTypes = types;
    },
  },
};
import Swagger from 'swagger-client';
import api from '@/docs/api.json';

const swagger = new Swagger({
  spec: api,
  requestInterceptor: (r) => {
    const request = r;
    if (!request.url.includes('https')) {
      request.url = request.url.replace('http', 'https');
    }
    if (request.url.includes('/login')) {
      return request;
    }
    request.headers.Authorization = localStorage.getItem('token');
    return request;
  },
}).client;

export default {
  state: {
    defaultGroup: '',
    token: localStorage.getItem('token') === null ? '' : localStorage.getItem('token'),
    user: '',
  },
  mutations: {
    setToken(state, token) {
      state.token = token.slice();
      localStorage.setItem('token', token.slice());
    },
    setUser(state, email) {
      state.user = email;
    },
    logOut(state) {
      state.token = '';
      state.user = '';
      localStorage.removeItem('token');
    },
    setDefaultGroup(state, group) {
      state.defaultGroup = group;
    },
  },
  actions: {
    async checkToken() {
      try {
        const r = await swagger.apis.Auth.get_api_check_token();
        return r;
      } catch (err) {
        return err.response;
      }
    },
    async getUserGroups() {
      try {
        const response = await swagger.apis.Auth.get_api_users_groups();
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async logIn(ctx, payload) {
      try {
        const response = await swagger.apis.Auth.post_api_login({ body: payload });
        const { token } = response.obj;
        ctx.commit('setToken', token);
        ctx.commit('setUser', payload.user);
        return response;
      } catch (err) {
        return err.response;
      }
    },
    async register(ctx, payload) {
      try {
        const response = await swagger.apis.Auth.post_api_users({ body: payload });
        return response;
      } catch (err) {
        return err.response;
      }
    },
  },
  getters: {
    getDefaultGroup(state) {
      return state.defaultGroup;
    },
    getToken() {
      return localStorage.getItem('token');
    },
    getUser(state) {
      return state.user;
    },
  },
};

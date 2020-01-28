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
    token: localStorage.getItem('token') || '',
    user: localStorage.getItem('user') || '',
  },
  mutations: {
    setToken(state, token) {
      state.token = token;
    },
    setUser(state, email) {
      state.user = email;
    },
    logOut(state) {
      state.token = '';
      state.user = '';
    },
    setDefaultGroup(state, group) {
      state.defaultGroup = group;
    },
  },
  actions: {
    async checkToken(ctx) {
      try {
        const r = await swagger.apis.Auth.get_api_check_token();
        ctx.commit('setToken', localStorage.getItem('token'));
        ctx.commit('setUser', localStorage.getItem('user'));
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
        localStorage.setItem('token', token);
        localStorage.setItem('user', payload.user);
        return response;
      } catch (err) {
        ctx.commit('setToken', '');
        ctx.commit('setUser', '');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
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
    getToken(state) {
      return state.token;
    },
    getUser(state) {
      return state.user;
    },
  },
};

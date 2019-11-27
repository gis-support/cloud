import Swagger from 'swagger-client';
import api from '@/docs/api.json';

const swagger = new Swagger({ spec: api }).client;

export default {
  state: {
    logged: false,
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
      state.logged = true;
    },
    logOut(state) {
      state.token = '';
      state.user = '';
      state.logged = false;
      localStorage.removeItem('token');
    },
  },
  actions: {
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
        console.log(payload);
        const response = await swagger.apis.Auth.post_api_register({ body: payload });
        console.log(response);
        return response;
      } catch (err) {
        return err.response;
      }
    },
  },
  getters: {
    getToken(state) {
      return state.token;
    },
    getUser(state) {
      return state.user;
    },
    getLogged(state) {
      return state.logged;
    },
  },
};

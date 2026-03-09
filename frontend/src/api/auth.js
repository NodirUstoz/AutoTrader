import client from './client';

const authApi = {
  register(data) {
    return client.post('/auth/register/', data);
  },

  login(email, password) {
    return client.post('/auth/login/', { email, password });
  },

  logout(refreshToken) {
    return client.post('/auth/logout/', { refresh: refreshToken });
  },

  refreshToken(refreshToken) {
    return client.post('/auth/token/refresh/', { refresh: refreshToken });
  },

  getProfile() {
    return client.get('/auth/profile/');
  },

  updateProfile(data) {
    return client.patch('/auth/profile/', data);
  },

  changePassword(data) {
    return client.put('/auth/profile/password/', data);
  },

  getBuyerProfile() {
    return client.get('/auth/profile/buyer/');
  },

  updateBuyerProfile(data) {
    return client.patch('/auth/profile/buyer/', data);
  },

  getDealers(params = {}) {
    return client.get('/auth/dealers/', { params });
  },

  getDealerDetail(id) {
    return client.get(`/auth/dealers/${id}/`);
  },
};

export default authApi;

import client from './client';

const listingsApi = {
  list(params = {}) {
    return client.get('/listings/', { params });
  },

  get(id) {
    return client.get(`/listings/${id}/`);
  },

  create(data) {
    return client.post('/listings/create/', data);
  },

  update(id, data) {
    return client.patch(`/listings/${id}/`, data);
  },

  delete(id) {
    return client.delete(`/listings/${id}/`);
  },

  publish(id) {
    return client.post(`/listings/${id}/publish/`);
  },

  markSold(id) {
    return client.post(`/listings/${id}/sold/`);
  },

  getMyListings() {
    return client.get('/listings/mine/');
  },

  // Saved searches
  getSavedSearches() {
    return client.get('/listings/saved-searches/');
  },

  createSavedSearch(data) {
    return client.post('/listings/saved-searches/', data);
  },

  updateSavedSearch(id, data) {
    return client.patch(`/listings/saved-searches/${id}/`, data);
  },

  deleteSavedSearch(id) {
    return client.delete(`/listings/saved-searches/${id}/`);
  },

  // Inquiries
  sendInquiry(data) {
    return client.post('/inquiries/', data);
  },

  getSentInquiries() {
    return client.get('/inquiries/sent/');
  },

  getReceivedInquiries() {
    return client.get('/inquiries/received/');
  },

  replyToInquiry(id, message) {
    return client.post(`/inquiries/${id}/reply/`, { reply_message: message });
  },

  // Test drives
  requestTestDrive(data) {
    return client.post('/inquiries/test-drives/', data);
  },

  getTestDrives() {
    return client.get('/inquiries/test-drives/list/');
  },

  // Financing
  calculateFinancing(data) {
    return client.post('/financing/calculate/', data);
  },

  submitLoanApplication(data) {
    return client.post('/financing/apply/', data);
  },

  getMyApplications() {
    return client.get('/financing/applications/');
  },

  getMyCalculations() {
    return client.get('/financing/calculations/');
  },
};

export default listingsApi;

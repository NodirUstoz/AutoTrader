import client from './client';

const vehiclesApi = {
  list(params = {}) {
    return client.get('/vehicles/', { params });
  },

  get(id) {
    return client.get(`/vehicles/${id}/`);
  },

  create(data) {
    return client.post('/vehicles/create/', data);
  },

  update(id, data) {
    return client.patch(`/vehicles/${id}/`, data);
  },

  delete(id) {
    return client.delete(`/vehicles/${id}/`);
  },

  uploadImages(vehicleId, formData) {
    return client.post(`/vehicles/${vehicleId}/images/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  getMakes() {
    return client.get('/vehicles/makes/');
  },

  getModels(makeId = null) {
    const params = makeId ? { make: makeId } : {};
    return client.get('/vehicles/models/', { params });
  },

  getFeatures() {
    return client.get('/vehicles/features/');
  },

  decodeVin(vin) {
    return client.get(`/vehicles/vin/${vin}/`);
  },

  getMyVehicles() {
    return client.get('/vehicles/mine/');
  },

  // Comparisons
  createComparison(vehicleIds, title = '') {
    return client.post('/comparisons/', {
      vehicle_ids: vehicleIds,
      title,
    });
  },

  getComparison(id) {
    return client.get(`/comparisons/${id}/`);
  },

  addToComparison(comparisonId, vehicleId) {
    return client.post(`/comparisons/${comparisonId}/add/`, {
      vehicle_id: vehicleId,
    });
  },

  removeFromComparison(comparisonId, vehicleId) {
    return client.post(`/comparisons/${comparisonId}/remove/`, {
      vehicle_id: vehicleId,
    });
  },

  getMyComparisons() {
    return client.get('/comparisons/mine/');
  },
};

export default vehiclesApi;

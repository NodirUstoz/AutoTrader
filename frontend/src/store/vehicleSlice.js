import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import vehiclesApi from '../api/vehicles';
import listingsApi from '../api/listings';

export const fetchListings = createAsyncThunk(
  'vehicles/fetchListings',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await listingsApi.list(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch listings');
    }
  }
);

export const fetchVehicleDetail = createAsyncThunk(
  'vehicles/fetchVehicleDetail',
  async (id, { rejectWithValue }) => {
    try {
      const response = await vehiclesApi.get(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch vehicle');
    }
  }
);

export const fetchMakes = createAsyncThunk(
  'vehicles/fetchMakes',
  async (_, { rejectWithValue }) => {
    try {
      const response = await vehiclesApi.getMakes();
      return response.data;
    } catch (error) {
      return rejectWithValue('Failed to fetch makes');
    }
  }
);

export const fetchModels = createAsyncThunk(
  'vehicles/fetchModels',
  async (makeId, { rejectWithValue }) => {
    try {
      const response = await vehiclesApi.getModels(makeId);
      return response.data;
    } catch (error) {
      return rejectWithValue('Failed to fetch models');
    }
  }
);

const vehicleSlice = createSlice({
  name: 'vehicles',
  initialState: {
    listings: [],
    totalCount: 0,
    totalPages: 0,
    currentPage: 1,
    selectedVehicle: null,
    makes: [],
    models: [],
    comparisonIds: [],
    loading: false,
    error: null,
    filters: {
      search: '',
      make: '',
      model: '',
      year_min: '',
      year_max: '',
      price_min: '',
      price_max: '',
      mileage_max: '',
      body_type: '',
      fuel_type: '',
      transmission: '',
      condition: '',
    },
  },
  reducers: {
    setFilters(state, action) {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters(state) {
      state.filters = {
        search: '',
        make: '',
        model: '',
        year_min: '',
        year_max: '',
        price_min: '',
        price_max: '',
        mileage_max: '',
        body_type: '',
        fuel_type: '',
        transmission: '',
        condition: '',
      };
    },
    addToComparison(state, action) {
      const id = action.payload;
      if (!state.comparisonIds.includes(id) && state.comparisonIds.length < 4) {
        state.comparisonIds.push(id);
      }
    },
    removeFromComparison(state, action) {
      state.comparisonIds = state.comparisonIds.filter((id) => id !== action.payload);
    },
    clearComparison(state) {
      state.comparisonIds = [];
    },
    clearSelectedVehicle(state) {
      state.selectedVehicle = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchListings.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchListings.fulfilled, (state, action) => {
        state.loading = false;
        state.listings = action.payload.results || [];
        state.totalCount = action.payload.count || 0;
        state.totalPages = action.payload.total_pages || 0;
        state.currentPage = action.payload.current_page || 1;
      })
      .addCase(fetchListings.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchVehicleDetail.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchVehicleDetail.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedVehicle = action.payload;
      })
      .addCase(fetchVehicleDetail.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchMakes.fulfilled, (state, action) => {
        state.makes = action.payload;
      })
      .addCase(fetchModels.fulfilled, (state, action) => {
        state.models = action.payload;
      });
  },
});

export const {
  setFilters,
  clearFilters,
  addToComparison,
  removeFromComparison,
  clearComparison,
  clearSelectedVehicle,
} = vehicleSlice.actions;

export default vehicleSlice.reducer;

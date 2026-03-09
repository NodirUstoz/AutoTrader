import { useCallback, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useSearchParams } from 'react-router-dom';

import { clearFilters, fetchListings, fetchMakes, fetchModels, setFilters } from '../store/vehicleSlice';

export default function useVehicleSearch() {
  const dispatch = useDispatch();
  const [searchParams, setSearchParams] = useSearchParams();
  const { listings, totalCount, totalPages, currentPage, loading, error, filters, makes, models } =
    useSelector((state) => state.vehicles);

  // Sync URL params to Redux filters on mount
  useEffect(() => {
    const urlFilters = {};
    for (const [key, value] of searchParams.entries()) {
      if (value) urlFilters[key] = value;
    }
    if (Object.keys(urlFilters).length > 0) {
      dispatch(setFilters(urlFilters));
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Load makes on mount
  useEffect(() => {
    if (makes.length === 0) {
      dispatch(fetchMakes());
    }
  }, [dispatch, makes.length]);

  // Load models when make changes
  useEffect(() => {
    if (filters.make) {
      dispatch(fetchModels(filters.make));
    }
  }, [dispatch, filters.make]);

  const search = useCallback(
    (page = 1) => {
      const params = {};
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params[key] = value;
      });
      params.page = page;

      // Update URL
      setSearchParams(params);

      // Fetch results
      dispatch(fetchListings(params));
    },
    [dispatch, filters, setSearchParams]
  );

  const updateFilter = useCallback(
    (name, value) => {
      const update = { [name]: value };
      // Reset model when make changes
      if (name === 'make') {
        update.model = '';
      }
      dispatch(setFilters(update));
    },
    [dispatch]
  );

  const resetFilters = useCallback(() => {
    dispatch(clearFilters());
    setSearchParams({});
  }, [dispatch, setSearchParams]);

  const goToPage = useCallback(
    (page) => {
      search(page);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    [search]
  );

  return {
    listings,
    totalCount,
    totalPages,
    currentPage,
    loading,
    error,
    filters,
    makes,
    models,
    search,
    updateFilter,
    resetFilters,
    goToPage,
  };
}

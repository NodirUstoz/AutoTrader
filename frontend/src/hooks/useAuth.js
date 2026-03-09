import { useCallback, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

import authApi from '../api/auth';
import {
  clearError,
  fetchUserProfile,
  loginUser,
  logout as logoutAction,
  registerUser,
} from '../store/authSlice';

export default function useAuth() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, isAuthenticated, loading, error, refreshToken } = useSelector(
    (state) => state.auth
  );

  // Fetch user profile when authenticated but user data is missing
  useEffect(() => {
    if (isAuthenticated && !user) {
      dispatch(fetchUserProfile());
    }
  }, [isAuthenticated, user, dispatch]);

  const login = useCallback(
    async (email, password) => {
      const result = await dispatch(loginUser({ email, password }));
      if (loginUser.fulfilled.match(result)) {
        await dispatch(fetchUserProfile());
        toast.success('Welcome back!');
        navigate('/');
        return true;
      }
      return false;
    },
    [dispatch, navigate]
  );

  const register = useCallback(
    async (userData) => {
      const result = await dispatch(registerUser(userData));
      if (registerUser.fulfilled.match(result)) {
        toast.success('Account created successfully!');
        navigate('/');
        return true;
      }
      return false;
    },
    [dispatch, navigate]
  );

  const logout = useCallback(async () => {
    try {
      if (refreshToken) {
        await authApi.logout(refreshToken);
      }
    } catch {
      // Ignore errors during logout API call
    }
    dispatch(logoutAction());
    toast.info('You have been logged out.');
    navigate('/');
  }, [dispatch, navigate, refreshToken]);

  const clearAuthError = useCallback(() => {
    dispatch(clearError());
  }, [dispatch]);

  return {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    clearAuthError,
    isDealer: user?.role === 'dealer',
    isBuyer: user?.role === 'buyer',
    isAdmin: user?.role === 'admin',
  };
}

import { createStore } from 'vuex';
import axios from 'axios';

// Create axios instance with configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    // Log request errors in development mode
    if (import.meta.env.MODE === 'development') {
      console.error('Request error:', error);
    }
    return Promise.reject(error);
  }
);

export default createStore({
  state: {
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user')) || null,
    userRole: localStorage.getItem('userRole') || '',
    isVerified: localStorage.getItem('isVerified') === 'true' || false,
    services: [],
    serviceRequests: [],
    professionals: [],
    customers: [],
    loading: false,
    error: null
  },
  getters: {
    isAuthenticated: state => !!state.token,
    isAdmin: state => state.userRole === 'ADMIN',
    isProfessional: state => state.userRole === 'PROFESSIONAL',
    isCustomer: state => state.userRole === 'CUSTOMER',
    isProfessionalVerified: state => state.isVerified,
    currentUser: state => state.user,
    userRole: state => state.userRole,
    getLoading: state => state.loading,
    getError: state => state.error,
    getServices: state => state.services,
    getServiceRequests: state => state.serviceRequests,
    getProfessionals: state => state.professionals,
    getCustomers: state => state.customers
  },
  mutations: {
    SET_TOKEN(state, token) {
      state.token = token;
    },
    SET_USER(state, user) {
      state.user = user;
    },
    SET_USER_ROLE(state, role) {
      state.userRole = role;
    },
    SET_PROFESSIONAL_VERIFIED(state, isVerified) {
      state.isVerified = isVerified;
    },
    SET_LOADING(state, loading) {
      state.loading = loading;
    },
    SET_ERROR(state, error) {
      state.error = error;
    },
    SET_SERVICES(state, services) {
      state.services = services;
    },
    SET_SERVICE_REQUESTS(state, requests) {
      state.serviceRequests = requests;
    },
    SET_PROFESSIONALS(state, professionals) {
      state.professionals = professionals;
    },
    SET_CUSTOMERS(state, customers) {
      state.customers = customers;
    },
    CLEAR_AUTH(state) {
      state.token = '';
      state.user = null;
      state.userRole = '';
      state.isVerified = false;
    }
  },
  actions: {
    // Authentication actions
    async login({ commit }, credentials) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.post(`/auth/login`, credentials);
        const { access_token, refresh_token, user, email } = response.data;
        
        // Ensure we have a complete user object with all necessary properties
        const userObject = {
          ...user,
          email: email || (user && user.email) || '',
          role: (user && user.role) || 'CUSTOMER' // Default to CUSTOMER if role is not provided
        };
        
        // Store normalized role (always uppercase)
        const normalizedRole = userObject.role.toUpperCase();
        
        // Handle professional verification status
        let isVerified = false;
        if (normalizedRole === 'PROFESSIONAL' && user.is_verified !== undefined) {
          isVerified = user.is_verified;
          userObject.is_verified = isVerified;
        }
        
        localStorage.setItem('token', access_token);
        localStorage.setItem('refreshToken', refresh_token);
        localStorage.setItem('userRole', normalizedRole);
        localStorage.setItem('user', JSON.stringify(userObject));
        localStorage.setItem('isVerified', isVerified.toString());
        
        commit('SET_TOKEN', access_token);
        commit('SET_USER', userObject);
        commit('SET_USER_ROLE', normalizedRole);
        commit('SET_PROFESSIONAL_VERIFIED', isVerified);
        
        // Token will be automatically used in future requests via the interceptor
        
        return { success: true, role: normalizedRole };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Login failed');
        return { success: false, error: error.response?.data?.error || 'Login failed' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async register({ commit }, userData) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        console.log('Sending customer registration request with data:', userData);
        const response = await api.post(`/auth/register/customer`, userData);
        console.log('Registration response:', response.data);
        return { success: true, message: response.data.message };
      } catch (error) {
        console.error('Registration error:', error);
        const errorMessage = error.response?.data?.error || 'Registration failed: ' + error.message;
        commit('SET_ERROR', errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async registerProfessional({ commit }, formData) {
      try {
        // FormData is already created in the component, so we can use it directly
        const response = await api.post('/auth/register/professional', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        console.log('Professional registration response:', response.data);
        return { success: true, message: response.data.message };
      } catch (error) {
        console.error('Professional registration error:', error);
        const errorMessage = error.response?.data?.error || 'Professional registration failed: ' + error.message;
        commit('SET_ERROR', errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    logout({ commit }) {
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('userRole');
      localStorage.removeItem('user');
      localStorage.removeItem('isVerified');
      
      commit('CLEAR_AUTH');
      // No need to delete headers with interceptors
      
      return { success: true };
    },
    
    // User profile actions
    async fetchUserProfile({ commit }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.get(`/users/profile`);
        commit('SET_USER', response.data);
        return { success: true, user: response.data };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to fetch profile');
        return { success: false, error: error.response?.data?.error || 'Failed to fetch profile' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async updateUserProfile({ commit }, profileData) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.put(`/users/profile`, profileData);
        commit('SET_USER', response.data);
        return { success: true, user: response.data };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to update profile');
        return { success: false, error: error.response?.data?.error || 'Failed to update profile' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    // Service actions
    async fetchServices({ commit }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.get(`/admin/services`);
        commit('SET_SERVICES', response.data);
        return { success: true, services: response.data };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to fetch services');
        return { success: false, error: error.response?.data?.error || 'Failed to fetch services' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    // Service request actions
    async fetchServiceRequests({ commit, state }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        let url = `/service-requests/customer`;
        if (state.userRole === 'ADMIN') {
          url = `/admin/service-requests`;
        } else if (state.userRole === 'PROFESSIONAL') {
          url = `/service-requests/professional`;
        }
        
        const response = await api.get(url);
        commit('SET_SERVICE_REQUESTS', response.data);
        return { success: true, requests: response.data };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to fetch service requests');
        return { success: false, error: error.response?.data?.error || 'Failed to fetch service requests' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async fetchAvailableServiceRequests({ commit }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.get(`/service-requests/available`);
        return { success: true, requests: response.data };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to fetch available service requests');
        return { success: false, error: error.response?.data?.error || 'Failed to fetch available service requests' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async acceptServiceRequest({ commit }, requestId) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.post(`/service-requests/${requestId}/accept`);
        return { success: true, request: response.data.service_request, message: response.data.message };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to accept service request');
        return { success: false, error: error.response?.data?.error || 'Failed to accept service request' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async createServiceRequest({ commit }, requestData) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.post(`/service-requests`, requestData);
        return { success: true, request: response.data.service_request };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to create service request');
        return { success: false, error: error.response?.data?.error || 'Failed to create service request' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    // Admin actions
    async fetchProfessionals({ commit }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.get(`/admin/professionals`);
        commit('SET_PROFESSIONALS', response.data);
        return { success: true, professionals: response.data };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to fetch professionals');
        return { success: false, error: error.response?.data?.error || 'Failed to fetch professionals' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async fetchCustomers({ commit }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.get(`/admin/customers`);
        commit('SET_CUSTOMERS', response.data);
        return { success: true, customers: response.data };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to fetch customers');
        return { success: false, error: error.response?.data?.error || 'Failed to fetch customers' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async verifyProfessional({ commit }, professionalId) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.post(`/admin/professionals/verify/${professionalId}`);
        return { success: true, message: response.data.message };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to verify professional');
        return { success: false, error: error.response?.data?.error || 'Failed to verify professional' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async rejectProfessional({ commit }, professionalId) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.post(`/admin/professionals/reject/${professionalId}`);
        return { success: true, message: response.data.message };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to reject professional');
        return { success: false, error: error.response?.data?.error || 'Failed to reject professional' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async resetProfessionalStatus({ commit }, professionalId) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.post(`/admin/professionals/reset/${professionalId}`);
        return { success: true, message: response.data.message };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to reset professional status');
        return { success: false, error: error.response?.data?.error || 'Failed to reset professional status' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async assignProfessionalToRequest({ commit }, { requestId, professionalId }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.put(`/admin/service-requests/${requestId}/assign`, { professional_id: professionalId });
        return { success: true, request: response.data.service_request };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to assign professional');
        return { success: false, error: error.response?.data?.error || 'Failed to assign professional' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async updateServiceRequestStatus({ commit }, { requestId, status }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.put(`/admin/service-requests/${requestId}/status`, { status });
        return { success: true, request: response.data.service_request };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to update service request status');
        return { success: false, error: error.response?.data?.error || 'Failed to update service request status' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async cancelServiceRequest({ commit }, requestId) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.put(`/service-requests/${requestId}/cancel`);
        return { success: true, request: response.data.service_request };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to cancel service request');
        return { success: false, error: error.response?.data?.error || 'Failed to cancel service request' };
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async submitReview({ commit }, { requestId, reviewData }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.post(`/service-requests/${requestId}/complete`, reviewData);
        return { success: true, review: response.data };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to submit review');
        return { success: false, error: error.response?.data?.error || 'Failed to submit review' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async createService({ commit }, serviceData) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.post(`/admin/services`, serviceData);
        return { success: true, service: response.data };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to create service');
        return { success: false, error: error.response?.data?.error || 'Failed to create service' };
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async updateService({ commit }, serviceData) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      try {
        const response = await api.put(`/admin/services/${serviceData.id}`, serviceData);
        return { success: true, service: response.data };
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.error || 'Failed to update service');
        return { success: false, error: error.response?.data?.error || 'Failed to update service' };
      } finally {
        commit('SET_LOADING', false);
      }
    }
  }
});
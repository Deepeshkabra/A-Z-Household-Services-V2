<template>
  <AppLayout>
    <div class="admin-dashboard">
      <div class="row mb-4">
        <div class="col-12">
          <div class="card shadow-sm">
            <div class="card-body">
              <h2 class="card-title">Welcome, {{ user ? user.name : 'Admin' }}!</h2>
              <p class="card-text">Manage professionals, customers, service requests, and services from your dashboard.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <!-- Quick Actions -->
        <div class="col-md-4">
          <div class="card h-100 shadow-sm">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">Quick Actions</h5>
            </div>
            <div class="card-body">
              <div class="d-grid gap-3">
                <router-link to="/admin/professionals" class="btn btn-outline-primary">
                  <i class="bi bi-person-badge me-2"></i> Manage Professionals
                </router-link>
                <router-link to="/admin/customers" class="btn btn-outline-primary">
                  <i class="bi bi-people me-2"></i> Manage Customers
                </router-link>
                <router-link to="/admin/service-requests" class="btn btn-outline-primary">
                  <i class="bi bi-list-check me-2"></i> Service Requests
                </router-link>
                <router-link to="/admin/services" class="btn btn-outline-primary">
                  <i class="bi bi-tools me-2"></i> Manage Services
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Pending Verifications -->
        <div class="col-md-8">
          <div class="card h-100 shadow-sm">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Pending Professional Verifications</h5>
              <router-link to="/admin/professionals" class="btn btn-sm btn-light">View All</router-link>
            </div>
            <div class="card-body">
              <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div v-else-if="pendingProfessionals.length === 0" class="text-center py-5">
                <p class="mb-3">No pending professional verifications.</p>
              </div>
              <div v-else>
                <div class="list-group">
                  <div v-for="professional in pendingProfessionals" :key="professional.id" class="list-group-item list-group-item-action">
                    <div class="d-flex w-100 justify-content-between align-items-center">
                      <h6 class="mb-1">{{ professional.user.name }}</h6>
                      <span class="badge bg-warning">Pending</span>
                    </div>
                    <p class="mb-1 text-truncate-2">{{ professional.specialization }}</p>
                    <div class="d-flex justify-content-between align-items-center">
                      <small class="text-muted">Joined: {{ formatDate(professional.created_at) }}</small>
                      <div>
                        <button @click="verifyProfessional(professional.id)" class="btn btn-sm btn-success me-2">
                          <i class="bi bi-check-circle me-1"></i> Verify
                        </button>
                        <button @click="rejectProfessional(professional.id)" class="btn btn-sm btn-danger">
                          <i class="bi bi-x-circle me-1"></i> Reject
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Section -->
      <div class="row g-4 mt-4">
        <div class="col-md-3">
          <div class="card shadow-sm">
            <div class="card-body text-center">
              <div class="display-4 text-primary mb-2">
                <i class="bi bi-people"></i>
              </div>
              <h5>Total Customers</h5>
              <h3 class="mb-0">{{ stats.totalCustomers || 0 }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card shadow-sm">
            <div class="card-body text-center">
              <div class="display-4 text-success mb-2">
                <i class="bi bi-person-badge"></i>
              </div>
              <h5>Total Professionals</h5>
              <h3 class="mb-0">{{ stats.totalProfessionals || 0 }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card shadow-sm">
            <div class="card-body text-center">
              <div class="display-4 text-info mb-2">
                <i class="bi bi-list-check"></i>
              </div>
              <h5>Service Requests</h5>
              <h3 class="mb-0">{{ stats.totalRequests || 0 }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card shadow-sm">
            <div class="card-body text-center">
              <div class="display-4 text-warning mb-2">
                <i class="bi bi-tools"></i>
              </div>
              <h5>Services</h5>
              <h3 class="mb-0">{{ stats.totalServices || 0 }}</h3>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Service Requests -->
      <div class="row mt-4">
        <div class="col-12">
          <div class="card shadow-sm">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Recent Service Requests</h5>
              <router-link to="/admin/service-requests" class="btn btn-sm btn-light">View All</router-link>
            </div>
            <div class="card-body">
              <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div v-else-if="recentRequests.length === 0" class="text-center py-5">
                <p class="mb-3">No service requests available.</p>
              </div>
              <div v-else>
                <div class="table-responsive">
                  <table class="table table-hover">
                    <thead>
                      <tr>
                        <th>Service</th>
                        <th>Customer</th>
                        <th>Professional</th>
                        <th>Date</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="request in recentRequests" :key="request.id">
                        <td>{{ request.service_name }}</td>
                        <td>{{ request.customer_name }}</td>
                        <td>{{ request.professional_name || 'Not Assigned' }}</td>
                        <td>{{ formatDate(request.preferred_date) }}</td>
                        <td>
                          <span class="badge" :class="getStatusBadgeClass(request.status)">
                            {{ formatStatus(request.status) }}
                          </span>
                        </td>
                        <td>
                          <button class="btn btn-sm btn-outline-primary me-1">
                            <i class="bi bi-eye"></i>
                          </button>
                          <button class="btn btn-sm btn-outline-danger">
                            <i class="bi bi-trash"></i>
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { computed, onMounted, ref } from 'vue';
import { useStore } from 'vuex';
import AppLayout from '../../components/layout/AppLayout.vue';

export default {
  name: 'AdminDashboard',
  components: {
    AppLayout
  },
  setup() {
    const store = useStore();
    const loading = ref(true);
    const serviceRequests = ref([]);
    const professionals = ref([]);
    const customers = ref([]);
    const services = ref([]);
    const stats = ref({
      totalCustomers: 0,
      totalProfessionals: 0,
      totalRequests: 0,
      totalServices: 0
    });

    const user = computed(() => store.getters.currentUser);
    const pendingProfessionals = computed(() => {
      return professionals.value.filter(pro => !pro.is_verified);
    });
    const recentRequests = computed(() => serviceRequests.value.slice(0, 5));

    onMounted(async () => {
      try {
        // Fetch user profile if not already in store
        if (!user.value) {
          await store.dispatch('fetchUserProfile');
        }
        
        // Fetch service requests
        const requestsResult = await store.dispatch('fetchServiceRequests');
        if (requestsResult.success) {
          serviceRequests.value = requestsResult.requests;
        }

        // Fetch professionals
        const professionalsResult = await store.dispatch('fetchProfessionals');
        if (professionalsResult.success) {
          professionals.value = professionalsResult.professionals;
        }

        // Fetch customers
        const customersResult = await store.dispatch('fetchCustomers');
        if (customersResult.success) {
          customers.value = customersResult.customers;
        }

        // Fetch services
        const servicesResult = await store.dispatch('fetchServices');
        if (servicesResult.success) {
          services.value = servicesResult.services;
        }

        // Update stats
        stats.value.totalCustomers = customers.value.length;
        stats.value.totalProfessionals = professionals.value.length;
        stats.value.totalRequests = serviceRequests.value.length;
        stats.value.totalServices = services.value.length;
      } catch (error) {
        console.error('Error loading admin dashboard data:', error);
      } finally {
        loading.value = false;
      }
    });

    const verifyProfessional = async (professionalId) => {
      try {
        loading.value = true;
        const result = await store.dispatch('verifyProfessional', professionalId);
        if (result.success) {
          // Refresh professionals list
          const professionalsResult = await store.dispatch('fetchProfessionals');
          if (professionalsResult.success) {
            professionals.value = professionalsResult.professionals;
          }
        }
      } catch (error) {
        console.error('Error verifying professional:', error);
      } finally {
        loading.value = false;
      }
    };

    const rejectProfessional = async (professionalId) => {
      try {
        loading.value = true;
        const result = await store.dispatch('rejectProfessional', professionalId);
        if (result.success) {
          // Refresh professionals list
          const professionalsResult = await store.dispatch('fetchProfessionals');
          if (professionalsResult.success) {
            professionals.value = professionalsResult.professionals;
          }
        }
      } catch (error) {
        console.error('Error rejecting professional:', error);
      } finally {
        loading.value = false;
      }
    };

    const formatDate = (dateString) => {
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    };

    const formatStatus = (status) => {
      return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    };

    const getStatusBadgeClass = (status) => {
      const statusMap = {
        'pending': 'bg-warning',
        'accepted': 'bg-info',
        'in_progress': 'bg-primary',
        'completed': 'bg-success',
        'cancelled': 'bg-danger'
      };
      return statusMap[status] || 'bg-secondary';
    };

    return {
      user,
      loading,
      serviceRequests,
      professionals,
      pendingProfessionals,
      recentRequests,
      stats,
      formatDate,
      formatStatus,
      getStatusBadgeClass,
      verifyProfessional,
      rejectProfessional
    };
  }
};
</script>

<style scoped>
.text-truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
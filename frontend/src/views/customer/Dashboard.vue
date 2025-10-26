<template>
  <AppLayout>
    <div class="customer-dashboard">
      <div class="row mb-4">
        <div class="col-12">
          <div class="card shadow-sm">
            <div class="card-body">
              <h2 class="card-title">Welcome, {{ user ? user.name : 'Customer' }}!</h2>
              <p class="card-text">Manage your service requests and profile from your dashboard.</p>
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
                <router-link to="/customer/new-request" class="btn btn-outline-primary">
                  <i class="bi bi-plus-circle me-2"></i> New Service Request
                </router-link>
                <router-link to="/customer/service-requests" class="btn btn-outline-primary">
                  <i class="bi bi-list-check me-2"></i> View My Requests
                </router-link>
                <router-link to="/customer/profile" class="btn btn-outline-primary">
                  <i class="bi bi-person me-2"></i> Update Profile
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Service Requests -->
        <div class="col-md-8">
          <div class="card h-100 shadow-sm">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Recent Service Requests</h5>
              <router-link to="/customer/service-requests" class="btn btn-sm btn-light">View All</router-link>
            </div>
            <div class="card-body">
              <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div v-else-if="serviceRequests.length === 0" class="text-center py-5">
                <p class="mb-3">You don't have any service requests yet.</p>
                <router-link to="/customer/new-request" class="btn btn-primary">
                  Create Your First Request
                </router-link>
              </div>
              <div v-else>
                <div class="list-group">
                  <div v-for="request in recentRequests" :key="request.id" class="list-group-item list-group-item-action">
                    <div class="d-flex w-100 justify-content-between align-items-center">
                      <h6 class="mb-1">{{ request.service_name }}</h6>
                      <span class="badge" :class="getStatusBadgeClass(request.status)">{{ formatStatus(request.status) }}</span>
                    </div>
                    <p class="mb-1 text-truncate-2">{{ request.description }}</p>
                    <small class="text-muted">Created: {{ formatDate(request.created_at) }}</small>
                  </div>
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
  name: 'CustomerDashboard',
  components: {
    AppLayout
  },
  setup() {
    const store = useStore();
    const loading = ref(true);
    const serviceRequests = ref([]);

    const user = computed(() => store.getters.currentUser);
    const recentRequests = computed(() => serviceRequests.value.slice(0, 5));

    onMounted(async () => {
      try {
        // Fetch user profile if not already in store
        if (!user.value) {
          await store.dispatch('fetchUserProfile');
        }
        
        // Fetch service requests
        const result = await store.dispatch('fetchServiceRequests');
        if (result.success) {
          serviceRequests.value = result.requests;
        }
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        loading.value = false;
      }
    });

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
      recentRequests,
      formatDate,
      formatStatus,
      getStatusBadgeClass
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
<template>
  <AppLayout>
    <div class="professional-dashboard">
      <div class="row mb-4">
        <div class="col-12">
          <div class="card shadow-sm">
            <div class="card-body">
              <h2 class="card-title">Welcome, {{ user ? user.name : 'Professional' }}!</h2>
              <p class="card-text">Manage your service requests and profile from your dashboard.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Verification Alert -->
      <div v-if="!isProfessionalVerified" class="row mb-4">
        <div class="col-12">
          <div class="alert alert-warning" role="alert">
            <div class="d-flex align-items-center">
              <i class="bi bi-exclamation-triangle-fill me-2 fs-4"></i>
              <div>
                <h5 class="alert-heading mb-1">Verification Pending</h5>
                <p class="mb-0">Your account is pending verification. You will be able to accept service requests once an admin verifies your account.</p>
              </div>
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
                <router-link to="/professional/service-requests" class="btn btn-outline-primary">
                  <i class="bi bi-list-check me-2"></i> View Service Requests
                </router-link>
                <router-link to="/professional/profile" class="btn btn-outline-primary">
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
              <h5 class="mb-0">My Recent Service Requests</h5>
              <router-link to="/professional/service-requests" class="btn btn-sm btn-light">View All</router-link>
            </div>
            <div class="card-body">
              <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div v-else-if="!isProfessionalVerified" class="text-center py-5">
                <p class="mb-3">You'll be able to view and accept service requests once your account is verified.</p>
              </div>
              <div v-else-if="myServiceRequests.length === 0" class="text-center py-5">
                <p class="mb-3">You haven't accepted any service requests yet.</p>
                <router-link to="/professional/service-requests" class="btn btn-primary">
                  Browse Available Requests
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
                    <div class="d-flex justify-content-between align-items-center">
                      <small class="text-muted">Customer: {{ request.customer_name }}</small>
                      <small class="text-muted">Date: {{ formatDate(request.preferred_date) }}</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Section -->
      <div class="row g-4 mt-2">
        <div class="col-md-4">
          <div class="card shadow-sm">
            <div class="card-body text-center">
              <div class="display-4 text-primary mb-2">
                <i class="bi bi-check-circle"></i>
              </div>
              <h5>Completed Jobs</h5>
              <h3 class="mb-0">{{ stats.completed || 0 }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card shadow-sm">
            <div class="card-body text-center">
              <div class="display-4 text-warning mb-2">
                <i class="bi bi-hourglass-split"></i>
              </div>
              <h5>In Progress</h5>
              <h3 class="mb-0">{{ stats.inProgress || 0 }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card shadow-sm">
            <div class="card-body text-center">
              <div class="display-4 text-success mb-2">
                <i class="bi bi-star"></i>
              </div>
              <h5>Rating</h5>
              <h3 class="mb-0">{{ stats.rating || 'N/A' }}</h3>
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
  name: 'ProfessionalDashboard',
  components: {
    AppLayout
  },
  setup() {
    const store = useStore();
    const loading = ref(true);
    const serviceRequests = ref([]);
    const stats = ref({
      completed: 0,
      inProgress: 0,
      rating: 'N/A'
    });

    const user = computed(() => store.getters.currentUser);
    const isProfessionalVerified = computed(() => store.getters.isProfessionalVerified);
    const myServiceRequests = computed(() => {
      return serviceRequests.value.filter(req => req.professional_id === user.value?.professional?.id);
    });
    const recentRequests = computed(() => myServiceRequests.value.slice(0, 5));

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
          
          // Calculate stats
          if (user.value?.professional?.id) {
            const myRequests = result.requests.filter(req => req.professional_id === user.value.professional.id);
            stats.value.completed = myRequests.filter(req => req.status === 'completed').length;
            stats.value.inProgress = myRequests.filter(req => req.status === 'in_progress').length;
            
            // Calculate average rating if available
            const completedWithRatings = myRequests.filter(req => req.status === 'completed' && req.rating);
            if (completedWithRatings.length > 0) {
              const totalRating = completedWithRatings.reduce((sum, req) => sum + req.rating, 0);
              stats.value.rating = (totalRating / completedWithRatings.length).toFixed(1);
            }
          }
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
      isProfessionalVerified,
      loading,
      serviceRequests,
      myServiceRequests,
      recentRequests,
      stats,
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
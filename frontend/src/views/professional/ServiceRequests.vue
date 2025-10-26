<template>
  <AppLayout>
    <div class="row mb-4">
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h4 class="mb-0">Service Requests</h4>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="!isProfessionalVerified" class="text-center py-5">
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
            <div v-else>
              <!-- Filter and Search -->
              <div class="row mb-4">
                <div class="col-md-6 mb-3 mb-md-0">
                  <div class="input-group">
                    <input
                      type="text"
                      class="form-control"
                      placeholder="Search requests..."
                      v-model="searchQuery"
                    />
                    <button class="btn btn-outline-secondary" type="button">
                      <i class="bi bi-search"></i>
                    </button>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="d-flex justify-content-md-end">
                    <select class="form-select" v-model="statusFilter">
                      <option value="all">All Statuses</option>
                      <option value="requested">Available Requests</option>
                      <option value="accepted">Accepted</option>
                      <option value="in_progress">In Progress</option>
                      <option value="completed">Completed</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- Tabs for My Requests vs Available Requests -->
              <ul class="nav nav-tabs mb-4">
                <li class="nav-item">
                  <a 
                    class="nav-link" 
                    :class="{ active: activeTab === 'my' }" 
                    href="#" 
                    @click.prevent="activeTab = 'my'"
                  >
                    My Service Requests
                  </a>
                </li>
                <li class="nav-item">
                  <a 
                    class="nav-link" 
                    :class="{ active: activeTab === 'available' }" 
                    href="#" 
                    @click.prevent="activeTab = 'available'"
                  >
                    Available Requests
                  </a>
                </li>
              </ul>

              <!-- My Service Requests Tab -->
              <div v-if="activeTab === 'my'">
                <div v-if="myServiceRequests.length === 0" class="text-center py-5">
                  <p class="mb-3">You haven't accepted any service requests yet.</p>
                  <button class="btn btn-primary" @click="activeTab = 'available'">
                    Browse Available Requests
                  </button>
                </div>
                <div v-else class="table-responsive">
                  <table class="table table-hover align-middle">
                    <thead class="table-light">
                      <tr>
                        <th>Service</th>
                        <th>Customer</th>
                        <th>Date Requested</th>
                        <th>Preferred Date</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="request in filteredMyRequests" :key="request.id">
                        <td>
                          <div class="fw-bold">{{ request.service.name }}</div>
                          <small class="text-muted text-truncate-2">{{ request.description }}</small>
                        </td>
                        <td>{{ request.customer_id }}</td>
                        <td>{{ formatDate(request.created_at) }}</td>
                        <!-- <td>{{ formatDate(request.preferred_date) }}</td> -->
                        <td>
                          <span class="badge" :class="getStatusBadgeClass(request.status)">
                            {{ formatStatus(request.status) }}
                          </span>
                        </td>
                        <td>
                          <button
                            class="btn btn-sm btn-outline-primary me-1"
                            @click="viewRequestDetails(request)"
                            title="View Details"
                          >
                            <i class="bi bi-eye"></i>
                          </button>
                          <button
                            v-if="request.status === 'accepted'"
                            class="btn btn-sm btn-outline-success me-1"
                            @click="updateRequestStatus(request.id, 'in_progress')"
                            title="Start Service"
                          >
                            <i class="bi bi-play-fill"></i>
                          </button>
                          <button
                            v-if="request.status === 'in_progress'"
                            class="btn btn-sm btn-outline-success me-1"
                            @click="updateRequestStatus(request.id, 'completed')"
                            title="Mark as Completed"
                          >
                            <i class="bi bi-check-lg"></i>
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Available Service Requests Tab -->
              <div v-if="activeTab === 'available'">
                <div v-if="availableRequests.length === 0" class="text-center py-5">
                  <p class="mb-3">There are no available service requests at the moment.</p>
                  <p>Check back later for new requests.</p>
                </div>
                <div v-else class="table-responsive">
                  <table class="table table-hover align-middle">
                    <thead class="table-light">
                      <tr>
                        <th>Service</th>
                        <th>Customer</th>
                        <th>Date Requested</th>
                        <th>Preferred Date</th>
                        <th>Location</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <!-- <tr v-for="request in filteredAvailableRequests" :key="request.id"> -->
                      <!-- <p>{{ availableRequests }}</p> -->
                      <tr v-for="request in availableRequests" :key="request.id">
                        <td>
                          <div class="fw-bold">{{ request.service_name }}</div>
                          <small class="text-muted text-truncate-2">{{ request.description }}</small>
                        </td>
                        <td>{{ request.customer_name }}</td>
                        <td>{{ formatDate(request.created_at) }}</td>
                        <td>{{ formatDate(request.preferred_date) }}</td>
                        <td>{{ request.location }}</td>
                        <td>
                          <button
                            class="btn btn-sm btn-outline-primary me-1"
                            @click="viewRequestDetails(request)"
                            title="View Details"
                          >
                            <i class="bi bi-eye"></i>
                          </button>
                          <button
                            class="btn btn-sm btn-outline-success"
                            @click="acceptRequest(request.id)"
                            title="Accept Request"
                          >
                            <i class="bi bi-check-circle"></i>
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

    <!-- Request Details Modal -->
    <div class="modal fade" id="requestDetailsModal" tabindex="-1" aria-labelledby="requestDetailsModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title" id="requestDetailsModalLabel">Service Request Details</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body" v-if="selectedRequest">
            <div class="row mb-4">
              <div class="col-md-6">
                <h6 class="text-muted mb-2">Service Information</h6>
                <p class="mb-1"><strong>Service Type:</strong> {{ selectedRequest.service_name }}</p>
                <p class="mb-1"><strong>Status:</strong> 
                  <span class="badge" :class="getStatusBadgeClass(selectedRequest.status)">
                    {{ formatStatus(selectedRequest.status) }}
                  </span>
                </p>
                <p class="mb-1"><strong>Date Requested:</strong> {{ formatDate(selectedRequest.created_at) }}</p>
                <p class="mb-1"><strong>Preferred Date:</strong> {{ formatDate(selectedRequest.preferred_date) }}</p>
                <p class="mb-1"><strong>Preferred Time:</strong> {{ selectedRequest.preferred_time }}</p>
              </div>
              <div class="col-md-6">
                <h6 class="text-muted mb-2">Customer Information</h6>
                <p class="mb-1"><strong>Name:</strong> {{ selectedRequest.customer_name }}</p>
                <p class="mb-1"><strong>Phone:</strong> {{ selectedRequest.customer_phone }}</p>
                <p class="mb-1"><strong>Address:</strong> {{ selectedRequest.location }}</p>
              </div>
            </div>
            <div class="row">
              <div class="col-12">
                <h6 class="text-muted mb-2">Service Description</h6>
                <p>{{ selectedRequest.description }}</p>
              </div>
            </div>
            <div v-if="selectedRequest.notes" class="row mt-3">
              <div class="col-12">
                <h6 class="text-muted mb-2">Additional Notes</h6>
                <p>{{ selectedRequest.notes }}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button 
              v-if="selectedRequest && selectedRequest.status === 'pending' && activeTab === 'available'" 
              type="button" 
              class="btn btn-success"
              @click="acceptRequest(selectedRequest.id)"
            >
              Accept Request
            </button>
            <button 
              v-if="selectedRequest && selectedRequest.status === 'accepted'" 
              type="button" 
              class="btn btn-primary"
              @click="updateRequestStatus(selectedRequest.id, 'in_progress')"
            >
              Start Service
            </button>
            <button 
              v-if="selectedRequest && selectedRequest.status === 'in_progress'" 
              type="button" 
              class="btn btn-success"
              @click="updateRequestStatus(selectedRequest.id, 'completed')"
            >
              Mark as Completed
            </button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { Modal } from 'bootstrap';
import AppLayout from '../../components/layout/AppLayout.vue';

export default {
  name: 'ProfessionalServiceRequests',
  components: {
    AppLayout
  },
  setup() {
    const store = useStore();
    const loading = ref(false);
    const error = ref(null);
    const success = ref(null);
    const searchQuery = ref('');
    const statusFilter = ref('all');
    const activeTab = ref('my');
    const selectedRequest = ref(null);
    const serviceRequests = ref([]);
    const requestModal = ref(null);

    // Computed properties
    const user = computed(() => store.getters.currentUser);
    const isProfessionalVerified = computed(() => store.getters.isProfessionalVerified);

    const myServiceRequests = computed(() => {
      return serviceRequests.value.filter(request => 
        request.professional_id === user.value?.professional?.id
      );
    });

    const availableRequests = computed(() => {
      return serviceRequests.value.filter(request => {
        // Check if the request is in 'pending' status (backend uses 'requested', frontend uses 'pending')
        const statusMatch = request.status === 'pending' || request.status === 'requested';
        
        // Check if no professional is assigned yet
        const noProfessionalAssigned = request.professional_id === null;
        
        // Check if the service ID matches the professional's service ID
        // Handle both formats: request.service_id or request.service.id
        const serviceIdMatch = 
          (request.service_id && request.service_id === user.value?.professional?.service_id) || 
          (request.service && request.service.id === user.value?.professional?.service_id);
        
        return statusMatch && noProfessionalAssigned && serviceIdMatch;
      });
    });

    const filteredMyRequests = computed(() => {
      let filtered = myServiceRequests.value;
      
      if (statusFilter.value !== 'all') {
        filtered = filtered.filter(request => request.status === statusFilter.value);
      }
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        filtered = filtered.filter(request => 
          request.service_name.toLowerCase().includes(query) ||
          request.description.toLowerCase().includes(query) ||
          request.customer_name.toLowerCase().includes(query)
        );
      }
      
      return filtered;
    });

    const filteredAvailableRequests = computed(() => {
      let filtered = availableRequests.value;
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        filtered = filtered.filter(request => {
          // Handle both formats: direct properties or nested service object
          const serviceName = request.service_name || (request.service && request.service.name) || '';
          const serviceDesc = request.description || (request.service && request.service.description) || '';
          const location = request.location || '';
          
          return serviceName.toLowerCase().includes(query) ||
                 serviceDesc.toLowerCase().includes(query) ||
                 location.toLowerCase().includes(query);
        });
      }
      
      return filtered;
    });

    // Methods
    const fetchServiceRequests = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        // Fetch my service requests
        const myResponse = await store.dispatch('fetchServiceRequests');
        if (myResponse.success) {
          // These are already filtered by professional ID in the backend
          serviceRequests.value = myResponse.requests;
        } else {
          error.value = myResponse.error || 'Failed to fetch service requests';
        }
        
        // Fetch available service requests
        const availableResponse = await store.dispatch('fetchAvailableServiceRequests');
        if (availableResponse.success) {
          // Add available requests to the service requests array
          const availableRequests = availableResponse.requests.filter(req => 
            // Ensure we don't add duplicates
            !serviceRequests.value.some(existing => existing.id === req.id)
          );
          serviceRequests.value = [...serviceRequests.value, ...availableRequests];
          console.log(serviceRequests.value);
          // serviceRequests.value = [...serviceRequests.value, ...availableResponse.requests];
        } else {
          error.value = availableResponse.error || 'Failed to fetch available service requests';
        }
      } catch (err) {
        error.value = 'An unexpected error occurred';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    const acceptRequest = async (requestId) => {
      loading.value = true;
      error.value = null;
      success.value = null;
      
      try {
        const response = await store.dispatch('acceptServiceRequest', requestId);
        if (response.success) {
          success.value = 'Service request accepted successfully';
          await fetchServiceRequests();
          if (requestModal.value) {
            requestModal.value.hide();
          }
        } else {
          error.value = response.error || 'Failed to accept service request';
        }
      } catch (err) {
        error.value = 'An unexpected error occurred';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    const updateRequestStatus = async (requestId, newStatus) => {
      loading.value = true;
      error.value = null;
      success.value = null;
      
      try {
        const response = await store.dispatch('updateServiceRequestStatus', {
          requestId,
          status: newStatus
        });
        
        if (response.success) {
          success.value = `Service request ${formatStatus(newStatus).toLowerCase()}`;
          await fetchServiceRequests();
          if (requestModal.value) {
            requestModal.value.hide();
          }
        } else {
          error.value = response.error || 'Failed to update service request status';
        }
      } catch (err) {
        error.value = 'An unexpected error occurred';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    const viewRequestDetails = (request) => {
      selectedRequest.value = request;
      if (!requestModal.value) {
        requestModal.value = new Modal(document.getElementById('requestDetailsModal'));
      }
      requestModal.value.show();
    };

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    };

    const formatStatus = (status) => {
      const statusMap = {
        'requested': 'requested',
        'accepted': 'Accepted',
        'in_progress': 'In Progress',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
      };
      return statusMap[status] || status;
    };

    const getStatusBadgeClass = (status) => {
      const classMap = {
        'requested': 'bg-warning',
        'accepted': 'bg-info',
        'in_progress': 'bg-primary',
        'completed': 'bg-success',
        'cancelled': 'bg-danger'
      };
      return classMap[status] || 'bg-secondary';
    };

    // Lifecycle hooks
    onMounted(async () => {
      await fetchServiceRequests();
    });

    return {
      loading,
      error,
      success,
      user,
      isProfessionalVerified,
      searchQuery,
      statusFilter,
      activeTab,
      serviceRequests,
      myServiceRequests,
      availableRequests,
      filteredMyRequests,
      filteredAvailableRequests,
      selectedRequest,
      fetchServiceRequests,
      acceptRequest,
      updateRequestStatus,
      viewRequestDetails,
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
  text-overflow: ellipsis;
}

.table th {
  font-weight: 600;
}

.badge {
  font-size: 0.8rem;
  padding: 0.35em 0.65em;
}
</style>
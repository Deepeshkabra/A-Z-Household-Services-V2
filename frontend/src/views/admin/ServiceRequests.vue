<template>
  <AppLayout>
    <div class="row mb-4">
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h4 class="mb-0">Service Requests</h4>
            <button class="btn btn-sm btn-light" @click="refreshData">
              <i class="bi bi-arrow-clockwise me-1"></i> Refresh
            </button>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="serviceRequests.length === 0" class="text-center py-5">
              <p class="mb-3">No service requests found.</p>
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
                      <option value="pending">Pending</option>
                      <option value="accepted">Accepted</option>
                      <option value="in_progress">In Progress</option>
                      <option value="completed">Completed</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- Service Requests Table -->
              <div class="table-responsive">
                <table class="table table-hover align-middle">
                  <thead class="table-light">
                    <tr>
                      <th>Service</th>
                      <th>Customer</th>
                      <th>Date Requested</th>
                      <th>Preferred Date</th>
                      <th>Professional</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="request in filteredRequests" :key="request.id">
                      <td>
                        <div class="fw-bold">{{ request.service_name }}</div>
                        <small class="text-muted text-truncate-2">{{ request.description }}</small>
                      </td>
                      <td>
                        <div v-if="request.customer">
                          {{ request.customer.name }}
                          <div><small class="text-muted">{{ request.customer.email }}</small></div>
                        </div>
                        <div v-else>-</div>
                      </td>
                      <td>{{ formatDate(request.created_at) }}</td>
                      <td>{{ formatDate(request.preferred_date) }}</td>
                      <td>
                        <div v-if="request.professional">
                          {{ request.professional.name }}
                        </div>
                        <div v-else-if="request.status === 'pending'">
                          <button 
                            class="btn btn-sm btn-outline-primary"
                            @click="assignProfessional(request)"
                          >
                            Assign
                          </button>
                        </div>
                        <div v-else>-</div>
                      </td>
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
                          v-if="request.status === 'pending'"
                          class="btn btn-sm btn-outline-danger"
                          @click="cancelRequest(request.id)"
                          title="Cancel Request"
                        >
                          <i class="bi bi-x-circle"></i>
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

    <!-- Request Details Modal -->
    <div
      class="modal fade"
      id="requestDetailsModal"
      tabindex="-1"
      aria-labelledby="requestDetailsModalLabel"
      aria-hidden="true"
      ref="detailsModal"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedRequest">
          <div class="modal-header">
            <h5 class="modal-title" id="requestDetailsModalLabel">Service Request Details</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <div class="row mb-3">
              <div class="col-md-6">
                <h6>Service</h6>
                <p>{{ selectedRequest.service_name }}</p>
              </div>
              <div class="col-md-6">
                <h6>Status</h6>
                <span class="badge" :class="getStatusBadgeClass(selectedRequest.status)">
                  {{ formatStatus(selectedRequest.status) }}
                </span>
              </div>
            </div>

            <div class="row mb-3">
              <div class="col-md-6">
                <h6>Date Requested</h6>
                <p>{{ formatDate(selectedRequest.created_at) }}</p>
              </div>
              <div class="col-md-6">
                <h6>Preferred Date & Time</h6>
                <p>
                  {{ formatDate(selectedRequest.preferred_date) }} -
                  {{ formatTime(selectedRequest.preferred_time) }}
                </p>
              </div>
            </div>

            <div class="mb-3">
              <h6>Service Address</h6>
              <p>{{ selectedRequest.address }}</p>
            </div>

            <div class="mb-3">
              <h6>Description</h6>
              <p>{{ selectedRequest.description }}</p>
            </div>

            <div class="mb-3" v-if="selectedRequest.notes">
              <h6>Additional Notes</h6>
              <p>{{ selectedRequest.notes }}</p>
            </div>

            <div class="mb-3" v-if="selectedRequest.customer">
              <h6>Customer Information</h6>
              <div class="d-flex align-items-center">
                <div class="avatar me-3">{{ getCustomerInitials(selectedRequest.customer) }}</div>
                <div>
                  <p class="mb-0 fw-bold">{{ selectedRequest.customer.name }}</p>
                  <p class="mb-0">{{ selectedRequest.customer.email }}</p>
                  <p class="mb-0">{{ selectedRequest.customer.phone }}</p>
                </div>
              </div>
            </div>

            <div class="mb-3" v-if="selectedRequest.professional">
              <h6>Assigned Professional</h6>
              <div class="d-flex align-items-center">
                <div class="avatar me-3">{{ getProfessionalInitials(selectedRequest.professional) }}</div>
                <div>
                  <p class="mb-0 fw-bold">{{ selectedRequest.professional.name }}</p>
                  <p class="mb-0">{{ selectedRequest.professional.email }}</p>
                  <p class="mb-0">{{ selectedRequest.professional.phone }}</p>
                </div>
              </div>
            </div>

            <div class="mb-3" v-if="selectedRequest.review">
              <h6>Customer Review</h6>
              <div class="d-flex align-items-center mb-2">
                <div class="rating text-warning me-2">
                  <i
                    v-for="star in 5"
                    :key="star"
                    class="bi"
                    :class="{
                      'bi-star-fill': star <= selectedRequest.review.rating,
                      'bi-star': star > selectedRequest.review.rating
                    }"
                  ></i>
                </div>
                <span>{{ selectedRequest.review.rating }}.0</span>
              </div>
              <p>{{ selectedRequest.review.comment }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <div v-if="selectedRequest.status === 'pending' && !selectedRequest.professional_id" class="me-auto">
              <button 
                type="button" 
                class="btn btn-primary"
                @click="showAssignModal"
              >
                Assign Professional
              </button>
            </div>
            <div v-if="selectedRequest.status === 'accepted'" class="me-auto">
              <button 
                type="button" 
                class="btn btn-primary"
                @click="updateStatus(selectedRequest.id, 'in_progress')"
              >
                Mark In Progress
              </button>
            </div>
            <div v-if="selectedRequest.status === 'in_progress'" class="me-auto">
              <button 
                type="button" 
                class="btn btn-success"
                @click="updateStatus(selectedRequest.id, 'completed')"
              >
                Mark Completed
              </button>
            </div>
            <button
              v-if="selectedRequest.status === 'pending'"
              type="button"
              class="btn btn-danger me-auto"
              @click="cancelRequest(selectedRequest.id)"
            >
              Cancel Request
            </button>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Assign Professional Modal -->
    <div
      class="modal fade"
      id="assignProfessionalModal"
      tabindex="-1"
      aria-labelledby="assignProfessionalModalLabel"
      aria-hidden="true"
      ref="assignModal"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="assignProfessionalModalLabel">Assign Professional</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <div v-if="loadingProfessionals" class="text-center py-3">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="professionals.length === 0" class="text-center py-3">
              <p>No professionals available.</p>
            </div>
            <div v-else>
              <div class="mb-3">
                <label for="professionalSelect" class="form-label">Select Professional</label>
                <select class="form-select" id="professionalSelect" v-model="selectedProfessionalId">
                  <option value="" disabled>Choose a professional</option>
                  <option 
                    v-for="professional in professionals" 
                    :key="professional.id" 
                    :value="professional.id"
                  >
                    {{ professional.name }} - {{ professional.specialization }}
                  </option>
                </select>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="confirmAssignProfessional"
              :disabled="!selectedProfessionalId"
            >
              Assign
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
import AppLayout from '../../components/layout/AppLayout.vue';

export default {
  name: 'AdminServiceRequests',
  components: {
    AppLayout
  },
  setup() {
    const store = useStore();
    const loading = ref(true);
    const serviceRequests = ref([]);
    const searchQuery = ref('');
    const statusFilter = ref('all');
    const selectedRequest = ref(null);
    const detailsModal = ref(null);
    const assignModal = ref(null);
    const professionals = ref([]);
    const loadingProfessionals = ref(false);
    const selectedProfessionalId = ref('');
    
    // Filter service requests based on search query and status filter
    const filteredRequests = computed(() => {
      let filtered = serviceRequests.value;
      
      // Filter by status
      if (statusFilter.value !== 'all') {
        filtered = filtered.filter(request => request.status === statusFilter.value);
      }
      
      // Filter by search query
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        filtered = filtered.filter(request => {
          return (
            request.service_name?.toLowerCase().includes(query) ||
            request.description?.toLowerCase().includes(query) ||
            request.customer?.name?.toLowerCase().includes(query) ||
            request.customer?.email?.toLowerCase().includes(query) ||
            request.address?.toLowerCase().includes(query)
          );
        });
      }
      
      return filtered;
    });

    onMounted(async () => {
      try {
        // Initialize Bootstrap modals
        const { Modal } = await import('bootstrap');
        detailsModal.value = new Modal(document.getElementById('requestDetailsModal'));
        assignModal.value = new Modal(document.getElementById('assignProfessionalModal'));
        
        // Fetch service requests
        await refreshData();
      } catch (error) {
        console.error('Error loading service requests:', error);
      } finally {
        loading.value = false;
      }
    });

    const refreshData = async () => {
      loading.value = true;
      try {
        const result = await store.dispatch('fetchServiceRequests');
        if (result.success) {
          serviceRequests.value = result.requests;
        }
      } catch (error) {
        console.error('Error refreshing service requests:', error);
      } finally {
        loading.value = false;
      }
    };

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    };

    const formatTime = (timeSlot) => {
      const timeMap = {
        'morning': 'Morning (8:00 AM - 12:00 PM)',
        'afternoon': 'Afternoon (12:00 PM - 4:00 PM)',
        'evening': 'Evening (4:00 PM - 8:00 PM)'
      };
      return timeMap[timeSlot] || timeSlot;
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

    const getProfessionalInitials = (professional) => {
      if (!professional || !professional.name) return 'NA';
      return professional.name.split(' ')
        .map(name => name[0])
        .join('')
        .toUpperCase();
    };

    const getCustomerInitials = (customer) => {
      if (!customer || !customer.name) return 'NA';
      return customer.name.split(' ')
        .map(name => name[0])
        .join('')
        .toUpperCase();
    };

    const viewRequestDetails = (request) => {
      selectedRequest.value = request;
      detailsModal.value.show();
    };

    const cancelRequest = async (requestId) => {
      if (confirm('Are you sure you want to cancel this service request?')) {
        try {
          const result = await store.dispatch('cancelServiceRequest', requestId);
          if (result.success) {
            // Update the request status in the list
            const index = serviceRequests.value.findIndex(req => req.id === requestId);
            if (index !== -1) {
              serviceRequests.value[index].status = 'cancelled';
            }
            
            // Close modal if open
            if (selectedRequest.value && selectedRequest.value.id === requestId) {
              selectedRequest.value.status = 'cancelled';
            }
          }
        } catch (error) {
          console.error('Error cancelling service request:', error);
        }
      }
    };

    const assignProfessional = async (request) => {
      selectedRequest.value = request;
      selectedProfessionalId.value = '';
      await loadProfessionals();
      assignModal.value.show();
    };

    const showAssignModal = async () => {
      selectedProfessionalId.value = '';
      await loadProfessionals();
      assignModal.value.show();
    };

    const loadProfessionals = async () => {
      loadingProfessionals.value = true;
      try {
        const result = await store.dispatch('fetchProfessionals');
        if (result.success) {
          professionals.value = result.professionals.filter(p => p.is_verified);
        }
      } catch (error) {
        console.error('Error loading professionals:', error);
      } finally {
        loadingProfessionals.value = false;
      }
    };

    const confirmAssignProfessional = async () => {
      if (!selectedRequest.value || !selectedProfessionalId.value) return;
      
      try {
        const result = await store.dispatch('assignProfessionalToRequest', {
          requestId: selectedRequest.value.id,
          professionalId: selectedProfessionalId.value
        });
        
        if (result.success) {
          const professionalToAssign = professionals.value.find(p => p.id === selectedProfessionalId.value);
          
          if (professionalToAssign) {
            const index = serviceRequests.value.findIndex(req => req.id === selectedRequest.value.id);
            if (index !== -1) {
              serviceRequests.value[index].professional = professionalToAssign;
              serviceRequests.value[index].professional_id = professionalToAssign.id;
              serviceRequests.value[index].status = 'accepted';
              
              // Update selected request if modal is open
              if (selectedRequest.value) {
                selectedRequest.value.professional = professionalToAssign;
                selectedRequest.value.professional_id = professionalToAssign.id;
                selectedRequest.value.status = 'accepted';
              }
            }
          }
          
          // Close the assign modal
          assignModal.value.hide();
        }
      } catch (error) {
        console.error('Error assigning professional:', error);
      }
    };

    const updateStatus = async (requestId, newStatus) => {
      try {
        const result = await store.dispatch('updateServiceRequestStatus', {
          requestId,
          status: newStatus
        });
        
        if (result.success) {
          // Update the request status in the list
          const index = serviceRequests.value.findIndex(req => req.id === requestId);
          if (index !== -1) {
            serviceRequests.value[index].status = newStatus;
          }
          
          // Update selected request if modal is open
          if (selectedRequest.value && selectedRequest.value.id === requestId) {
            selectedRequest.value.status = newStatus;
          }
        }
      } catch (error) {
        console.error('Error updating service request status:', error);
      }
    };

    return {
      loading,
      serviceRequests,
      searchQuery,
      statusFilter,
      filteredRequests,
      selectedRequest,
      professionals,
      loadingProfessionals,
      selectedProfessionalId,
      formatDate,
      formatTime,
      formatStatus,
      getStatusBadgeClass,
      getProfessionalInitials,
      getCustomerInitials,
      viewRequestDetails,
      cancelRequest,
      assignProfessional,
      showAssignModal,
      confirmAssignProfessional,
      updateStatus,
      refreshData
    };
  }
};
</script>

<style scoped>
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #6c757d;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.rating {
  display: flex;
}

.text-truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
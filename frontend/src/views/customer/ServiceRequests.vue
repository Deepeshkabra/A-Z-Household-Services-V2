<template>
  <AppLayout>
    <div class="row mb-4">
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h4 class="mb-0">My Service Requests</h4>
            <router-link to="/customer/new-request" class="btn btn-light btn-sm">
              <i class="bi bi-plus-circle me-1"></i> New Request
            </router-link>
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

              <!-- Service Requests Table -->
              <div class="table-responsive">
                <table class="table table-hover align-middle">
                  <thead class="table-light">
                    <tr>
                      <th>Service</th>
                      <th>Date Requested</th>
                      <th>Preferred Date</th>
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
                      <td>{{ formatDate(request.created_at) }}</td>
                      <td>{{ formatDate(request.preferred_date) }}</td>
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

            <div class="mb-3" v-if="selectedRequest.professional">
              <h6>Assigned Professional</h6>
              <div class="d-flex align-items-center">
                <div class="avatar me-3">{{ getProfessionalInitials(selectedRequest.professional) }}</div>
                <div>
                  <p class="mb-0 fw-bold">{{ selectedRequest.professional.name }}</p>
                  <p class="mb-0">{{ selectedRequest.professional.phone }}</p>
                </div>
              </div>
            </div>

            <div class="mb-3" v-if="selectedRequest.status === 'completed' && !selectedRequest.review">
              <h6>Leave a Review</h6>
              <div class="mb-3">
                <label for="rating" class="form-label">Rating</label>
                <div class="rating-input">
                  <i
                    v-for="star in 5"
                    :key="star"
                    class="bi"
                    :class="{
                      'bi-star-fill': star <= reviewForm.rating,
                      'bi-star': star > reviewForm.rating
                    }"
                    @click="reviewForm.rating = star"
                  ></i>
                </div>
              </div>
              <div class="mb-3">
                <label for="reviewComment" class="form-label">Comment</label>
                <textarea
                  class="form-control"
                  id="reviewComment"
                  v-model="reviewForm.comment"
                  rows="3"
                ></textarea>
              </div>
              <button class="btn btn-primary" @click="submitReview">Submit Review</button>
            </div>

            <div class="mb-3" v-else-if="selectedRequest.review">
              <h6>Your Review</h6>
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
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useStore } from 'vuex';
import AppLayout from '../../components/layout/AppLayout.vue';

export default {
  name: 'CustomerServiceRequests',
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
    
    const reviewForm = ref({
      rating: 0,
      comment: ''
    });

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
            request.service_name.toLowerCase().includes(query) ||
            request.description.toLowerCase().includes(query) ||
            request.address.toLowerCase().includes(query)
          );
        });
      }
      
      return filtered;
    });

    onMounted(async () => {
      try {
        // Initialize Bootstrap modal
        const { Modal } = await import('bootstrap');
        detailsModal.value = new Modal(document.getElementById('requestDetailsModal'));
        
        // Fetch service requests
        const result = await store.dispatch('fetchServiceRequests');
        if (result.success) {
          serviceRequests.value = result.requests;
        }
      } catch (error) {
        console.error('Error loading service requests:', error);
      } finally {
        loading.value = false;
      }
    });

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

    const submitReview = async () => {
      if (reviewForm.value.rating === 0) {
        alert('Please select a rating');
        return;
      }
      
      try {
        const result = await store.dispatch('submitReview', {
          requestId: selectedRequest.value.id,
          reviewData: {
            rating: reviewForm.value.rating,
            comment: reviewForm.value.comment
          }
        });
        
        if (result.success) {
          // Update the request in the list
          const index = serviceRequests.value.findIndex(req => req.id === selectedRequest.value.id);
          if (index !== -1) {
            serviceRequests.value[index].review = {
              rating: reviewForm.value.rating,
              comment: reviewForm.value.comment
            };
          }
          
          // Update the selected request
          selectedRequest.value.review = {
            rating: reviewForm.value.rating,
            comment: reviewForm.value.comment
          };
          
          // Reset the form
          reviewForm.value = {
            rating: 0,
            comment: ''
          };
          
          // Show success message
          alert('Thank you for your review!');
        }
      } catch (error) {
        console.error('Error submitting review:', error);
        alert('Failed to submit review. Please try again.');
      }
    };

    return {
      loading,
      serviceRequests,
      searchQuery,
      statusFilter,
      filteredRequests,
      selectedRequest,
      reviewForm,
      formatDate,
      formatTime,
      formatStatus,
      getStatusBadgeClass,
      getProfessionalInitials,
      viewRequestDetails,
      cancelRequest,
      submitReview
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

.rating-input i {
  cursor: pointer;
  color: #ffc107;
  font-size: 1.5rem;
  margin-right: 0.25rem;
}

.rating i {
  color: #ffc107;
  margin-right: 0.1rem;
}

.text-truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
<template>
  <AppLayout>
    <div class="row mb-4">
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h4 class="mb-0">Manage Professionals</h4>
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
            <div v-else>
              <!-- Filter and Search -->
              <div class="row mb-4">
                <div class="col-md-6 mb-3 mb-md-0">
                  <div class="input-group">
                    <input
                      type="text"
                      class="form-control"
                      placeholder="Search professionals..."
                      v-model="searchQuery"
                    />
                    <button class="btn btn-outline-secondary" type="button">
                      <i class="bi bi-search"></i>
                    </button>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="d-flex justify-content-md-end">
                    <select class="form-select w-auto" v-model="statusFilter">
                      <option value="all">All Status</option>
                      <option value="verified">Verified</option>
                      <option value="pending">Pending Verification</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- Professionals Table -->
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Specialization</th>
                      <th>Joined</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="professional in filteredProfessionals" :key="professional.id">
                      <td>{{ professional.user.name }}</td>
                      <td>{{ professional.user.email }}</td>
                      <td>{{ professional.specialization }}</td>
                      <td>{{ formatDate(professional.created_at) }}</td>
                      <td>
                        <span 
                          class="badge" 
                          :class="{
                            'bg-success': professional.is_verified,
                            'bg-warning': !professional.is_verified
                          }"
                        >
                          {{ professional.is_verified ? 'Verified' : 'Pending' }}
                        </span>
                      </td>
                      <td>
                        <div class="btn-group">
                          <button 
                            v-if="!professional.is_verified"
                            @click="verifyProfessional(professional.id)" 
                            class="btn btn-sm btn-success me-1"
                            :disabled="loading"
                          >
                            <i class="bi bi-check-circle"></i>
                          </button>
                          <button 
                            v-if="!professional.is_verified"
                            @click="rejectProfessional(professional.id)" 
                            class="btn btn-sm btn-danger me-1"
                            :disabled="loading"
                          >
                            <i class="bi bi-x-circle"></i>
                          </button>
                          <button 
                            v-if="professional.is_verified"
                            @click="resetProfessionalStatus(professional.id)" 
                            class="btn btn-sm btn-secondary me-1"
                            :disabled="loading"
                          >
                            <i class="bi bi-arrow-counterclockwise"></i>
                          </button>
                          <button 
                            @click="viewProfessionalDetails(professional)" 
                            class="btn btn-sm btn-primary"
                          >
                            <i class="bi bi-eye"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Empty State -->
              <div v-if="filteredProfessionals.length === 0" class="text-center py-5">
                <p class="mb-0">No professionals found matching your criteria.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Professional Details Modal -->
    <div class="modal fade" id="professionalDetailsModal" tabindex="-1" aria-labelledby="professionalDetailsModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedProfessional">
          <div class="modal-header">
            <h5 class="modal-title" id="professionalDetailsModalLabel">Professional Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-md-6">
                <h6>Personal Information</h6>
                <p><strong>Name:</strong> {{ selectedProfessional.user.name }}</p>
                <p><strong>Email:</strong> {{ selectedProfessional.user.email }}</p>
                <p><strong>Phone:</strong> {{ selectedProfessional.phone || 'Not provided' }}</p>
                <p><strong>Address:</strong> {{ selectedProfessional.address || 'Not provided' }}</p>
                <p><strong>Joined:</strong> {{ formatDate(selectedProfessional.created_at) }}</p>
              </div>
              <div class="col-md-6">
                <h6>Professional Information</h6>
                <p><strong>Specialization:</strong> {{ selectedProfessional.specialization }}</p>
                <p><strong>Experience:</strong> {{ selectedProfessional.experience || 'Not provided' }} years</p>
                <p><strong>Status:</strong> 
                  <span 
                    class="badge" 
                    :class="{
                      'bg-success': selectedProfessional.is_verified,
                      'bg-warning': !selectedProfessional.is_verified
                    }"
                  >
                    {{ selectedProfessional.is_verified ? 'Verified' : 'Pending' }}
                  </span>
                </p>
                <p><strong>Completed Jobs:</strong> {{ selectedProfessional.completed_jobs || 0 }}</p>
                <p><strong>Average Rating:</strong> {{ selectedProfessional.average_rating || 'N/A' }}</p>
              </div>
            </div>
            <div class="row mt-3">
              <div class="col-12">
                <h6>Bio</h6>
                <p>{{ selectedProfessional.bio || 'No bio provided.' }}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button 
              v-if="!selectedProfessional.is_verified"
              @click="verifyProfessional(selectedProfessional.id)" 
              class="btn btn-success"
              :disabled="loading"
            >
              Verify
            </button>
            <button 
              v-if="!selectedProfessional.is_verified"
              @click="rejectProfessional(selectedProfessional.id)" 
              class="btn btn-danger"
              :disabled="loading"
            >
              Reject
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
  name: 'AdminProfessionals',
  components: {
    AppLayout
  },
  setup() {
    const store = useStore();
    const loading = ref(false);
    const professionals = ref([]);
    const searchQuery = ref('');
    const statusFilter = ref('all');
    const selectedProfessional = ref(null);

    const filteredProfessionals = computed(() => {
      let result = professionals.value;
      
      // Apply search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(pro => {
          return (
            pro.user.name.toLowerCase().includes(query) ||
            pro.user.email.toLowerCase().includes(query) ||
            (pro.specialization && pro.specialization.toLowerCase().includes(query))
          );
        });
      }
      
      // Apply status filter
      if (statusFilter.value !== 'all') {
        if (statusFilter.value === 'verified') {
          result = result.filter(pro => pro.is_verified);
        } else if (statusFilter.value === 'pending') {
          result = result.filter(pro => !pro.is_verified);
        }
      }

      return result;
    });

    const fetchProfessionals = async () => {
      loading.value = true;
      try {
        const result = await store.dispatch('fetchProfessionals');
        if (result.success) {
          professionals.value = result.professionals;
        } else {
          console.error('Failed to fetch professionals:', result.error);
        }
      } catch (error) {
        console.error('Error fetching professionals:', error);
      } finally {
        loading.value = false;
      }
    };

    const refreshData = () => {
      fetchProfessionals();
    };

    const verifyProfessional = async (professionalId) => {
      try {
        loading.value = true;
        const result = await store.dispatch('verifyProfessional', professionalId);
        if (result.success) {
          // Update the professional in the list
          await fetchProfessionals();
          // If the modal is open with this professional, update it
          if (selectedProfessional.value && selectedProfessional.value.id === professionalId) {
            const updatedPro = professionals.value.find(p => p.id === professionalId);
            if (updatedPro) {
              selectedProfessional.value = updatedPro;
            }
          }
        } else {
          console.error('Failed to verify professional:', result.error);
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
          // Update the professional in the list
          await fetchProfessionals();
          // If the modal is open with this professional, update it
          if (selectedProfessional.value && selectedProfessional.value.id === professionalId) {
            const updatedPro = professionals.value.find(p => p.id === professionalId);
            if (updatedPro) {
              selectedProfessional.value = updatedPro;
            }
          }
        } else {
          console.error('Failed to reject professional:', result.error);
        }
      } catch (error) {
        console.error('Error rejecting professional:', error);
      } finally {
        loading.value = false;
      }
    };

    const resetProfessionalStatus = async (professionalId) => {
      try {
        loading.value = true;
        const result = await store.dispatch('resetProfessionalStatus', professionalId);
        if (result.success) {
          // Update the professional in the list
          await fetchProfessionals();
          // If the modal is open with this professional, update it
          if (selectedProfessional.value && selectedProfessional.value.id === professionalId) {
            const updatedPro = professionals.value.find(p => p.id === professionalId);
            if (updatedPro) {
              selectedProfessional.value = updatedPro;
            }
          }
        } else {
          console.error('Failed to reset professional status:', result.error);
        }
      } catch (error) {
        console.error('Error resetting professional status:', error);
      } finally {
        loading.value = false;
      }
    };

    const viewProfessionalDetails = (professional) => {
      selectedProfessional.value = professional;
      // Use bootstrap modal
      const modalElement = document.getElementById('professionalDetailsModal');
      const modal = new bootstrap.Modal(modalElement);
      modal.show();
    };

    const formatDate = (dateString) => {
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    };

    onMounted(() => {
      fetchProfessionals();
    });

    return {
      loading,
      professionals,
      searchQuery,
      statusFilter,
      selectedProfessional,
      filteredProfessionals,
      refreshData,
      verifyProfessional,
      rejectProfessional,
      resetProfessionalStatus,
      viewProfessionalDetails,
      formatDate
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
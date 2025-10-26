<template>
  <AppLayout>
    <div class="row mb-4">
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h4 class="mb-0">Manage Services</h4>
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
              <!-- Filter and Add Service -->
              <div class="row mb-4">
                <div class="col-md-6 mb-3 mb-md-0">
                  <div class="input-group">
                    <input
                      type="text"
                      class="form-control"
                      placeholder="Search services..."
                      v-model="searchQuery"
                    />
                    <button class="btn btn-outline-secondary" type="button">
                      <i class="bi bi-search"></i>
                    </button>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="d-flex justify-content-md-end">
                    <button class="btn btn-primary" @click="openAddServiceModal">
                      <i class="bi bi-plus-circle me-1"></i> Add New Service
                    </button>
                  </div>
                </div>
              </div>

              <!-- Services Table -->
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Base Price</th>
                      <th>Category</th>
                      <th>Est. Time</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="service in filteredServices" :key="service.id">
                      <td>{{ service.name }}</td>
                      <td>${{ service.base_price }}</td>
                      <td>{{ service.category || 'Uncategorized' }}</td>
                      <td>{{ service.estimated_time ? `${service.estimated_time} mins` : 'Varies' }}</td>
                      <td>
                        <span 
                          class="badge" 
                          :class="{
                            'bg-success': service.is_available,
                            'bg-danger': !service.is_available
                          }"
                        >
                          {{ service.is_available ? 'Available' : 'Unavailable' }}
                        </span>
                      </td>
                      <td>
                        <div class="btn-group">
                          <button 
                            @click="toggleServiceStatus(service.id)" 
                            class="btn btn-sm" 
                            :class="service.is_available ? 'btn-warning' : 'btn-success'"
                            :disabled="loading"
                          >
                            <i class="bi" :class="service.is_available ? 'bi-pause-fill' : 'bi-play-fill'"></i>
                          </button>
                          <button 
                            @click="editService(service)" 
                            class="btn btn-sm btn-primary ms-1"
                          >
                            <i class="bi bi-pencil"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Empty State -->
              <div v-if="filteredServices.length === 0" class="text-center py-5">
                <p class="mb-0">No services found matching your criteria.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Service Modal -->
    <div class="modal fade" id="serviceModal" tabindex="-1" aria-labelledby="serviceModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="serviceModalLabel">{{ isEditing ? 'Edit Service' : 'Add New Service' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveService">
              <div class="mb-3">
                <label for="serviceName" class="form-label">Service Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="serviceName" 
                  v-model="serviceForm.name" 
                  required
                />
              </div>
              <div class="mb-3">
                <label for="servicePrice" class="form-label">Base Price ($)</label>
                <input 
                  type="number" 
                  class="form-control" 
                  id="servicePrice" 
                  v-model="serviceForm.base_price" 
                  min="0" 
                  step="0.01" 
                  required
                />
              </div>
              <div class="mb-3">
                <label for="serviceCategory" class="form-label">Category</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="serviceCategory" 
                  v-model="serviceForm.category"
                />
              </div>
              <div class="mb-3">
                <label for="serviceTime" class="form-label">Estimated Time (minutes)</label>
                <input 
                  type="number" 
                  class="form-control" 
                  id="serviceTime" 
                  v-model="serviceForm.estimated_time" 
                  min="0"
                />
              </div>
              <div class="mb-3">
                <label for="serviceDescription" class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  id="serviceDescription" 
                  v-model="serviceForm.description" 
                  rows="3"
                ></textarea>
              </div>
              <div class="form-check mb-3">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  id="serviceAvailable" 
                  v-model="serviceForm.is_available"
                />
                <label class="form-check-label" for="serviceAvailable">
                  Service is available
                </label>
              </div>
              <div class="alert alert-danger" v-if="formError">
                {{ formError }}
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="saveService" 
              :disabled="loading"
            >
              {{ isEditing ? 'Update' : 'Create' }}
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
import { Modal } from 'bootstrap';

export default {
  name: 'AdminServices',
  components: {
    AppLayout
  },
  setup() {
    const store = useStore();
    const loading = ref(false);
    const services = ref([]);
    const searchQuery = ref('');
    const isEditing = ref(false);
    const selectedServiceId = ref(null);
    const formError = ref('');
    
    const serviceForm = ref({
      name: '',
      base_price: 0.01,
      description: '',
      estimated_time: 1,
      category: '',
      is_available: true
    });

    const filteredServices = computed(() => {
      if (!searchQuery.value) {
        return services.value;
      }
      
      const query = searchQuery.value.toLowerCase();
      return services.value.filter(service => 
        service.name.toLowerCase().includes(query) ||
        (service.category && service.category.toLowerCase().includes(query))
      );
    });

    // Fetch all services
    const fetchServices = async () => {
      loading.value = true;
      try {
        const result = await store.dispatch('fetchServices');
        if (result.success) {
          services.value = result.services;
        } else {
          console.error('Error fetching services:', result.error);
        }
      } catch (error) {
        console.error('Error fetching services:', error);
      } finally {
        loading.value = false;
      }
    };

    // Refresh data
    const refreshData = () => {
      fetchServices();
    };

    // Open modal to add a new service
    const openAddServiceModal = () => {
      isEditing.value = false;
      selectedServiceId.value = null;
      resetForm();
      
      // Open modal
      const modalElement = document.getElementById('serviceModal');
      if (modalElement) {
        const modal = new Modal(modalElement);
        modal.show();
      }
    };

    // Open modal to edit a service
    const editService = (service) => {
      isEditing.value = true;
      selectedServiceId.value = service.id;
      
      // Populate form with service data
      serviceForm.value = {
        name: service.name,
        base_price: service.base_price,
        description: service.description || '',
        estimated_time: service.estimated_time || 0,
        category: service.category || '',
        is_available: service.is_available
      };
      
      // Open modal
      const modalElement = document.getElementById('serviceModal');
      if (modalElement) {
        const modal = new Modal(modalElement);
        modal.show();
      }
    };

    // Toggle service availability status
    const toggleServiceStatus = async (serviceId) => {
      loading.value = true;
      try {
        // Find the service
        const serviceIndex = services.value.findIndex(s => s.id === serviceId);
        if (serviceIndex === -1) return;
        
        const service = services.value[serviceIndex];
        const updatedStatus = !service.is_available;
        
        // Call API to update service status
        const result = await store.dispatch('updateService', {
          id: serviceId,
          is_available: updatedStatus
        });
        
        if (result.success) {
          // Update local state
          services.value[serviceIndex].is_available = updatedStatus;
        } else {
          console.error('Error updating service status:', result.error);
        }
      } catch (error) {
        console.error('Error toggling service status:', error);
      } finally {
        loading.value = false;
      }
    };

    // Save service (create or update)
    const saveService = async () => {
      formError.value = '';
      loading.value = true;
      
      try {
        let result;
        
        if (isEditing.value) {
          // Update existing service
          result = await store.dispatch('updateService', {
            id: selectedServiceId.value,
            ...serviceForm.value
          });
        } else {
          // Create new service
          result = await store.dispatch('createService', serviceForm.value);
        }
        
        if (result.success) {
          // Close modal
          const modalElement = document.getElementById('serviceModal');
          if (modalElement) {
            const modal = Modal.getInstance(modalElement);
            if (modal) {
              modal.hide();
            }
          }
          
          // Refresh services list
          fetchServices();
        } else {
          formError.value = result.error || 'Failed to save service';
        }
      } catch (error) {
        formError.value = 'An unexpected error occurred';
        console.error('Error saving service:', error);
      } finally {
        loading.value = false;
      }
    };

    // Reset form
    const resetForm = () => {
      serviceForm.value = {
        name: '',
        base_price: 0.01,
        description: '',
        estimated_time: 1,
        category: '',
        is_available: true
      };
      formError.value = '';
    };

    onMounted(() => {
      fetchServices();
    });

    return {
      loading,
      services,
      searchQuery,
      filteredServices,
      isEditing,
      serviceForm,
      formError,
      refreshData,
      openAddServiceModal,
      editService,
      toggleServiceStatus,
      saveService
    };
  }
};
</script>
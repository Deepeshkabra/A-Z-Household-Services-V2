<template>
  <AppLayout>
    <div class="row mb-4">
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h4 class="mb-0">Manage Customers</h4>
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
                      placeholder="Search customers..."
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
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- Customers Table -->
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Phone</th>
                      <th>Joined</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="customer in filteredCustomers" :key="customer.id">
                      <td>{{ customer.user.name }}</td>
                      <td>{{ customer.user.email }}</td>
                      <td>{{ customer.phone || 'Not provided' }}</td>
                      <td>{{ formatDate(customer.created_at) }}</td>
                      <td>
                        <span 
                          class="badge" 
                          :class="{
                            'bg-success': customer.is_active,
                            'bg-danger': !customer.is_active
                          }"
                        >
                          {{ customer.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td>
                        <div class="btn-group">
                          <button 
                            @click="toggleCustomerStatus(customer.id)" 
                            class="btn btn-sm" 
                            :class="customer.is_active ? 'btn-warning' : 'btn-success'"
                            :disabled="loading"
                          >
                            <i class="bi" :class="customer.is_active ? 'bi-pause-fill' : 'bi-play-fill'"></i>
                          </button>
                          <button 
                            @click="viewCustomerDetails(customer)" 
                            class="btn btn-sm btn-primary ms-1"
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
              <div v-if="filteredCustomers.length === 0" class="text-center py-5">
                <p class="mb-0">No customers found matching your criteria.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Customer Details Modal -->
    <div class="modal fade" id="customerDetailsModal" tabindex="-1" aria-labelledby="customerDetailsModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedCustomer">
          <div class="modal-header">
            <h5 class="modal-title" id="customerDetailsModalLabel">Customer Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-md-6">
                <h6>Personal Information</h6>
                <p><strong>Name:</strong> {{ selectedCustomer.user.name }}</p>
                <p><strong>Email:</strong> {{ selectedCustomer.user.email }}</p>
                <p><strong>Phone:</strong> {{ selectedCustomer.phone || 'Not provided' }}</p>
                <p><strong>Address:</strong> {{ selectedCustomer.address || 'Not provided' }}</p>
                <p><strong>Joined:</strong> {{ formatDate(selectedCustomer.created_at) }}</p>
              </div>
              <div class="col-md-6">
                <h6>Account Information</h6>
                <p><strong>Status:</strong> 
                  <span 
                    class="badge" 
                    :class="{
                      'bg-success': selectedCustomer.is_active,
                      'bg-danger': !selectedCustomer.is_active
                    }"
                  >
                    {{ selectedCustomer.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </p>
                <p><strong>Total Service Requests:</strong> {{ selectedCustomer.total_requests || 0 }}</p>
                <p><strong>Completed Requests:</strong> {{ selectedCustomer.completed_requests || 0 }}</p>
              </div>
            </div>
            <div class="row mt-3">
              <div class="col-12">
                <h6>Recent Service Requests</h6>
                <div v-if="selectedCustomer.recent_requests && selectedCustomer.recent_requests.length > 0">
                  <div class="list-group">
                    <div v-for="request in selectedCustomer.recent_requests" :key="request.id" class="list-group-item list-group-item-action">
                      <div class="d-flex w-100 justify-content-between align-items-center">
                        <h6 class="mb-1">{{ request.service_name }}</h6>
                        <span class="badge" :class="getStatusBadgeClass(request.status)">
                          {{ formatStatus(request.status) }}
                        </span>
                      </div>
                      <p class="mb-1">{{ request.description }}</p>
                      <small class="text-muted">{{ formatDate(request.preferred_date) }}</small>
                    </div>
                  </div>
                </div>
                <p v-else>No service requests found for this customer.</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button 
              @click="toggleCustomerStatus(selectedCustomer.id)" 
              class="btn" 
              :class="selectedCustomer.is_active ? 'btn-warning' : 'btn-success'"
              :disabled="loading"
            >
              {{ selectedCustomer.is_active ? 'Deactivate Account' : 'Activate Account' }}
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
  name: 'AdminCustomers',
  components: {
    AppLayout
  },
  setup() {
    const store = useStore();
    const loading = ref(false);
    const customers = ref([]);
    const searchQuery = ref('');
    const statusFilter = ref('all');
    const selectedCustomer = ref(null);

    const filteredCustomers = computed(() => {
      let result = customers.value;

      // Apply status filter
      if (statusFilter.value !== 'all') {
        if (statusFilter.value === 'active') {
          result = result.filter(customer => customer.is_active);
        } else if (statusFilter.value === 'inactive') {
          result = result.filter(customer => !customer.is_active);
        }
      }

      // Apply search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(customer => {
          return (
            customer.user.name.toLowerCase().includes(query) ||
            customer.user.email.toLowerCase().includes(query) ||
            (customer.phone && customer.phone.toLowerCase().includes(query))
          );
        });
      }

      return result;
    });

    const fetchCustomers = async () => {
      loading.value = true;
      try {
        const result = await store.dispatch('fetchCustomers');
        if (result.success) {
          customers.value = result.customers;
        } else {
          console.error('Failed to fetch customers:', result.error);
        }
      } catch (error) {
        console.error('Error fetching customers:', error);
      } finally {
        loading.value = false;
      }
    };

    const refreshData = () => {
      fetchCustomers();
    };

    const toggleCustomerStatus = async (customerId) => {
      try {
        loading.value = true;
        const customer = customers.value.find(c => c.id === customerId);
        const action = customer.is_active ? 'deactivateCustomer' : 'activateCustomer';
        
        const result = await store.dispatch(action, customerId);
        if (result.success) {
          // Update the customer in the list
          await fetchCustomers();
          // If the modal is open with this customer, update it
          if (selectedCustomer.value && selectedCustomer.value.id === customerId) {
            const updatedCustomer = customers.value.find(c => c.id === customerId);
            if (updatedCustomer) {
              selectedCustomer.value = updatedCustomer;
            }
          }
        } else {
          console.error(`Failed to ${customer.is_active ? 'deactivate' : 'activate'} customer:`, result.error);
        }
      } catch (error) {
        console.error('Error toggling customer status:', error);
      } finally {
        loading.value = false;
      }
    };

    const viewCustomerDetails = async (customer) => {
      try {
        loading.value = true;
        // Fetch detailed customer information including recent requests
        const result = await store.dispatch('fetchCustomerDetails', customer.id);
        if (result.success) {
          selectedCustomer.value = result.customer;
        } else {
          // Fallback to basic customer info if detailed fetch fails
          selectedCustomer.value = customer;
          console.error('Failed to fetch customer details:', result.error);
        }
        
        // Use bootstrap modal
        const modalElement = document.getElementById('customerDetailsModal');
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
      } catch (error) {
        console.error('Error viewing customer details:', error);
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

    onMounted(() => {
      fetchCustomers();
    });

    return {
      loading,
      customers,
      searchQuery,
      statusFilter,
      selectedCustomer,
      filteredCustomers,
      refreshData,
      toggleCustomerStatus,
      viewCustomerDetails,
      formatDate,
      formatStatus,
      getStatusBadgeClass
    };
  }
};
</script>
<template>
  <AppLayout>
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">New Service Request</h4>
          </div>
          <div class="card-body">
            <div v-if="error" class="alert alert-danger" role="alert">
              {{ error }}
            </div>
            <div v-if="success" class="alert alert-success" role="alert">
              {{ success }}
            </div>

            <form @submit.prevent="submitRequest">
              <div class="mb-3">
                <label for="service" class="form-label">Service Type</label>
                <select class="form-select" id="service" v-model="requestForm.service_id" required>
                  <option value="" disabled selected>Select a service</option>
                  <option v-for="service in services" :key="service.id" :value="service.id">
                    {{ service.name }} - ${{ service.base_price }}
                  </option>
                </select>
              </div>

              <div class="mb-3">
                <label for="description" class="form-label">Description</label>
                <textarea
                  class="form-control"
                  id="description"
                  v-model="requestForm.description"
                  rows="4"
                  required
                  placeholder="Please describe your service needs in detail"
                ></textarea>
              </div>

              <div class="mb-3">
                <label for="address" class="form-label">Service Address</label>
                <input
                  type="text"
                  class="form-control"
                  id="address"
                  v-model="requestForm.address"
                  required
                  placeholder="Enter the address where service is needed"
                />
              </div>

              <div class="mb-3">
                <label for="pin_code" class="form-label">Pincode</label>
                <input
                  type="text"
                  class="form-control"
                  id="pin_code"
                  v-model="requestForm.pin_code"
                  required
                  placeholder="Enter area pincode"
                  pattern="\d{6}"
                />
              </div>

              <div class="row mb-3">
                <div class="col-md-6">
                  <label for="date" class="form-label">Preferred Date</label>
                  <input
                    type="date"
                    class="form-control"
                    id="date"
                    v-model="requestForm.preferred_date"
                    required
                    :min="minDate"
                  />
                </div>
                <div class="col-md-6">
                  <label for="time" class="form-label">Preferred Time</label>
                  <select class="form-select" id="time" v-model="requestForm.preferred_time" required>
                    <option value="" disabled selected>Select a time</option>
                    <option value="morning">Morning (8:00 AM - 12:00 PM)</option>
                    <option value="afternoon">Afternoon (12:00 PM - 4:00 PM)</option>
                    <option value="evening">Evening (4:00 PM - 8:00 PM)</option>
                  </select>
                </div>
              </div>

              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Submit Request
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import AppLayout from '../../components/layout/AppLayout.vue';

export default {
  name: 'NewServiceRequest',
  components: {
    AppLayout
  },
  setup() {
    const store = useStore();
    const router = useRouter();
    const loading = ref(false);
    const error = ref('');
    const success = ref('');
    const services = ref([]);

    const requestForm = ref({
      service_id: '',
      description: '',
      address: '',
  pin_code: '',
      preferred_date: '',
      preferred_time: '',
      notes: ''
    });

    // Get minimum date (today)
    const minDate = computed(() => {
      const today = new Date();
      return today.toISOString().split('T')[0];
    });

    onMounted(async () => {
      try {
        // Fetch services
        const result = await store.dispatch('fetchServices');
        if (result.success) {
          services.value = result.services;
        }
      } catch (err) {
        error.value = 'Error loading services. Please try again.';
        console.error('Error fetching services:', err);
      }
    });

    const submitRequest = async () => {
      loading.value = true;
      error.value = '';
      success.value = '';

      try {
        const payload = {
          ...requestForm.value,
          location: requestForm.value.address,
          scheduled_date: requestForm.value.preferred_date,
          pin_code: requestForm.value.pin_code
        };
        const result = await store.dispatch('createServiceRequest', payload);
        if (result.success) {
          success.value = 'Service request submitted successfully!';
          // Reset form
          requestForm.value = {
            service_id: '',
            description: '',
            address: '',
            pin_code: '',
            preferred_date: '',
            preferred_time: '',
            notes: ''
          };
          
          // Redirect to service requests page after 2 seconds
          setTimeout(() => {
            router.push('/customer/service-requests');
          }, 2000);
        } else {
          error.value = result.error || 'Failed to submit service request. Please try again.';
        }
      } catch (err) {
        error.value = 'An error occurred. Please try again.';
        console.error('Error submitting service request:', err);
      } finally {
        loading.value = false;
      }
    };

    return {
      requestForm,
      loading,
      error,
      success,
      services,
      minDate,
      submitRequest
    };
  }
};
</script>
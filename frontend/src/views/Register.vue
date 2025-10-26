<template>
  <AppLayout>
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-6">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">Register</h4>
          </div>
          <div class="card-body">
            <div v-if="error" class="alert alert-danger" role="alert">
              {{ error }}
            </div>
            <div v-if="success" class="alert alert-success" role="alert">
              {{ success }}
            </div>

            <!-- Registration Type Selection -->
            <div class="mb-4" v-if="!registrationType">
              <!-- <h5 class="mb-3">I want to register as:</h5> -->
              <div class="d-grid gap-3">
                <button @click="registrationType = 'customer'" class="btn btn-outline-primary p-3">
                  <i class="bi bi-person-fill fs-4 mb-2"></i>
                  <div>Customer</div>
                  <small class="text-muted">Find professionals for your household needs</small>
                </button>
                <button @click="registrationType = 'professional'" class="btn btn-outline-primary p-3">
                  <i class="bi bi-tools fs-4 mb-2"></i>
                  <div>Professional</div>
                  <small class="text-muted">Offer your services to customers</small>
                </button>
              </div>
            </div>

            <!-- Customer Registration Form -->
            <form v-if="registrationType === 'customer'" @submit.prevent="registerCustomer">
              <div class="mb-3">
                <label for="name" class="form-label">Full Name</label>
                <input
                  type="text"
                  class="form-control"
                  id="name"
                  v-model="customerForm.name"
                  required
                />
              </div>
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input
                  type="email"
                  class="form-control"
                  id="email"
                  v-model="customerForm.email"
                  required
                />
              </div>
              <div class="mb-3">
                <label for="phone" class="form-label">Phone Number</label>
                <input
                  type="tel"
                  class="form-control"
                  id="phone"
                  v-model="customerForm.phone"
                  required
                  placeholder="+1XXXXXXXXXX"
                />
              </div>
              <div class="mb-3">
                <label for="location" class="form-label">Location</label>
                <input
                  type="text"
                  class="form-control"
                  id="location"
                  v-model="customerForm.location"
                  required
                />
              </div>
              <div class="mb-3">
                <label for="pincode" class="form-label">Pincode</label>
                <input
                  type="text"
                  class="form-control"
                  id="pincode"
                  v-model="customerForm.pincode"
                  required
                  maxlength="5"
                  pattern="[0-9]{5}"
                  placeholder="5-digit pincode"
                />
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input
                  type="password"
                  class="form-control"
                  id="password"
                  v-model="customerForm.password"
                  required
                  minlength="8"
                />
                <small class="form-text text-muted">
                  Password must be at least 8 characters long, include at least one uppercase letter and one number.
                </small>
              </div>
              <div class="mb-3">
                <label for="confirmPassword" class="form-label">Confirm Password</label>
                <input
                  type="password"
                  class="form-control"
                  id="confirmPassword"
                  v-model="customerForm.confirmPassword"
                  required
                />
              </div>
              <div class="d-flex justify-content-between">
                <button type="button" class="btn btn-outline-secondary" @click="registrationType = null">
                  Back
                </button>
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Register
                </button>
              </div>
            </form>

            <!-- Professional Registration Form -->
            <form v-if="registrationType === 'professional'" @submit.prevent="registerProfessional">
              <div class="mb-3">
                <label for="proName" class="form-label">Full Name</label>
                <input
                  type="text"
                  class="form-control"
                  id="proName"
                  v-model="professionalForm.name"
                  required
                />
              </div>
              <div class="mb-3">
                <label for="proEmail" class="form-label">Email</label>
                <input
                  type="email"
                  class="form-control"
                  id="proEmail"
                  v-model="professionalForm.email"
                  required
                />
              </div>
              <div class="mb-3">
                <label for="proPhone" class="form-label">Phone Number</label>
                <input
                  type="tel"
                  class="form-control"
                  id="proPhone"
                  v-model="professionalForm.phone"
                  required
                  placeholder="+1XXXXXXXXXX"
                />
              </div>
              <div class="mb-3">
                <label for="service" class="form-label">Service Type</label>
                <select class="form-select" id="service" v-model="professionalForm.service_id" required>
                  <option value="" disabled selected>Select a service</option>
                  <option v-for="service in services" :key="service.id" :value="service.id">
                    {{ service.name }}
                  </option>
                </select>
              </div>
              <div class="mb-3">
                <label for="experience" class="form-label">Years of Experience</label>
                <input
                  type="number"
                  class="form-control"
                  id="experience"
                  v-model="professionalForm.experience_years"
                  required
                  min="0"
                  max="50"
                  step="0.5"
                />
              </div>
              <div class="mb-3">
                <label for="bio" class="form-label">Bio</label>
                <textarea
                  class="form-control"
                  id="bio"
                  v-model="professionalForm.bio"
                  rows="3"
                ></textarea>
              </div>
              <div class="mb-3">
                <label for="proLocation" class="form-label">Location</label>
                <input
                  type="text"
                  class="form-control"
                  id="proLocation"
                  v-model="professionalForm.location"
                  required
                />
              </div>
              <div class="mb-3">
                <label for="proPincode" class="form-label">Pincode</label>
                <input
                  type="text"
                  class="form-control"
                  id="proPincode"
                  v-model="professionalForm.pincode"
                  required
                  maxlength="5"
                  pattern="[0-9]{5}"
                  placeholder="5-digit pincode"
                />
              </div>
              <div class="mb-3">
                <label for="proPassword" class="form-label">Password</label>
                <input
                  type="password"
                  class="form-control"
                  id="proPassword"
                  v-model="professionalForm.password"
                  required
                  minlength="8"
                />
                <small class="form-text text-muted">
                  Password must be at least 8 characters long, include at least one uppercase letter and one number.
                </small>
              </div>
              <div class="mb-3">
                <label for="proConfirmPassword" class="form-label">Confirm Password</label>
                <input
                  type="password"
                  class="form-control"
                  id="proConfirmPassword"
                  v-model="professionalForm.confirmPassword"
                  required
                />
              </div>
              <div class="mb-3">
                <label class="form-label">Verification Documents</label>
                <div class="mb-3">
                  <label for="idProof" class="form-label">Government ID (PDF/Image)</label>
                  <input
                    type="file"
                    class="form-control"
                    id="idProof"
                    accept=".pdf,.jpg,.jpeg,.png"
                    @change="handleFileUpload($event, 'id_proof')"
                    required
                  >
                </div>
                <div class="mb-3">
                  <label for="certification" class="form-label">Professional Certification (PDF)</label>
                  <input
                    type="file"
                    class="form-control"
                    id="certification"
                    accept=".pdf"
                    @change="handleFileUpload($event, 'certification')"
                    required
                  >
                </div>
                <div class="mb-3">
                  <label for="license" class="form-label">Business License (Optional)</label>
                  <input
                    type="file"
                    class="form-control"
                    id="license"
                    accept=".pdf"
                    @change="handleFileUpload($event, 'license')"
                  >
                </div>
              </div>
              <div class="mb-3">
                <label for="proLocation" class="form-label">Location</label>
                <input
                  type="text"
                  class="form-control"
                  id="proLocation"
                  v-model="professionalForm.location"
                  required
                />
              </div>
              <div class="mb-3">
                <label for="proPincode" class="form-label">Pincode</label>
                <input
                  type="text"
                  class="form-control"
                  id="proPincode"
                  v-model="professionalForm.pincode"
                  required
                  maxlength="5"
                  pattern="[0-9]{5}"
                  placeholder="5-digit pincode"
                />
              </div>
              <div class="mb-3">
                <label for="proPassword" class="form-label">Password</label>
                <input
                  type="password"
                  class="form-control"
                  id="proPassword"
                  v-model="professionalForm.password"
                  required
                  minlength="8"
                />
                <small class="form-text text-muted">
                  Password must be at least 8 characters long, include at least one uppercase letter and one number.
                </small>
              </div>
              <div class="mb-3">
                <label for="proConfirmPassword" class="form-label">Confirm Password</label>
                <input
                  type="password"
                  class="form-control"
                  id="proConfirmPassword"
                  v-model="professionalForm.confirmPassword"
                  required
                />
              </div>
              <div class="d-flex justify-content-between">
                <button type="button" class="btn btn-outline-secondary" @click="registrationType = null">
                  Back
                </button>
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Register
                </button>
              </div>
            </form>

            <div class="mt-3 text-center" v-if="registrationType">
              <p>Already have an account? <router-link to="/login">Login here</router-link></p>
            </div>
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
import AppLayout from '../components/layout/AppLayout.vue';

export default {
  name: 'RegisterPage',
  components: {
    AppLayout
  },
  setup() {
    const store = useStore();
    const router = useRouter();

    const registrationType = ref(null);
    const loading = computed(() => store.getters.getLoading);
    const error = computed(() => store.getters.getError);
    const success = ref('');
    const services = ref([]);

    const customerForm = ref({
      name: '',
      email: '',
      phone: '',
      location: '',
      pincode: '',
      password: '',
      confirmPassword: '',
      role: 'CUSTOMER'
    });

    const professionalForm = ref({
      name: '',
      email: '',
      phone: '',
      service_id: '',
      experience_years: 0,
      bio: '',
      location: '',
      pincode: '',
      password: '',
      confirmPassword: '',
      role: 'PROFESSIONAL',
      documents: []
    });

    // Fetch services for professional registration
    onMounted(async () => {
      try {
        const result = await store.dispatch('fetchServices');
        if (result.success) {
          services.value = result.services;
        }
      } catch (err) {
        console.error('Error fetching services:', err);
      }
    });

    const validatePassword = (password, confirmPassword) => {
      if (password !== confirmPassword) {
        store.commit('SET_ERROR', 'Passwords do not match');
        return false;
      }
      
      // Check password requirements
      if (password.length < 8) {
        store.commit('SET_ERROR', 'Password must be at least 8 characters long');
        return false;
      }
      
      if (!/[A-Z]/.test(password)) {
        store.commit('SET_ERROR', 'Password must contain at least one uppercase letter');
        return false;
      }
      
      if (!/[0-9]/.test(password)) {
        store.commit('SET_ERROR', 'Password must contain at least one number');
        return false;
      }
      
      return true;
    };

    const registerCustomer = async () => {
      // Validate passwords
      if (!validatePassword(customerForm.value.password, customerForm.value.confirmPassword)) {
        return;
      }
      
      // Clear any previous errors
      store.commit('SET_ERROR', null);
      
      // Create registration data
      const userData = {
        name: customerForm.value.name,
        email: customerForm.value.email,
        phone: customerForm.value.phone,
        password_hash: customerForm.value.password,
        role: customerForm.value.role,
        location: customerForm.value.location,
        pincode: customerForm.value.pincode
      };
      
      const result = await store.dispatch('register', userData);
      
      if (result.success) {
        success.value = 'Registration successful! You can now login.';
        // Reset form
        customerForm.value = {
          name: '',
          email: '',
          phone: '',
          location: '',
          pincode: '',
          password: '',
          confirmPassword: '',
          role: 'CUSTOMER'
        };
        
        // Redirect to login after 2 seconds
        setTimeout(() => {
          router.push('/login');
        }, 2000);
      }
    };

    const handleFileUpload = (event, documentType) => {
      const file = event.target.files[0];
      if (file) {
        // Store the file with its document type
        professionalForm.value.documents.push({
          file: file,
          document_type: documentType
        });
      }
    };

    const registerProfessional = async () => {
      // Validate passwords
      if (!validatePassword(professionalForm.value.password, professionalForm.value.confirmPassword)) {
        return;
      }
      
      // Clear any previous errors
      store.commit('SET_ERROR', null);
      
      // Create a FormData object directly instead of a regular object
      const formData = new FormData();
      
      // Add basic professional data
      formData.append('name', professionalForm.value.name);
      formData.append('email', professionalForm.value.email);
      formData.append('phone', professionalForm.value.phone);
      formData.append('password_hash', professionalForm.value.password);
      formData.append('role', professionalForm.value.role);
      formData.append('service_id', parseInt(professionalForm.value.service_id));
      formData.append('experience_years', parseFloat(professionalForm.value.experience_years));
      formData.append('bio', professionalForm.value.bio || '');
      formData.append('location', professionalForm.value.location);
      formData.append('pincode', professionalForm.value.pincode);
      
      // Add document files to the form data
      // The backend expects files in request.files.getlist('documents')
      if (professionalForm.value.documents.length > 0) {
        // Store the document type for the first file (backend currently uses one type for all files)
        formData.append('document_type', professionalForm.value.documents[0].document_type);
        
        // Add each document file with the same field name 'documents'
        // This will create an array of files in request.files.getlist('documents')
        professionalForm.value.documents.forEach(doc => {
          formData.append('documents', doc.file);
        });
      }
      
      // Send the form data directly to the backend
      const result = await store.dispatch('registerProfessional', formData);
      
      if (result.success) {
        success.value = 'Professional registration successful! Your account will be verified by an admin before you can start accepting service requests.';
        // Reset form
        professionalForm.value = {
          name: '',
          email: '',
          phone: '',
          service_id: '',
          experience_years: 0,
          bio: '',
          location: '',
          pincode: '',
          password: '',
          confirmPassword: '',
          role: 'PROFESSIONAL',
          documents: []
        };
        
        // Redirect to login after 2 seconds
        setTimeout(() => {
          router.push('/login');
        }, 2000);
      }
    };
    return {
      registrationType,
      loading,
      error,
      success,
      services,
      customerForm,
      professionalForm,
      registerCustomer,
      registerProfessional,
      handleFileUpload
    };
  }
}
</script>
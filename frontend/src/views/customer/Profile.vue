<template>
  <AppLayout>
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">My Profile</h4>
          </div>
          <div class="card-body">
            <div v-if="error" class="alert alert-danger" role="alert">
              {{ error }}
            </div>
            <div v-if="success" class="alert alert-success" role="alert">
              {{ success }}
            </div>

            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <form v-else @submit.prevent="updateProfile">
              <div class="mb-3">
                <label for="name" class="form-label">Full Name</label>
                <input
                  type="text"
                  class="form-control"
                  id="name"
                  v-model="profileForm.name"
                  required
                />
              </div>
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input
                  type="email"
                  class="form-control"
                  id="email"
                  v-model="profileForm.email"
                  required
                  disabled
                />
                <small class="form-text text-muted">Email cannot be changed</small>
              </div>
              <div class="mb-3">
                <label for="phone" class="form-label">Phone Number</label>
                <input
                  type="tel"
                  class="form-control"
                  id="phone"
                  v-model="profileForm.phone"
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
                  v-model="profileForm.location"
                  required
                />
              </div>
              <div class="mb-3">
                <label for="pincode" class="form-label">Pincode</label>
                <input
                  type="text"
                  class="form-control"
                  id="pincode"
                  v-model="profileForm.pincode"
                  required
                  maxlength="5"
                  pattern="[0-9]{5}"
                  placeholder="5-digit pincode"
                />
              </div>

              <hr class="my-4" />

              <h5 class="mb-3">Change Password (Optional)</h5>
              <div class="mb-3">
                <label for="currentPassword" class="form-label">Current Password</label>
                <input
                  type="password"
                  class="form-control"
                  id="currentPassword"
                  v-model="passwordForm.currentPassword"
                />
              </div>
              <div class="mb-3">
                <label for="newPassword" class="form-label">New Password</label>
                <input
                  type="password"
                  class="form-control"
                  id="newPassword"
                  v-model="passwordForm.newPassword"
                  minlength="8"
                />
                <small class="form-text text-muted">
                  Password must be at least 8 characters long, include at least one uppercase letter and one number.
                </small>
              </div>
              <div class="mb-3">
                <label for="confirmPassword" class="form-label">Confirm New Password</label>
                <input
                  type="password"
                  class="form-control"
                  id="confirmPassword"
                  v-model="passwordForm.confirmPassword"
                />
              </div>

              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary" :disabled="updating">
                  <span v-if="updating" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Update Profile
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
import AppLayout from '../../components/layout/AppLayout.vue';

export default {
  name: 'CustomerProfile',
  components: {
    AppLayout
  },
  setup() {
    const store = useStore();
    const loading = ref(true);
    const updating = ref(false);
    const error = ref('');
    const success = ref('');

    const profileForm = ref({
      name: '',
      email: '',
      phone: '',
      location: '',
      pincode: ''
    });

    const passwordForm = ref({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });

    const user = computed(() => store.getters.currentUser);

    onMounted(async () => {
      try {
        // Fetch user profile
        const result = await store.dispatch('fetchUserProfile');
        if (result.success) {
          // Populate form with user data
          profileForm.value.name = result.user.name;
          profileForm.value.email = result.user.email;
          profileForm.value.phone = result.user.phone;
          
          // Get customer-specific data
          if (result.user.customer) {
            profileForm.value.location = result.user.customer.location;
            profileForm.value.pincode = result.user.customer.pincode;
          }
        }
      } catch (err) {
        error.value = 'Error loading profile. Please try again.';
        console.error('Error fetching profile:', err);
      } finally {
        loading.value = false;
      }
    });

    const validatePassword = () => {
      // Check if password fields are filled
      if (!passwordForm.value.currentPassword && !passwordForm.value.newPassword && !passwordForm.value.confirmPassword) {
        return true; // Password change not requested
      }

      // Check if all password fields are filled
      if (!passwordForm.value.currentPassword || !passwordForm.value.newPassword || !passwordForm.value.confirmPassword) {
        error.value = 'All password fields are required to change password';
        return false;
      }

      // Check if passwords match
      if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
        error.value = 'New passwords do not match';
        return false;
      }

      // Check password requirements
      if (passwordForm.value.newPassword.length < 8) {
        error.value = 'Password must be at least 8 characters long';
        return false;
      }

      if (!/[A-Z]/.test(passwordForm.value.newPassword)) {
        error.value = 'Password must contain at least one uppercase letter';
        return false;
      }

      if (!/[0-9]/.test(passwordForm.value.newPassword)) {
        error.value = 'Password must contain at least one number';
        return false;
      }

      return true;
    };

    const updateProfile = async () => {
      error.value = '';
      success.value = '';
      updating.value = true;

      try {
        // Validate password if changing
        if (!validatePassword()) {
          updating.value = false;
          return;
        }

        // Update profile
        const profileData = {
          name: profileForm.value.name,
          phone: profileForm.value.phone,
          location: profileForm.value.location,
          pincode: profileForm.value.pincode
        };

        const result = await store.dispatch('updateUserProfile', profileData);

        // Change password if requested
        if (passwordForm.value.currentPassword && passwordForm.value.newPassword) {
          const passwordResult = await store.dispatch('changePassword', {
            currentPassword: passwordForm.value.currentPassword,
            newPassword: passwordForm.value.newPassword
          });

          if (!passwordResult.success) {
            error.value = passwordResult.error || 'Failed to update password';
            updating.value = false;
            return;
          }

          // Reset password form
          passwordForm.value = {
            currentPassword: '',
            newPassword: '',
            confirmPassword: ''
          };
        }

        if (result.success) {
          success.value = 'Profile updated successfully';
        } else {
          error.value = result.error || 'Failed to update profile';
        }
      } catch (err) {
        error.value = 'An error occurred. Please try again.';
        console.error('Error updating profile:', err);
      } finally {
        updating.value = false;
      }
    };

    return {
      profileForm,
      passwordForm,
      loading,
      updating,
      error,
      success,
      updateProfile
    };
  }
};
</script>
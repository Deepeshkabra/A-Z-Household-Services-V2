<template>
  <AppLayout>
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">Login</h4>
          </div>
          <div class="card-body">
            <div v-if="error" class="alert alert-danger" role="alert">
              {{ error }}
            </div>
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input
                  type="email"
                  class="form-control"
                  id="email"
                  v-model="credentials.email"
                  required
                  autocomplete="email"
                />
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input
                  type="password"
                  class="form-control"
                  id="password"
                  v-model="credentials.password"
                  required
                  autocomplete="current-password"
                />
              </div>
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Login
                </button>
              </div>
            </form>
            <div class="mt-3 text-center">
              <p>Don't have an account? <router-link to="/register">Register here</router-link></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import AppLayout from '../components/layout/AppLayout.vue';

export default {
  name: 'LoginPage',
  components: {
    AppLayout
  },
  setup() {
    const store = useStore();
    const router = useRouter();

    const credentials = ref({
      email: '',
      password: ''
    });

    const loading = computed(() => store.getters.getLoading);
    const error = computed(() => store.getters.getError);

    const handleLogin = async () => {
      const result = await store.dispatch('login', credentials.value);
      if (result.success) {
        // Redirect based on user role
        if (result.role === 'ADMIN') {
          router.push('/admin/dashboard');
        } else if (result.role === 'PROFESSIONAL') {
          router.push('/professional/dashboard');
        } else {
          router.push('/customer/dashboard');
        }
      }
    };

    return {
      credentials,
      loading,
      error,
      handleLogin
    };
  }
};
</script>
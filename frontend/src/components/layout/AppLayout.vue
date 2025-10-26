<template>
  <div class="app-container">
    <header class="app-header">
      <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
          <router-link class="navbar-brand" to="/">
            <strong>A to Z Household Services</strong>
          </router-link>
          <button
            class="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarNav"
            aria-controls="navbarNav"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav me-auto">
              <li class="nav-item">
                <router-link class="nav-link" to="/">Home</router-link>
              </li>
              <li class="nav-item" v-if="isAuthenticated && isCustomer">
                <router-link class="nav-link" to="/customer/dashboard">Dashboard</router-link>
              </li>
              <li class="nav-item" v-if="isAuthenticated && isProfessional">
                <router-link class="nav-link" to="/professional/dashboard">Dashboard</router-link>
              </li>
              <li class="nav-item" v-if="isAuthenticated && isAdmin">
                <router-link class="nav-link" to="/admin/dashboard">Dashboard</router-link>
              </li>
              <li class="nav-item" v-if="isAuthenticated && isCustomer">
                <router-link class="nav-link" to="/customer/service-requests">My Requests</router-link>
              </li>
              <li class="nav-item" v-if="isAuthenticated && isProfessional">
                <router-link class="nav-link" to="/professional/service-requests">Service Requests</router-link>
              </li>
            </ul>
            <ul class="navbar-nav">
              <template v-if="!isAuthenticated">
                <li class="nav-item">
                  <router-link class="nav-link" to="/login">Login</router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/register">Register</router-link>
                </li>
              </template>
              <template v-else>
                <li class="nav-item dropdown">
                  <a
                    class="nav-link dropdown-toggle"
                    href="#"
                    id="navbarDropdown"
                    role="button"
                    data-bs-toggle="dropdown"
                    aria-expanded="false"
                  >
                    {{ currentUser ? currentUser.name : 'Account' }}
                  </a>
                  <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
                    <li v-if="isCustomer">
                      <router-link class="dropdown-item" to="/customer/profile">Profile</router-link>
                    </li>
                    <li v-if="isProfessional">
                      <router-link class="dropdown-item" to="/professional/profile">Profile</router-link>
                    </li>
                    <li>
                      <hr class="dropdown-divider" />
                    </li>
                    <li>
                      <a class="dropdown-item" href="#" @click.prevent="logout">Logout</a>
                    </li>
                  </ul>
                </li>
              </template>
            </ul>
          </div>
        </div>
      </nav>
    </header>

    <main class="app-content">
      <div class="container py-4">
        <slot></slot>
      </div>
    </main>

    <footer class="app-footer bg-light py-4 mt-auto">
      <div class="container">
        <div class="row">
          <div class="col-md-6">
            <h5>A to Z Household Services</h5>
            <p>Your one-stop solution for all household services</p>
          </div>
          <div class="col-md-3">
            <h6>Quick Links</h6>
            <ul class="list-unstyled">
              <li><router-link to="/">Home</router-link></li>
              <li><router-link to="/login">Login</router-link></li>
              <li><router-link to="/register">Register</router-link></li>
            </ul>
          </div>
          <div class="col-md-3">
            <h6>Contact Us</h6>
            <address>
              <p>Email: info@atozhousehold.com</p>
              <p>Phone: (123) 456-7890</p>
            </address>
          </div>
        </div>
        <div class="row mt-3">
          <div class="col-12 text-center">
            <p class="mb-0">&copy; {{ new Date().getFullYear() }} A to Z Household Services. All rights reserved.</p>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'AppLayout',
  setup() {
    const store = useStore();
    const router = useRouter();

    const isAuthenticated = computed(() => store.getters.isAuthenticated);
    const isAdmin = computed(() => store.getters.isAdmin);
    const isProfessional = computed(() => store.getters.isProfessional);
    const isCustomer = computed(() => store.getters.isCustomer);
    const currentUser = computed(() => store.getters.currentUser);

    const logout = async () => {
      await store.dispatch('logout');
      router.push('/login');
    };

    return {
      isAuthenticated,
      isAdmin,
      isProfessional,
      isCustomer,
      currentUser,
      logout
    };
  }
};
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-content {
  flex: 1;
}

.app-footer a {
  color: #495057;
  text-decoration: none;
}

.app-footer a:hover {
  color: #0d6efd;
  text-decoration: underline;
}
</style>
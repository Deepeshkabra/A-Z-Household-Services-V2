<template>
  <AppLayout>
    <div class="text-center py-5">
      <div class="display-1 text-muted mb-3">404</div>
      <h1 class="h2 mb-4">Page Not Found</h1>
      <p class="lead mb-5">The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.</p>
      <router-link to="/" class="btn btn-primary">
        <i class="bi bi-house-door me-2"></i> Back to Home
      </router-link>
    </div>
  </AppLayout>
</template>

<script>
import AppLayout from '../components/layout/AppLayout.vue';

export default {
  name: 'NotFoundPage',
  components: {
    AppLayout
  }
};
</script>
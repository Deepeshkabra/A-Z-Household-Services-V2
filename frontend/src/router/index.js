import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/customer/dashboard',
    name: 'CustomerDashboard',
    component: () => import('../views/customer/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'CUSTOMER' }
  },
  {
    path: '/customer/service-requests',
    name: 'CustomerServiceRequests',
    component: () => import('../views/customer/ServiceRequests.vue'),
    meta: { requiresAuth: true, role: 'CUSTOMER' }
  },
  {
    path: '/customer/new-request',
    name: 'NewServiceRequest',
    component: () => import('../views/customer/NewRequest.vue'),
    meta: { requiresAuth: true, role: 'CUSTOMER' }
  },
  {
    path: '/customer/profile',
    name: 'CustomerProfile',
    component: () => import('../views/customer/Profile.vue'),
    meta: { requiresAuth: true, role: 'CUSTOMER' }
  },
  {
    path: '/professional/dashboard',
    name: 'ProfessionalDashboard',
    component: () => import('../views/professional/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'PROFESSIONAL' }
  },
  {
    path: '/professional/service-requests',
    name: 'ProfessionalServiceRequests',
    component: () => import('../views/professional/ServiceRequests.vue'),
    meta: { requiresAuth: true, role: 'PROFESSIONAL' }
  },
  {
    path: '/professional/profile',
    name: 'ProfessionalProfile',
    component: () => import('../views/professional/Profile.vue'),
    meta: { requiresAuth: true, role: 'PROFESSIONAL' }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('../views/admin/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },
  {
    path: '/admin/professionals',
    name: 'AdminProfessionals',
    component: () => import('../views/admin/Professionals.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },
  {
    path: '/admin/customers',
    name: 'AdminCustomers',
    component: () => import('../views/admin/Customers.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },
  {
    path: '/admin/service-requests',
    name: 'AdminServiceRequests',
    component: () => import('../views/admin/ServiceRequests.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },
  {
    path: '/admin/services',
    name: 'AdminServices',
    component: () => import('../views/admin/Services.vue'),
    meta: { requiresAuth: true, role: 'ADMIN' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const role = to.matched.find(record => record.meta.role)?.meta.role;
  
  // Get auth status from localStorage
  const isAuthenticated = localStorage.getItem('token');
  const userRole = localStorage.getItem('userRole');
  
  if (requiresAuth && !isAuthenticated) {
    next('/login');
  } else if (requiresAuth && role && role !== userRole) {
    // Redirect to appropriate dashboard based on role
    if (userRole === 'ADMIN') {
      next('/admin/dashboard');
    } else if (userRole === 'PROFESSIONAL') {
      next('/professional/dashboard');
    } else if (userRole === 'CUSTOMER') {
      next('/customer/dashboard');
    } else {
      next('/login');
    }
  } else {
    next();
  }
});

export default router;
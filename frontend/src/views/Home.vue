<template>
  <AppLayout>
    <div class="home-page">
      <!-- Hero Section -->
      <section class="hero-section bg-primary text-white py-5">
        <div class="container">
          <div class="row align-items-center">
            <div class="col-lg-6">
              <h1 class="display-4 fw-bold mb-4">Your One-Stop Solution for Household Services</h1>
              <p class="lead mb-4">Find reliable professionals for all your household needs - from plumbing and electrical work to cleaning and gardening services.</p>
              <div class="d-grid gap-2 d-md-flex justify-content-md-start">
                <router-link to="/register" class="btn btn-light btn-lg px-4 me-md-2">Get Started</router-link>
                <a href="#services" class="btn btn-outline-light btn-lg px-4">Our Services</a>
              </div>
            </div>
            <div class="col-lg-6 d-none d-lg-block">
              <img src="/img/hero-image.svg" alt="Household Services" class="img-fluid rounded shadow-lg" />
            </div>
          </div>
        </div>
      </section>

      <!-- Services Section -->
      <section id="services" class="services-section py-5">
        <div class="container">
          <div class="text-center mb-5">
            <h2 class="fw-bold">Our Services</h2>
            <p class="lead text-muted">We offer a wide range of professional household services</p>
          </div>

          <div class="row g-4">
            <div class="col-md-4">
              <div class="card h-100 border-0 shadow-sm">
                <div class="card-body text-center p-4">
                  <div class="icon-box mb-3">
                    <i class="bi bi-tools fs-1 text-primary"></i>
                  </div>
                  <h5 class="card-title">Plumbing Services</h5>
                  <p class="card-text">Professional plumbing services for repairs, installations, and maintenance.</p>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="card h-100 border-0 shadow-sm">
                <div class="card-body text-center p-4">
                  <div class="icon-box mb-3">
                    <i class="bi bi-lightning-charge fs-1 text-primary"></i>
                  </div>
                  <h5 class="card-title">Electrical Work</h5>
                  <p class="card-text">Certified electricians for all your electrical needs and installations.</p>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="card h-100 border-0 shadow-sm">
                <div class="card-body text-center p-4">
                  <div class="icon-box mb-3">
                    <i class="bi bi-brush fs-1 text-primary"></i>
                  </div>
                  <h5 class="card-title">Cleaning Services</h5>
                  <p class="card-text">Professional cleaning services for homes and commercial spaces.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- How It Works Section -->
      <section class="how-it-works-section py-5 bg-light">
        <div class="container">
          <div class="text-center mb-5">
            <h2 class="fw-bold">How It Works</h2>
            <p class="lead text-muted">Simple steps to get your service request fulfilled</p>
          </div>

          <div class="row g-4">
            <div class="col-md-4">
              <div class="card h-100 border-0 shadow-sm">
                <div class="card-body text-center p-4">
                  <div class="step-number mb-3">1</div>
                  <h5 class="card-title">Create an Account</h5>
                  <p class="card-text">Register as a customer to access our services or as a professional to offer your skills.</p>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="card h-100 border-0 shadow-sm">
                <div class="card-body text-center p-4">
                  <div class="step-number mb-3">2</div>
                  <h5 class="card-title">Request a Service</h5>
                  <p class="card-text">Submit your service request with details about the job and your requirements.</p>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="card h-100 border-0 shadow-sm">
                <div class="card-body text-center p-4">
                  <div class="step-number mb-3">3</div>
                  <h5 class="card-title">Get it Done</h5>
                  <p class="card-text">Our professionals will complete your service request efficiently and professionally.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Testimonials Section -->
      <section class="testimonials-section py-5">
        <div class="container">
          <div class="text-center mb-5">
            <h2 class="fw-bold">What Our Customers Say</h2>
            <p class="lead text-muted">Hear from our satisfied customers</p>
          </div>

          <div class="row g-4">
            <div class="col-md-4">
              <div class="card h-100 border-0 shadow-sm">
                <div class="card-body p-4">
                  <div class="d-flex align-items-center mb-3">
                    <div class="rating text-warning me-2">
                      <i class="bi bi-star-fill"></i>
                      <i class="bi bi-star-fill"></i>
                      <i class="bi bi-star-fill"></i>
                      <i class="bi bi-star-fill"></i>
                      <i class="bi bi-star-fill"></i>
                    </div>
                    <span class="text-muted">5.0</span>
                  </div>
                  <p class="card-text mb-3">"The plumber was very professional and fixed our leaking pipe quickly. Great service!"</p>
                  <div class="d-flex align-items-center">
                    <div class="avatar me-3">JD</div>
                    <div>
                      <h6 class="mb-0">John Doe</h6>
                      <small class="text-muted">Plumbing Service</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="card h-100 border-0 shadow-sm">
                <div class="card-body p-4">
                  <div class="d-flex align-items-center mb-3">
                    <div class="rating text-warning me-2">
                      <i class="bi bi-star-fill"></i>
                      <i class="bi bi-star-fill"></i>
                      <i class="bi bi-star-fill"></i>
                      <i class="bi bi-star-fill"></i>
                      <i class="bi bi-star-half"></i>
                    </div>
                    <span class="text-muted">4.5</span>
                  </div>
                  <p class="card-text mb-3">"The cleaning service was thorough and efficient. My house has never looked better!"</p>
                  <div class="d-flex align-items-center">
                    <div class="avatar me-3">JS</div>
                    <div>
                      <h6 class="mb-0">Jane Smith</h6>
                      <small class="text-muted">Cleaning Service</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="card h-100 border-0 shadow-sm">
                <div class="card-body p-4">
                  <div class="d-flex align-items-center mb-3">
                    <div class="rating text-warning me-2">
                      <i class="bi bi-star-fill"></i>
                      <i class="bi bi-star-fill"></i>
                      <i class="bi bi-star-fill"></i>
                      <i class="bi bi-star-fill"></i>
                      <i class="bi bi-star-fill"></i>
                    </div>
                    <span class="text-muted">5.0</span>
                  </div>
                  <p class="card-text mb-3">"The electrician was knowledgeable and fixed our wiring issues promptly. Highly recommended!"</p>
                  <div class="d-flex align-items-center">
                    <div class="avatar me-3">RJ</div>
                    <div>
                      <h6 class="mb-0">Robert Johnson</h6>
                      <small class="text-muted">Electrical Service</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA Section -->
      <section class="cta-section py-5 bg-primary text-white">
        <div class="container">
          <div class="row align-items-center">
            <div class="col-lg-8 mx-auto text-center">
              <h2 class="fw-bold mb-4">Ready to Get Started?</h2>
              <p class="lead mb-4">Join our platform today and experience the best household services.</p>
              <div class="d-grid gap-2 d-sm-flex justify-content-sm-center">
                <router-link to="/register" class="btn btn-light btn-lg px-4 me-sm-3">Register Now</router-link>
                <router-link to="/login" class="btn btn-outline-light btn-lg px-4">Login</router-link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </AppLayout>
</template>

<script>
import AppLayout from '../components/layout/AppLayout.vue';

export default {
  name: 'HomePage',
  components: {
    AppLayout
  }
};
</script>

<style scoped>
.hero-section {
  padding: 5rem 0;
  background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%);
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #0d6efd;
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #0d6efd;
  color: white;
  font-weight: bold;
}

.rating i {
  color: #ffc107;
}

@media (max-width: 768px) {
  .hero-section {
    padding: 3rem 0;
  }
}
</style>
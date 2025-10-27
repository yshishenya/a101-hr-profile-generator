<template>
  <v-container fluid class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card
          elevation="8"
          rounded="lg"
          max-width="400"
          class="mx-auto"
        >
          <v-card-text class="pa-8">
            <!-- Logo and Title -->
            <div class="text-center mb-6">
              <v-icon size="48" color="primary" class="mb-4">
                mdi-office-building
              </v-icon>
              <h1 class="text-h5 font-weight-bold mb-2">
                A101 HR Profile Generator
              </h1>
              <p class="text-subtitle-1 text-medium-emphasis">
                Sign in to continue
              </p>
            </div>

            <!-- Error Alert -->
            <v-alert
              v-if="authStore.error"
              type="error"
              variant="tonal"
              closable
              class="mb-4"
              @click:close="clearError"
            >
              {{ authStore.error }}
            </v-alert>

            <!-- Login Form -->
            <v-form ref="form" @submit.prevent="handleLogin">
              <!-- Username Field -->
              <v-text-field
                v-model="username"
                label="Username"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                :rules="usernameRules"
                :disabled="loading"
                autofocus
                class="mb-4"
                @input="clearError"
              />

              <!-- Password Field -->
              <v-text-field
                v-model="password"
                label="Password"
                prepend-inner-icon="mdi-lock"
                :type="showPassword ? 'text' : 'password'"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                variant="outlined"
                :rules="passwordRules"
                :disabled="loading"
                class="mb-2"
                @click:append-inner="showPassword = !showPassword"
                @input="clearError"
              />

              <!-- Remember Me Checkbox -->
              <v-checkbox
                v-model="rememberMe"
                label="Remember me"
                :disabled="loading"
                color="primary"
                class="mb-4"
                hide-details
              />

              <!-- Login Button -->
              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="loading"
                :disabled="loading"
                class="mt-6"
              >
                Sign In
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Router and store
const router = useRouter()
const authStore = useAuthStore()

// Form ref
const form = ref()

// Form fields
const username = ref('')
const password = ref('')
const rememberMe = ref(false)
const loading = ref(false)
const showPassword = ref(false)

// Validation rules
const usernameRules = [
  (v: string) => !!v || 'Username is required'
]

const passwordRules = [
  (v: string) => !!v || 'Password is required',
  (v: string) => v.length >= 6 || 'Password must be at least 6 characters'
]

/**
 * Clear error message when user starts typing
 */
function clearError(): void {
  authStore.clearError()
}

/**
 * Handle login form submission
 */
async function handleLogin(): Promise<void> {
  // Validate form
  const { valid } = await form.value.validate()
  if (!valid) return

  // Set loading state
  loading.value = true

  try {
    // Attempt login
    const success = await authStore.login({
      username: username.value,
      password: password.value,
      remember_me: rememberMe.value
    })

    if (success) {
      // Clear password on success
      password.value = ''

      // Redirect to requested page or dashboard
      const redirect = router.currentRoute.value.query.redirect as string || '/'
      await router.push(redirect)
    } else {
      // Clear password on error and refocus
      password.value = ''
      // Focus will be handled by the form validation
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
}
</style>

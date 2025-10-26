import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

/**
 * Application routes configuration
 *
 * Route structure:
 * - /login: Public authentication page
 * - /: Protected app layout with nested routes
 *   - Dashboard (index): Main dashboard view
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: {
      requiresAuth: false,
      title: 'Login'
    }
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: {
          title: 'Dashboard'
        }
      },
      {
        path: 'generator',
        name: 'Generator',
        component: () => import('@/views/GeneratorView.vue'),
        meta: {
          title: 'Profile Generator'
        }
      }
    ]
  },
  {
    // Catch-all route for 404
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/'
  }
]

/**
 * Router instance with history mode
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

/**
 * Global navigation guard for authentication
 *
 * Logic:
 * 1. Ensure auth is initialized (safe to call multiple times)
 * 2. Check if route requires authentication (meta.requiresAuth)
 * 3. If protected route and user not authenticated → redirect to /login
 * 4. If /login and user already authenticated → redirect to /
 * 5. Otherwise allow navigation
 */
router.beforeEach(async (
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  const authStore = useAuthStore()

  // Ensure auth is initialized (handles page refresh case)
  // Safe to call multiple times - will only run once
  await authStore.initialize()

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)
  const isAuthenticated = authStore.isAuthenticated

  // Protected route without authentication
  if (requiresAuth && !isAuthenticated) {
    next({
      name: 'Login',
      query: { redirect: to.fullPath } // Save intended destination
    })
    return
  }

  // Login page when already authenticated
  if (to.name === 'Login' && isAuthenticated) {
    const redirect = to.query.redirect as string
    next(redirect || '/')
    return
  }

  // Allow navigation
  next()
})

/**
 * Set page title based on route meta
 */
router.afterEach((to: RouteLocationNormalized) => {
  const title = to.meta.title as string
  document.title = title ? `${title} - HR Profile Generator` : 'HR Profile Generator'
})

export default router

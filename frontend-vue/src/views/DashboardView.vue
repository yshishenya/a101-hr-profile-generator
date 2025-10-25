<template>
  <v-container fluid class="pa-6">
    <!-- Page Title -->
    <h1 class="text-h4 font-weight-bold mb-6">
      Dashboard
    </h1>

    <!-- Welcome Card -->
    <v-card elevation="2" rounded="lg" class="mb-6">
      <v-card-text class="pa-6">
        <div class="d-flex align-center">
          <v-icon size="48" color="primary" class="mr-4">
            mdi-hand-wave
          </v-icon>
          <div>
            <h2 class="text-h5 font-weight-medium mb-1">
              Welcome, {{ authStore.user?.full_name || 'User' }}!
            </h2>
            <p class="text-subtitle-1 text-medium-emphasis mb-0">
              Dashboard with statistics will be implemented in Week 3
            </p>
          </div>
        </div>
      </v-card-text>
    </v-card>

    <!-- Stats Cards Row -->
    <v-row>
      <!-- Total Positions Card -->
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" rounded="lg" class="pa-4">
          <div class="d-flex align-center mb-3">
            <v-icon size="40" color="primary" class="mr-3">
              mdi-briefcase-outline
            </v-icon>
            <div>
              <div class="text-h4 font-weight-bold">
                1,689
              </div>
              <div class="text-subtitle-2 text-medium-emphasis">
                Total Positions
              </div>
            </div>
          </div>
          <v-progress-linear
            color="primary"
            :model-value="100"
            height="4"
            rounded
          />
        </v-card>
      </v-col>

      <!-- Profiles Generated Card -->
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" rounded="lg" class="pa-4">
          <div class="d-flex align-center mb-3">
            <v-icon size="40" color="success" class="mr-3">
              mdi-account-check-outline
            </v-icon>
            <div>
              <div class="text-h4 font-weight-bold">
                0
              </div>
              <div class="text-subtitle-2 text-medium-emphasis">
                Profiles Generated
              </div>
            </div>
          </div>
          <v-progress-linear
            color="success"
            :model-value="0"
            height="4"
            rounded
          />
        </v-card>
      </v-col>

      <!-- Completion Card -->
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" rounded="lg" class="pa-4">
          <div class="d-flex align-center mb-3">
            <v-icon size="40" color="info" class="mr-3">
              mdi-chart-arc
            </v-icon>
            <div>
              <div class="text-h4 font-weight-bold">
                0%
              </div>
              <div class="text-subtitle-2 text-medium-emphasis">
                Completion
              </div>
            </div>
          </div>
          <v-progress-linear
            color="info"
            :model-value="0"
            height="4"
            rounded
          />
        </v-card>
      </v-col>

      <!-- Active Tasks Card -->
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" rounded="lg" class="pa-4">
          <div class="d-flex align-center mb-3">
            <v-icon size="40" color="warning" class="mr-3">
              mdi-clock-outline
            </v-icon>
            <div>
              <div class="text-h4 font-weight-bold">
                0
              </div>
              <div class="text-subtitle-2 text-medium-emphasis">
                Active Tasks
              </div>
            </div>
          </div>
          <v-progress-linear
            color="warning"
            :model-value="0"
            height="4"
            rounded
          />
        </v-card>
      </v-col>
    </v-row>

    <!-- Placeholder Content -->
    <v-row class="mt-6">
      <v-col cols="12" md="8">
        <v-card elevation="2" rounded="lg">
          <v-card-title class="pa-4">
            <v-icon class="mr-2">mdi-chart-line</v-icon>
            Recent Activity
          </v-card-title>
          <v-card-text class="pa-6">
            <div class="text-center py-12">
              <v-icon size="64" color="grey-lighten-1" class="mb-4">
                mdi-chart-timeline-variant
              </v-icon>
              <p class="text-subtitle-1 text-medium-emphasis">
                Activity chart will be displayed here
              </p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card elevation="2" rounded="lg">
          <v-card-title class="pa-4">
            <v-icon class="mr-2">mdi-format-list-bulleted</v-icon>
            Quick Actions
          </v-card-title>
          <v-card-text class="pa-4">
            <v-list lines="two" class="pa-0">
              <v-list-item
                prepend-icon="mdi-file-document-plus"
                title="Generate Profile"
                subtitle="Create a new employee profile"
                disabled
              />
              <v-list-item
                prepend-icon="mdi-magnify"
                title="Search Positions"
                subtitle="Find positions in catalog"
                disabled
              />
              <v-list-item
                prepend-icon="mdi-download"
                title="Export Data"
                subtitle="Download generated profiles"
                disabled
              />
              <v-list-item
                prepend-icon="mdi-cog"
                title="Settings"
                subtitle="Configure application"
                disabled
              />
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

// Access auth store for user info
const authStore = useAuthStore()
</script>

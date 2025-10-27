<template>
  <v-card variant="outlined" class="mb-4">
    <v-card-title class="d-flex align-center gap-2">
      <v-icon>mdi-calendar-clock</v-icon>
      Условия работы
    </v-card-title>

    <v-card-text>
      <!-- Work Schedule -->
      <v-text-field
        :model-value="workingConditions.work_schedule"
        variant="outlined"
        label="График работы"
        placeholder="Например: 5/2 с 9:00 до 18:00"
        density="comfortable"
        class="mb-4"
        :rules="scheduleRules"
        @update:model-value="updateSchedule"
      >
        <template #prepend-inner>
          <v-icon>mdi-clock-outline</v-icon>
        </template>
      </v-text-field>

      <!-- Remote Work Options -->
      <v-textarea
        :model-value="workingConditions.remote_work_options"
        variant="outlined"
        label="Возможности удалённой работы"
        placeholder="Например: Гибридный режим, 2-3 дня удалённо..."
        rows="2"
        auto-grow
        class="mb-4"
        :rules="remoteWorkRules"
        @update:model-value="updateRemoteWork"
      >
        <template #prepend-inner>
          <v-icon>mdi-home-account</v-icon>
        </template>
      </v-textarea>

      <!-- Business Travel -->
      <v-textarea
        :model-value="workingConditions.business_travel"
        variant="outlined"
        label="Командировки"
        placeholder="Например: Редкие командировки по РФ (до 10%)..."
        rows="2"
        auto-grow
        :rules="businessTravelRules"
        @update:model-value="updateBusinessTravel"
      >
        <template #prepend-inner>
          <v-icon>mdi-airplane</v-icon>
        </template>
      </v-textarea>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import {
  scheduleRules,
  remoteWorkRules,
  businessTravelRules,
} from '../constants/additionalInfoSuggestions'

// Types
interface WorkingConditions {
  work_schedule: string
  remote_work_options: string
  business_travel: string
}

// Props
interface Props {
  workingConditions: WorkingConditions
}

defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:schedule': [value: string]
  'update:remote-work': [value: string]
  'update:business-travel': [value: string]
}>()

// Methods
function updateSchedule(value: string): void {
  emit('update:schedule', value)
}

function updateRemoteWork(value: string): void {
  emit('update:remote-work', value)
}

function updateBusinessTravel(value: string): void {
  emit('update:business-travel', value)
}
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}
</style>

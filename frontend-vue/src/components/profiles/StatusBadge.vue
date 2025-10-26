<template>
  <v-chip
    :color="statusConfig.color"
    :variant="statusConfig.variant"
    size="small"
    class="status-badge"
  >
    <template #prepend>
      <v-icon v-if="status !== 'generating'" size="small">
        {{ statusConfig.icon }}
      </v-icon>
      <v-progress-circular
        v-else
        :model-value="progress"
        :size="16"
        :width="2"
        color="white"
      />
    </template>

    <span class="status-text">{{ statusConfig.label }}</span>

    <!-- Progress percentage for generating status -->
    <span v-if="status === 'generating' && progress !== undefined" class="ml-1">
      ({{ progress }}%)
    </span>
  </v-chip>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PositionStatus } from '@/types/unified'

// Props
interface Props {
  status: PositionStatus
  progress?: number
}

const props = defineProps<Props>()

// Status configuration
const statusConfig = computed(() => {
  switch (props.status) {
    case 'generated':
      return {
        label: 'Сгенерирован',
        icon: 'mdi-check-circle',
        color: 'success',
        variant: 'flat' as const
      }
    case 'not_generated':
      return {
        label: 'Не сгенерирован',
        icon: 'mdi-help-circle',
        color: 'grey',
        variant: 'outlined' as const
      }
    case 'generating':
      return {
        label: 'Генерируется',
        icon: 'mdi-clock-outline',
        color: 'warning',
        variant: 'flat' as const
      }
    default:
      return {
        label: 'Неизвестно',
        icon: 'mdi-alert-circle',
        color: 'error',
        variant: 'outlined' as const
      }
  }
})
</script>

<style scoped>
.status-badge {
  font-weight: 500;
  letter-spacing: 0.25px;
}

.status-text {
  font-size: 0.75rem;
}

/* Ensure consistent spacing */
.status-badge :deep(.v-chip__prepend) {
  margin-inline-end: 4px;
}
</style>

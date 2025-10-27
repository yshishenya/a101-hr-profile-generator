<template>
  <v-expansion-panels variant="accordion">
    <!-- Working Conditions -->
    <v-expansion-panel>
      <v-expansion-panel-title>
        <div class="d-flex align-center gap-2">
          <v-icon size="small">mdi-calendar-clock</v-icon>
          <span class="font-weight-medium">Условия работы</span>
        </div>
      </v-expansion-panel-title>

      <v-expansion-panel-text>
        <v-list lines="two" density="compact">
          <v-list-item prepend-icon="mdi-clock-outline">
            <v-list-item-title>График работы</v-list-item-title>
            <v-list-item-subtitle class="text-wrap mt-1">
              {{ workingConditions.work_schedule || 'Не указано' }}
            </v-list-item-subtitle>
          </v-list-item>

          <v-divider />

          <v-list-item prepend-icon="mdi-home-account">
            <v-list-item-title>Удалённая работа</v-list-item-title>
            <v-list-item-subtitle class="text-wrap mt-1">
              {{ workingConditions.remote_work_options || 'Не указано' }}
            </v-list-item-subtitle>
          </v-list-item>

          <v-divider />

          <v-list-item prepend-icon="mdi-airplane">
            <v-list-item-title>Командировки</v-list-item-title>
            <v-list-item-subtitle class="text-wrap mt-1">
              {{ workingConditions.business_travel || 'Не указано' }}
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-expansion-panel-text>
    </v-expansion-panel>

    <!-- Special Requirements -->
    <v-expansion-panel>
      <v-expansion-panel-title>
        <div class="d-flex align-center gap-2">
          <v-icon size="small">mdi-shield-check</v-icon>
          <span class="font-weight-medium">Особые требования</span>
          <v-chip size="x-small" variant="outlined">
            {{ specialRequirements.length }}
          </v-chip>
        </div>
      </v-expansion-panel-title>

      <v-expansion-panel-text>
        <v-list density="compact">
          <v-list-item
            v-for="(req, idx) in specialRequirements"
            :key="idx"
            class="px-0"
          >
            <template #prepend>
              <v-icon size="small" color="warning">mdi-alert-circle</v-icon>
            </template>
            <v-list-item-subtitle class="text-wrap">{{ req }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="specialRequirements.length === 0" class="px-0">
            <v-list-item-subtitle class="text-medium-emphasis">Нет требований</v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-expansion-panel-text>
    </v-expansion-panel>

    <!-- Risk Factors -->
    <v-expansion-panel>
      <v-expansion-panel-title>
        <div class="d-flex align-center gap-2">
          <v-icon size="small">mdi-alert</v-icon>
          <span class="font-weight-medium">Факторы риска</span>
          <v-chip size="x-small" variant="outlined">
            {{ riskFactors.length }}
          </v-chip>
        </div>
      </v-expansion-panel-title>

      <v-expansion-panel-text>
        <v-list density="compact">
          <v-list-item
            v-for="(risk, idx) in riskFactors"
            :key="idx"
            class="px-0"
          >
            <template #prepend>
              <v-icon size="small" color="error">mdi-alert-octagon</v-icon>
            </template>
            <v-list-item-subtitle class="text-wrap">{{ risk }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="riskFactors.length === 0" class="px-0">
            <v-list-item-subtitle class="text-medium-emphasis">Рисков не выявлено</v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script setup lang="ts">
// Types
interface WorkingConditions {
  work_schedule: string
  remote_work_options: string
  business_travel: string
}

// Props
interface Props {
  workingConditions: WorkingConditions
  specialRequirements: string[]
  riskFactors: string[]
}

defineProps<Props>()
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}

.text-wrap {
  white-space: normal;
  word-wrap: break-word;
}
</style>

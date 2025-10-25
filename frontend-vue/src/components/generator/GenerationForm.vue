<template>
  <div>
    <div class="text-subtitle-2 mb-3">Step 2: Configure Generation</div>

    <!-- Temperature Control -->
    <div class="mb-4">
      <div class="d-flex justify-space-between align-center mb-2">
        <label class="text-body-2">
          Temperature
          <v-tooltip location="top">
            <template #activator="{ props }">
              <v-icon v-bind="props" size="small" class="ml-1">
                mdi-information-outline
              </v-icon>
            </template>
            <div style="max-width: 300px">
              Controls creativity of generated content:
              <ul class="mt-2">
                <li><strong>0.3-0.5:</strong> Conservative, factual</li>
                <li><strong>0.6-0.8:</strong> Balanced (recommended)</li>
                <li><strong>0.9-1.0:</strong> Creative, varied</li>
              </ul>
            </div>
          </v-tooltip>
        </label>
        <span class="text-body-2 font-weight-bold">{{ temperatureValue }}</span>
      </div>

      <v-slider
        v-model="temperatureValue"
        :min="0.3"
        :max="1.0"
        :step="0.1"
        color="primary"
        track-color="grey-lighten-2"
        thumb-label
        :thumb-size="20"
        show-ticks="always"
        tick-size="2"
      >
        <template #thumb-label="{ modelValue }">
          {{ modelValue.toFixed(1) }}
        </template>
      </v-slider>

      <div class="d-flex justify-space-between text-caption text-medium-emphasis">
        <span>Conservative</span>
        <span>Balanced</span>
        <span>Creative</span>
      </div>
    </div>

    <v-divider class="my-4" />

    <!-- Employee Name (Optional) -->
    <div class="mb-4">
      <div class="text-body-2 mb-2">
        Employee Name (Optional)
        <v-tooltip location="top">
          <template #activator="{ props }">
            <v-icon v-bind="props" size="small" class="ml-1">
              mdi-information-outline
            </v-icon>
          </template>
          <div style="max-width: 300px">
            If provided, the profile will be personalized for this employee.
            Leave empty for a generic position profile.
          </div>
        </v-tooltip>
      </div>

      <v-text-field
        v-model="employeeNameValue"
        placeholder="e.g., John Smith"
        variant="outlined"
        density="comfortable"
        clearable
        prepend-inner-icon="mdi-account-outline"
      />
    </div>

    <!-- Quick Presets -->
    <div>
      <div class="text-body-2 mb-2">Quick Presets</div>
      <v-chip-group>
        <v-chip
          :variant="temperatureValue === 0.4 ? 'flat' : 'outlined'"
          :color="temperatureValue === 0.4 ? 'primary' : 'default'"
          @click="applyPreset(0.4)"
        >
          <v-icon start size="small">mdi-shield-check</v-icon>
          Conservative
        </v-chip>

        <v-chip
          :variant="temperatureValue === 0.7 ? 'flat' : 'outlined'"
          :color="temperatureValue === 0.7 ? 'primary' : 'default'"
          @click="applyPreset(0.7)"
        >
          <v-icon start size="small">mdi-checkbox-marked-circle</v-icon>
          Recommended
        </v-chip>

        <v-chip
          :variant="temperatureValue === 0.9 ? 'flat' : 'outlined'"
          :color="temperatureValue === 0.9 ? 'primary' : 'default'"
          @click="applyPreset(0.9)"
        >
          <v-icon start size="small">mdi-lightbulb-on</v-icon>
          Creative
        </v-chip>
      </v-chip-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Props
interface Props {
  temperature?: number
  employeeName?: string
}

const props = withDefaults(defineProps<Props>(), {
  temperature: 0.7,
  employeeName: ''
})

// Emits
const emit = defineEmits<{
  'update:temperature': [value: number]
  'update:employeeName': [value: string]
}>()

// Computed two-way bindings
const temperatureValue = computed({
  get: () => props.temperature,
  set: (value: number) => emit('update:temperature', value)
})

const employeeNameValue = computed({
  get: () => props.employeeName,
  set: (value: string) => emit('update:employeeName', value)
})

// Methods
function applyPreset(temperature: number): void {
  temperatureValue.value = temperature
}
</script>

<style scoped>
:deep(.v-slider-thumb__label) {
  font-size: 0.75rem;
  font-weight: 600;
}

:deep(.v-slider__tick) {
  opacity: 0.3;
}
</style>

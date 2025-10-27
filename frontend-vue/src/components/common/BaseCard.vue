<template>
  <v-card
    :elevation="elevation"
    :rounded="rounded"
    :class="cardClass"
    v-bind="$attrs"
  >
    <slot />
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

/**
 * BaseCard - Reusable card component with consistent styling
 *
 * This component provides a consistent card styling pattern across the application.
 * It wraps Vuetify's v-card with default elevation and rounded properties.
 *
 * @example
 * <BaseCard class="mb-4">
 *   <v-card-text>Content here</v-card-text>
 * </BaseCard>
 *
 * @example With custom elevation
 * <BaseCard :elevation="4">
 *   <v-card-title>Custom elevation</v-card-title>
 * </BaseCard>
 */

interface Props {
  /**
   * Card elevation (shadow depth)
   * @default 2
   */
  elevation?: string | number

  /**
   * Card border radius
   * @default "lg"
   */
  rounded?: string | boolean

  /**
   * Additional CSS classes
   */
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  elevation: 2,
  rounded: 'lg',
  class: ''
})

// Merge classes properly
const cardClass = computed(() => props.class || '')
</script>

<style scoped>
/* No additional styles needed - inherits from Vuetify */
</style>

<template>
  <v-dialog
    :model-value="modelValue"
    :theme="theme.global.name.value"
    v-bind="$attrs"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <slot />
  </v-dialog>
</template>

<script setup lang="ts">
import { useTheme } from 'vuetify'

/**
 * BaseThemedDialog - Wrapper component for Vuetify v-dialog with automatic theme support
 *
 * This component solves the Vuetify 3 dialog teleportation issue where dialogs render
 * outside the main app context, breaking theme inheritance. By explicitly binding the
 * current theme, all child content reactively updates when theme changes.
 *
 * Usage:
 * ```vue
 * <BaseThemedDialog v-model="showDialog" max-width="600px" persistent>
 *   <v-card>
 *     <!-- Dialog content -->
 *   </v-card>
 * </BaseThemedDialog>
 * ```
 *
 * @component
 * @example
 * ```vue
 * <template>
 *   <BaseThemedDialog v-model="dialogVisible" max-width="800px">
 *     <v-card>
 *       <v-card-title>My Dialog</v-card-title>
 *       <v-card-text>Content here</v-card-text>
 *     </v-card>
 *   </BaseThemedDialog>
 * </template>
 *
 * <script setup lang="ts">
 * import { ref } from 'vue'
 * import BaseThemedDialog from '@/components/common/BaseThemedDialog.vue'
 *
 * const dialogVisible = ref(false)
 * </script>
 * ```
 */

interface Props {
  modelValue: boolean
}

defineProps<Props>()

defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// Get current theme for reactive binding
// Used in template: :theme="theme.global.name.value"
const theme = useTheme()
</script>

<style scoped>
/* No styles needed - all styling handled by v-dialog and slotted content */
</style>

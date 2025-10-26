<template>
  <v-tooltip location="bottom">
    <template #activator="{ props: tooltipProps }">
      <v-btn
        v-bind="tooltipProps"
        :size="buttonConfig.SIZE"
        :variant="buttonConfig.VARIANT"
        :color="buttonConfig.COLOR"
        :class="breakpointClass"
        :aria-label="ariaLabel"
        @click.stop="$emit('click')"
      >
        <v-icon v-if="showIcon" start size="small">{{ iconName }}</v-icon>
        {{ buttonText }}
      </v-btn>
    </template>
    <span>{{ tooltipText }}</span>
  </v-tooltip>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  BUTTON_CONFIG,
  type SelectionMode,
  type Breakpoint,
  getButtonText,
  getTooltipText,
  getIconName,
  getBreakpointClass
} from '@/constants/treeSelection'

// Props
interface Props {
  /** Selection mode: 'direct' (only direct positions) or 'all' (recursive) */
  mode: SelectionMode

  /** Responsive breakpoint: 'desktop', 'tablet', or 'mobile' */
  breakpoint: Breakpoint

  /** Number of positions that will be selected */
  count: number
}

const props = defineProps<Props>()

// Emits
defineEmits<{
  click: []
}>()

// Computed
const buttonConfig = BUTTON_CONFIG

const breakpointClass = computed(() => getBreakpointClass(props.breakpoint))

const buttonText = computed(() => getButtonText(props.mode, props.breakpoint, props.count))

const tooltipText = computed(() => getTooltipText(props.mode))

const iconName = computed(() => getIconName(props.mode))

const showIcon = computed(() => props.breakpoint === 'desktop')

const ariaLabel = computed(() =>
  `${tooltipText.value} (${props.count} position${props.count !== 1 ? 's' : ''})`
)
</script>

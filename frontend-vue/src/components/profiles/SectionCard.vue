<template>
  <v-card
    :class="{
      'section-card': true,
      'section-card--editing': isEditing,
      'section-card--invalid': !isValid,
    }"
  >
    <!-- Section Header -->
    <v-sheet
      :bg-color="isEditing ? 'primary-lighten-5' : 'surface-variant'"
      class="pa-4"
    >
      <div class="d-flex align-center justify-space-between">
        <!-- Left: Icon + Title + Status -->
        <div class="d-flex align-center gap-3">
          <v-icon :icon="icon" :color="isEditing ? 'primary' : undefined" />
          <span class="text-h6">{{ title }}</span>

          <!-- Status Badge -->
          <v-chip
            v-if="!isEditing && isValid"
            size="small"
            color="success"
            variant="flat"
          >
            <v-icon size="small">mdi-check</v-icon>
          </v-chip>

          <v-chip
            v-else-if="!isEditing && !isValid"
            size="small"
            color="warning"
            variant="flat"
          >
            <v-icon size="small">mdi-alert</v-icon>
          </v-chip>

          <v-chip
            v-else-if="isEditing"
            size="small"
            color="primary"
            variant="flat"
          >
            <v-icon size="small">mdi-pencil</v-icon>
            Редактирование
          </v-chip>

          <!-- Has Changes Badge -->
          <v-badge
            v-if="hasChanges && !isEditing"
            dot
            color="warning"
            offset-x="-4"
            offset-y="4"
          >
            <v-chip size="small" variant="outlined">
              Не сохранено
            </v-chip>
          </v-badge>
        </div>

        <!-- Right: Action Buttons -->
        <div class="d-flex align-center gap-2">
          <!-- View Mode: Edit Button -->
          <v-btn
            v-if="!isEditing"
            icon="mdi-pencil"
            variant="text"
            size="small"
            @click="emit('edit')"
          >
            <v-icon>mdi-pencil</v-icon>
            <v-tooltip activator="parent" location="bottom">
              Редактировать секцию
            </v-tooltip>
          </v-btn>

          <!-- Edit Mode: Save & Cancel Buttons -->
          <template v-else>
            <v-btn
              icon="mdi-check"
              variant="text"
              size="small"
              color="success"
              @click="emit('save')"
            >
              <v-icon>mdi-check</v-icon>
              <v-tooltip activator="parent" location="bottom">
                Сохранить изменения
              </v-tooltip>
            </v-btn>

            <v-btn
              icon="mdi-close"
              variant="text"
              size="small"
              color="error"
              @click="emit('cancel')"
            >
              <v-icon>mdi-close</v-icon>
              <v-tooltip activator="parent" location="bottom">
                Отменить изменения
              </v-tooltip>
            </v-btn>
          </template>
        </div>
      </div>

      <!-- Validation Error (only in view mode) -->
      <v-alert
        v-if="!isEditing && !isValid && validationError"
        type="warning"
        variant="tonal"
        density="compact"
        class="mt-3"
      >
        <div class="text-caption">
          <v-icon size="small" class="mr-1">mdi-alert</v-icon>
          {{ validationError }}
        </div>
      </v-alert>
    </v-sheet>

    <v-divider />

    <!-- Section Content -->
    <v-card-text
      :class="{
        'pa-4': true,
        'section-content--readonly': !isEditing,
        'section-content--editing': isEditing,
      }"
    >
      <slot name="content" />
    </v-card-text>

    <!-- Edit Mode Footer (optional actions) -->
    <template v-if="isEditing">
      <v-divider />
      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn variant="text" @click="emit('cancel')"> Отмена </v-btn>
        <v-btn color="success" variant="elevated" @click="emit('save')">
          Сохранить секцию
        </v-btn>
      </v-card-actions>
    </template>
  </v-card>
</template>

<script setup lang="ts">
// Props
interface Props {
  sectionId: string
  title: string
  icon: string
  isEditing?: boolean
  isValid?: boolean
  validationError?: string
  hasChanges?: boolean
}

withDefaults(defineProps<Props>(), {
  isEditing: false,
  isValid: true,
  validationError: undefined,
  hasChanges: false,
})

// Emits
const emit = defineEmits<{
  edit: []
  save: []
  cancel: []
}>()
</script>

<style scoped>
.section-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
}

.section-card--editing {
  border-color: rgb(var(--v-theme-primary));
  box-shadow: 0 4px 12px rgba(var(--v-theme-primary), 0.2);
}

.section-card--invalid {
  border-color: rgb(var(--v-theme-warning));
}

.section-content--readonly:hover {
  background-color: rgba(var(--v-theme-surface-variant), 0.5);
  cursor: pointer;
}

.section-content--editing {
  background-color: rgba(var(--v-theme-primary-lighten-5), 0.1);
}

.gap-2 {
  gap: 8px;
}

.gap-3 {
  gap: 12px;
}

/* Smooth transitions for edit mode */
.v-card-actions {
  animation: slideUp 0.2s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

/**
 * Proficiency levels for professional skills
 * Used in ProfessionalSkillsEditor.vue
 */

export interface ProficiencyLevel {
  value: number
  label: string
}

export const PROFICIENCY_LEVELS: ProficiencyLevel[] = [
  { value: 1, label: 'Базовый' },
  { value: 2, label: 'Средний' },
  { value: 3, label: 'Продвинутый' },
  { value: 4, label: 'Экспертный' },
]

/**
 * Get color for proficiency level chip
 */
export function getProficiencyColor(level: number): string {
  switch (level) {
    case 1:
      return 'grey'
    case 2:
      return 'info'
    case 3:
      return 'success'
    case 4:
      return 'primary'
    default:
      return 'grey'
  }
}

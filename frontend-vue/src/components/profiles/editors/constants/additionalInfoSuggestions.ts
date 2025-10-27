/**
 * Suggestions for additional info editor
 * Used in AdditionalInfoEditor.vue
 */

export const REQUIREMENTS_SUGGESTIONS = [
  'Прохождение проверки безопасности',
  'Медосмотр',
  'Знание корпоративных политик',
  'Двухфакторная аутентификация',
]

export const RISK_SUGGESTIONS = [
  'Высокая нагрузка в периоды дедлайнов',
  'Работа с legacy-системами',
  'Зависимость от внешних подрядчиков',
  'Частые изменения приоритетов',
]

/**
 * Validation rules for work schedule
 */
export const scheduleRules = [
  (v: string) => !!v || 'Укажите график работы',
  (v: string) => (v && v.length >= 5) || 'Минимум 5 символов',
  (v: string) => (v && v.length <= 200) || 'Максимум 200 символов',
]

/**
 * Validation rules for remote work options
 */
export const remoteWorkRules = [
  (v: string) => !!v || 'Укажите возможности удалённой работы',
  (v: string) => (v && v.length >= 10) || 'Минимум 10 символов',
  (v: string) => (v && v.length <= 500) || 'Максимум 500 символов',
]

/**
 * Validation rules for business travel
 */
export const businessTravelRules = [
  (v: string) => !!v || 'Укажите информацию о командировках',
  (v: string) => (v && v.length >= 10) || 'Минимум 10 символов',
  (v: string) => (v && v.length <= 500) || 'Максимум 500 символов',
]

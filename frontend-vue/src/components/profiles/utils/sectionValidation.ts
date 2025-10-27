/**
 * Section validation utilities for ProfileContentEditor
 */

/**
 * Validates section data
 * @returns Object containing validation status and optional error message
 */
export function validateSection(
  sectionId: string,
  data: unknown
): { isValid: boolean; error?: string } {
  // Basic validation
  let isValid = true
  let error: string | undefined

  if (!data) {
    isValid = false
    error = 'Секция не может быть пустой'
    return { isValid, error }
  }

  // Section-specific validation
  switch (sectionId) {
    case 'basic_info':
      if (
        typeof data !== 'object' ||
        !(data as Record<string, unknown>).direct_manager ||
        !(data as Record<string, unknown>).primary_activity_type
      ) {
        isValid = false
        error = 'Укажите руководителя и вид деятельности'
      }
      break

    case 'responsibility_areas':
      if (!Array.isArray(data) || data.length === 0) {
        isValid = false
        error = 'Добавьте хотя бы одну зону ответственности'
      }
      break

    case 'professional_skills':
      if (!Array.isArray(data) || data.length === 0) {
        isValid = false
        error = 'Добавьте хотя бы один навык'
      }
      break

    case 'corporate_competencies':
    case 'personal_qualities':
      if (!Array.isArray(data) || data.length === 0) {
        isValid = false
        error = 'Добавьте хотя бы одно значение'
      }
      break

    case 'experience_and_education':
      if (
        typeof data !== 'object' ||
        !(data as Record<string, unknown>).education_level
      ) {
        isValid = false
        error = 'Укажите уровень образования'
      }
      break
  }

  return { isValid, error }
}

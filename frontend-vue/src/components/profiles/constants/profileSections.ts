/**
 * Profile section definitions for ProfileContentEditor
 */

export interface ProfileSection {
  id: string
  title: string
  icon: string
  component: string
}

export const PROFILE_SECTIONS: ProfileSection[] = [
  {
    id: 'basic_info',
    title: 'Основная информация',
    icon: 'mdi-information',
    component: 'BasicInfoEditor',
  },
  {
    id: 'responsibility_areas',
    title: 'Зоны ответственности',
    icon: 'mdi-clipboard-list',
    component: 'ResponsibilityAreasEditor',
  },
  {
    id: 'professional_skills',
    title: 'Профессиональные навыки',
    icon: 'mdi-toolbox',
    component: 'ProfessionalSkillsEditor',
  },
  {
    id: 'corporate_competencies',
    title: 'Корпоративные компетенции',
    icon: 'mdi-brain',
    component: 'CompetenciesEditor',
  },
  {
    id: 'personal_qualities',
    title: 'Личные качества',
    icon: 'mdi-account-heart',
    component: 'CompetenciesEditor', // Reuse same editor
  },
  {
    id: 'experience_and_education',
    title: 'Опыт и образование',
    icon: 'mdi-school',
    component: 'ExperienceEducationEditor',
  },
  {
    id: 'careerogram',
    title: 'Карьерограмма',
    icon: 'mdi-chart-timeline-variant',
    component: 'CareerogramEditor',
  },
  {
    id: 'workplace_provisioning',
    title: 'Обеспечение рабочего места',
    icon: 'mdi-laptop',
    component: 'WorkplaceProvisioningEditor',
  },
  {
    id: 'performance_metrics',
    title: 'Показатели эффективности',
    icon: 'mdi-chart-line',
    component: 'PerformanceMetricsEditor',
  },
  {
    id: 'additional_information',
    title: 'Дополнительная информация',
    icon: 'mdi-information-outline',
    component: 'AdditionalInfoEditor',
  },
]

/**
 * Maps section IDs to profile_data field names
 */
export const SECTION_FIELD_MAP: Record<string, string> = {
  responsibility_areas: 'responsibility_areas',
  professional_skills: 'professional_skills',
  corporate_competencies: 'corporate_competencies',
  personal_qualities: 'personal_qualities',
  experience_and_education: 'experience_and_education',
  careerogram: 'careerogram',
  workplace_provisioning: 'workplace_provisioning',
  performance_metrics: 'performance_metrics',
  additional_information: 'additional_information',
}

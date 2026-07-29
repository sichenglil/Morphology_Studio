import { api } from './client'
import type { ValidationResult } from '@/types/scene'
export const runValidation = () => api.post<ValidationResult>('/api/validation')

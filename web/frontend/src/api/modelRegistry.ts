import { api } from './client'

export interface PackagedRobotModel {
  id: string
  name: string
  urdf: string
  preview_gif: string
  preview_png: string
  enabled: boolean
  primary: boolean
  available: boolean
  preview_available: boolean
  preview_url: string
  preview_png_url: string
}

export const getModelRegistry = () => api.get<{models: PackagedRobotModel[]}>('/api/model-registry')
export const loadPackagedModel = (id: string) =>
  api.post(`/api/model-registry/${encodeURIComponent(id)}/load`)

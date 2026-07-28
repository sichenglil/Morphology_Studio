import { api } from './client'
import type { SceneManifest } from '@/types/scene'
export const getScene = () => api.get<SceneManifest>('/api/scene')
export const setJointValue = (name: string, value: number) => api.patch(`/api/joints/${encodeURIComponent(name)}`, {value})

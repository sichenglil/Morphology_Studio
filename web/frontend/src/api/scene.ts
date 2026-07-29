import { api } from './client'
import type { SceneManifest } from '@/types/scene'
export const getScene = () => api.get<SceneManifest>('/api/scene')
export const commitJointValues = (values:Record<string,number>, expectedRevision:number, modelId?:string|null) => api.post<{values:Record<string,number>;revision:number}>('/api/workspaces/current/joint-states/commit',{values,expectedRevision,modelId})

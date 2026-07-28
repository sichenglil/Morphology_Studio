import { api } from './client'
import type { SceneManifest } from '@/types/scene'
export interface LoadOptions { path: string; entry?: string; arguments?: Record<string,string>; package_map_path?: string }
export const loadModel = (options: LoadOptions) => api.post<SceneManifest>('/api/models/load', options)
export const pickPath = (kind: 'file'|'directory') => api.get<{path:string}>(`/api/pick?kind=${kind}`)
export const analyzePath = (path: string) => api.get<{format:string; entries: Array<Record<string,unknown>>}>(`/api/models/analyze?path=${encodeURIComponent(path)}`)

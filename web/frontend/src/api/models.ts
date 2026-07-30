import { api } from './client'
import type { SceneManifest } from '@/types/scene'
export interface LoadOptions { path: string; entry?: string; arguments?: Record<string,string>; package_map_path?: string }
export interface AnalyzeResult { format:string; entries:Array<Record<string,unknown>>; stepEmbedded?:boolean }
export interface StepPartPayload { name:string; parent:number|null; joint_type:string; axis:number[]; stl:string }
export interface StepImportPayload { source_path:string; name:string; parts:StepPartPayload[] }
export const loadModel = (options: LoadOptions) => api.post<SceneManifest>('/api/models/load', options)
export const importStepModel = (payload:StepImportPayload) => api.post<SceneManifest>('/api/models/import-step', payload)
export const pickPath = (kind: 'file'|'directory'|'save', options: {extension?:string; filename?:string} = {}) => {
  const query = new URLSearchParams({kind})
  if (options.extension) query.set('extension', options.extension)
  if (options.filename) query.set('filename', options.filename)
  return api.get<{path:string}>(`/api/pick?${query.toString()}`)
}
export const analyzePath = (path: string) => api.get<AnalyzeResult>(`/api/models/analyze?path=${encodeURIComponent(path)}`)

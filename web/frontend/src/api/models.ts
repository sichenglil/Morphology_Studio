import { api } from './client'
import type { SceneManifest } from '@/types/scene'
export interface LoadOptions { path: string; entry?: string; arguments?: Record<string,string>; package_map_path?: string }
export interface StepAdapterStatus { available:boolean; root:string|null; pnpm:string|null; installed:boolean; url:string; reason:string }
export interface AnalyzeResult { format:string; entries:Array<Record<string,unknown>>; stepAdapter?:StepAdapterStatus|null }
export const loadModel = (options: LoadOptions) => api.post<SceneManifest>('/api/models/load', options)
export const pickPath = (kind: 'file'|'directory'|'save') => api.get<{path:string}>(`/api/pick?kind=${kind}`)
export const analyzePath = (path: string) => api.get<AnalyzeResult>(`/api/models/analyze?path=${encodeURIComponent(path)}`)
export const getStepAdapterStatus = () => api.get<StepAdapterStatus>('/api/step-adapter/status')
export const launchStepAdapter = (path?:string) => api.post<StepAdapterStatus>('/api/step-adapter/launch', path?{path}:{})

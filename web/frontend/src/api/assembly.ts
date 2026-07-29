import { api } from './client'
import type { SceneManifest } from '@/types/scene'
export interface AssemblyRequest { child_path:string; parent_link:string; child_link:string; name:string; assembly_name?:string; transform:number[] }
export const assembleModel=(request:AssemblyRequest)=>api.post<SceneManifest>('/api/assembly',request)

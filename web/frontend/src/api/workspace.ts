import {api} from './client'
import type {SceneManifest} from '@/types/scene'
export const clearWorkspace=()=>api.post<SceneManifest>('/api/workspaces/current/new',{})
export const openWorkspace=(path:string)=>api.post<SceneManifest>('/api/workspaces/open',{path})
export const saveWorkspace=(path:string,settings:Record<string,unknown>)=>api.post<{ok:boolean;path:string}>('/api/workspaces/current/save',{path,settings})

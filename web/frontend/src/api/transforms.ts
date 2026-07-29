import type { SceneManifest, Transform } from '@/types/scene'
export type TransformTarget='model_instance'|'link'|'joint'|'assembly_connection'|'visual'|'collision'
export interface EditableTransform extends Transform {scale?:number[]}
async function json<T>(url:string,init?:RequestInit):Promise<T>{const response=await fetch(url,init);if(!response.ok)throw new Error((await response.json()).detail||response.statusText);return response.json()}
export function commitTransform(targetType:TransformTarget,entityId:string,transform:EditableTransform,expectedRevision:number){return json<{scene:SceneManifest;transform:EditableTransform}>('/api/workspaces/current/transforms/commit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({targetType,entityId,transform,expectedRevision})})}
export function undoTransform(){return json<SceneManifest>('/api/workspaces/current/history/undo',{method:'POST'})}
export function redoTransform(){return json<SceneManifest>('/api/workspaces/current/history/redo',{method:'POST'})}

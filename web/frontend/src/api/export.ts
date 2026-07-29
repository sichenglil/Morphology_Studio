import {api} from './client'
export type ExportFormat='urdf'|'mjcf'|'morphology'|'package'|'package_zip'
export const exportModel=(format:ExportFormat,output:string)=>api.post<{ok:boolean;output:string}>('/api/export',{format,output})

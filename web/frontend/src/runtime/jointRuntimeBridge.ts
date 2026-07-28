type Preview=(id:string,value:number)=>number
let preview:Preview|undefined
export function registerJointPreview(handler:Preview){preview=handler;return()=>{if(preview===handler)preview=undefined}}
export function previewRuntimeJoint(id:string,value:number){return preview?.(id,value)??value}

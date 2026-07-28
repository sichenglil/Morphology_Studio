import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { getScene, setJointValue } from '@/api/scene'
import { loadModel, type LoadOptions } from '@/api/models'
import { runValidation } from '@/api/validation'
import { assembleModel, type AssemblyRequest } from '@/api/assembly'
import type { SceneManifest, ValidationResult } from '@/types/scene'
import {commitTransform,undoTransform,redoTransform,type EditableTransform,type TransformTarget} from '@/api/transforms'

const zero=()=>({xyz:[0,0,0],rpy:[0,0,0]})
const emptyScene = (): SceneManifest => ({robotId:null, rootLinks:[], links:[], joints:[], resources:[],revision:0,rootTransform:zero(),assemblyJoints:[],history:{canUndo:false,canRedo:false}})
export const useEditorStore = defineStore('editor', () => {
  const scene = ref<SceneManifest>(emptyScene())
  const selectedType = ref<TransformTarget|null>(null)
  const selectedId = ref<string|null>(null)
  const validation = ref<ValidationResult|null>(null)
  const busy = ref(false)
  const logs = ref<string[]>(['Morphology Studio ready'])
  const mode = ref<'auto'|'assisted'|'manual'>('assisted')
  const selected = computed(() => selectedType.value === 'link' ? scene.value.links.find(x=>x.id===selectedId.value) : scene.value.joints.find(x=>x.id===selectedId.value))
  const transformMode=ref<'translate'|'rotate'|'scale'>('translate'); const transformSpace=ref<'local'|'world'>('local'); const selectionLevel=ref<'link'|'geometry'>('link'); const snapEnabled=ref(false)
  const editSemantic=ref<'assembly'|'kinematic'>('assembly')
  function select(type:TransformTarget, id:string) { selectedType.value=type; selectedId.value=id }
  function clearSelection(){selectedType.value=null;selectedId.value=null}
  async function commit(type:TransformTarget,id:string,transform:EditableTransform){const result=await commitTransform(type,id,transform,scene.value.revision);scene.value=result.scene;logs.value.push(`Transform committed: ${id}`)}
  async function undo(){scene.value=await undoTransform();logs.value.push('Undo transform')}
  async function redo(){scene.value=await redoTransform();logs.value.push('Redo transform')}
  async function open(options:LoadOptions) { busy.value=true; try { scene.value=await loadModel(options); logs.value.push(`Loaded ${scene.value.robotId}`); selectedId.value=null; validation.value=null } finally { busy.value=false } }
  async function refresh() { scene.value=await getScene() }
  async function moveJoint(name:string, value:number) { await setJointValue(name,value); const joint=scene.value.joints.find(x=>x.name===name); if(joint) joint.value=value }
  async function validate() { validation.value=await runValidation(); logs.value.push(`Validation: ${validation.value.errors} errors, ${validation.value.warnings} warnings`) }
  async function assemble(request:AssemblyRequest){busy.value=true;try{scene.value=await assembleModel(request);logs.value.push(`Assembly connection created: ${request.name}`)}finally{busy.value=false}}
  return {scene,selectedType,selectedId,selected,validation,busy,logs,mode,transformMode,transformSpace,selectionLevel,snapEnabled,editSemantic,select,clearSelection,commit,undo,redo,open,refresh,moveJoint,validate,assemble}
})

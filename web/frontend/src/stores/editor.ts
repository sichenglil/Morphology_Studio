import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { getScene, setJointValue } from '@/api/scene'
import { loadModel, type LoadOptions } from '@/api/models'
import { runValidation } from '@/api/validation'
import { assembleModel, type AssemblyRequest } from '@/api/assembly'
import type { SceneManifest, ValidationResult } from '@/types/scene'

const emptyScene = (): SceneManifest => ({robotId:null, rootLinks:[], links:[], joints:[], resources:[]})
export const useEditorStore = defineStore('editor', () => {
  const scene = ref<SceneManifest>(emptyScene())
  const selectedType = ref<'link'|'joint'|null>(null)
  const selectedId = ref<string|null>(null)
  const validation = ref<ValidationResult|null>(null)
  const busy = ref(false)
  const logs = ref<string[]>(['Morphology Studio ready'])
  const mode = ref<'auto'|'assisted'|'manual'>('assisted')
  const selected = computed(() => selectedType.value === 'link' ? scene.value.links.find(x=>x.id===selectedId.value) : scene.value.joints.find(x=>x.id===selectedId.value))
  function select(type:'link'|'joint', id:string) { selectedType.value=type; selectedId.value=id }
  async function open(options:LoadOptions) { busy.value=true; try { scene.value=await loadModel(options); logs.value.push(`Loaded ${scene.value.robotId}`); selectedId.value=null; validation.value=null } finally { busy.value=false } }
  async function refresh() { scene.value=await getScene() }
  async function moveJoint(name:string, value:number) { await setJointValue(name,value); const joint=scene.value.joints.find(x=>x.name===name); if(joint) joint.value=value }
  async function validate() { validation.value=await runValidation(); logs.value.push(`Validation: ${validation.value.errors} errors, ${validation.value.warnings} warnings`) }
  async function assemble(request:AssemblyRequest){busy.value=true;try{scene.value=await assembleModel(request);logs.value.push(`Assembly connection created: ${request.name}`)}finally{busy.value=false}}
  return {scene,selectedType,selectedId,selected,validation,busy,logs,mode,select,open,refresh,moveJoint,validate,assemble}
})

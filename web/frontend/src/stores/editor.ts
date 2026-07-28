import { defineStore } from 'pinia'
import { computed, ref, shallowReactive } from 'vue'
import { getScene, commitJointValues } from '@/api/scene'
import { loadModel, type LoadOptions } from '@/api/models'
import { runValidation } from '@/api/validation'
import { assembleModel, type AssemblyRequest } from '@/api/assembly'
import type { SceneManifest, ValidationResult } from '@/types/scene'
import {commitTransform,undoTransform,redoTransform,type EditableTransform,type TransformTarget} from '@/api/transforms'
import {previewRuntimeJoint} from '@/runtime/jointRuntimeBridge'
import {performanceMetrics} from '@/runtime/PerformanceMetrics'

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
  const jointValues=shallowReactive<Record<string,number>>({});const sceneGeneration=ref(0);let pendingJointCommits:Record<string,number>={};let commitTimer:ReturnType<typeof setTimeout>|undefined
  const selected = computed(() => selectedType.value === 'link' ? scene.value.links.find(x=>x.id===selectedId.value) : scene.value.joints.find(x=>x.id===selectedId.value))
  const transformMode=ref<'translate'|'rotate'|'scale'>('translate'); const transformSpace=ref<'local'|'world'>('local'); const selectionLevel=ref<'link'|'geometry'>('link'); const snapEnabled=ref(false)
  const editSemantic=ref<'assembly'|'kinematic'>('assembly')
  const renderQuality=ref<'performance'|'balanced'|'quality'>('balanced')
  function select(type:TransformTarget, id:string) { selectedType.value=type; selectedId.value=id }
  function clearSelection(){selectedType.value=null;selectedId.value=null}
  async function commit(type:TransformTarget,id:string,transform:EditableTransform){const result=await commitTransform(type,id,transform,scene.value.revision);scene.value=result.scene;sceneGeneration.value++;logs.value.push(`Transform committed: ${id}`)}
  async function undo(){scene.value=await undoTransform();sceneGeneration.value++;logs.value.push('Undo transform')}
  async function redo(){scene.value=await redoTransform();sceneGeneration.value++;logs.value.push('Redo transform')}
  function initializeJoints(){for(const key of Object.keys(jointValues))delete jointValues[key];for(const joint of scene.value.joints)jointValues[joint.id]=joint.value||0}
  async function open(options:LoadOptions) { busy.value=true; try { scene.value=await loadModel(options);initializeJoints();sceneGeneration.value++;logs.value.push(`Loaded ${scene.value.robotId}`); selectedId.value=null; validation.value=null } finally { busy.value=false } }
  async function refresh() { scene.value=await getScene();initializeJoints();sceneGeneration.value++ }
  function previewJoint(name:string,value:number){const next=previewRuntimeJoint(name,value);jointValues[name]=next;return next}
  function queueJointCommit(name:string,value:number){pendingJointCommits[name]=value;if(commitTimer)clearTimeout(commitTimer);commitTimer=setTimeout(()=>void flushJointCommits(),80)}
  async function flushJointCommits(){if(commitTimer)clearTimeout(commitTimer);commitTimer=undefined;const values=pendingJointCommits;pendingJointCommits={};if(!Object.keys(values).length)return;performanceMetrics.increment('backendCommits');const before=Object.fromEntries(Object.keys(values).map(k=>[k,scene.value.joints.find(j=>j.id===k)?.value??0]));try{const result=await commitJointValues(values,scene.value.revision,scene.value.robotId);scene.value.revision=result.revision;for(const [id,value] of Object.entries(result.values)){const joint=scene.value.joints.find(j=>j.id===id);if(joint)joint.value=value}logs.value.push(`Joint commit: ${Object.keys(values).length} joint(s)`)}catch(error){for(const [id,value] of Object.entries(before)){jointValues[id]=value;previewRuntimeJoint(id,value)}throw error}finally{performanceMetrics.pending(0)}}
  async function validate() { validation.value=await runValidation(); logs.value.push(`Validation: ${validation.value.errors} errors, ${validation.value.warnings} warnings`) }
  async function assemble(request:AssemblyRequest){busy.value=true;try{scene.value=await assembleModel(request);initializeJoints();sceneGeneration.value++;logs.value.push(`Assembly connection created: ${request.name}`)}finally{busy.value=false}}
  return {scene,sceneGeneration,jointValues,selectedType,selectedId,selected,validation,busy,logs,mode,transformMode,transformSpace,selectionLevel,snapEnabled,editSemantic,renderQuality,select,clearSelection,commit,undo,redo,open,refresh,previewJoint,queueJointCommit,flushJointCommits,validate,assemble}
})

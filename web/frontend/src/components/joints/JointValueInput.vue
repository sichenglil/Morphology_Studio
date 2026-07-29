<template>
  <input
    ref="input"
    class="joint-value-input"
    :class="{ invalid: invalid || outOfRange }"
    :value="draft"
    :disabled="disabled"
    :aria-label="`${joint.name} value`"
    :aria-invalid="invalid || outOfRange"
    :title="rangeTitle"
    inputmode="decimal"
    autocomplete="off"
    @focus="beginEdit"
    @input="onInput"
    @blur="onBlur"
    @keydown="onKeydown"
    @wheel="onWheel"
  />
</template>

<script setup lang="ts">
import {computed, ref, watch} from 'vue'
import {ElMessage} from 'element-plus'
import type {JointNode} from '@/types/scene'

export type RotationUnit = 'rad'|'deg'
export type TranslationUnit = 'm'|'cm'|'mm'

const props=defineProps<{joint:JointNode;value:number;unit:RotationUnit|TranslationUnit;precision:number;disabled?:boolean}>()
const emit=defineEmits<{preview:[value:number];commit:[value:number]}>()
const input=ref<HTMLInputElement>()
const focused=ref(false),dirty=ref(false),invalid=ref(false),cancelled=ref(false),editStart=ref(props.value)
const factor=computed(()=>props.unit==='deg'?180/Math.PI:props.unit==='cm'?100:props.unit==='mm'?1000:1)
const display=(value:number)=>Number.isFinite(value)?(value*factor.value).toFixed(props.precision):''
const draft=ref(display(props.value))
const parsed=computed(()=>{const text=draft.value.trim();if(!text||['-','.','-.','+','+.'].includes(text))return null;const value=Number(text);return Number.isFinite(value)?value/factor.value:null})
const lower=computed(()=>typeof props.joint.limit.lower==='number'?props.joint.limit.lower:undefined)
const upper=computed(()=>typeof props.joint.limit.upper==='number'?props.joint.limit.upper:undefined)
const outOfRange=computed(()=>parsed.value!==null&&((lower.value!==undefined&&parsed.value<lower.value)||(upper.value!==undefined&&parsed.value>upper.value)))
const rangeTitle=computed(()=>lower.value===undefined&&upper.value===undefined?'无限位':`范围：${lower.value===undefined?'−∞':display(lower.value)} ～ ${upper.value===undefined?'∞':display(upper.value)} ${props.unit}`)

watch(()=>[props.value,props.unit,props.precision] as const,()=>{if(!focused.value||!dirty.value)draft.value=display(props.value)})
function beginEdit(){focused.value=true;dirty.value=false;invalid.value=false;editStart.value=props.value}
function onInput(event:Event){draft.value=(event.target as HTMLInputElement).value;dirty.value=true;invalid.value=false;if(parsed.value!==null)emit('preview',parsed.value)}
function finish(){
  if(!dirty.value){focused.value=false;draft.value=display(props.value);return}
  if(parsed.value===null){invalid.value=true;draft.value=display(props.value);emit('preview',props.value);focused.value=false;ElMessage.error('请输入有效的有限数值');return}
  let next=parsed.value
  const original=next
  if(lower.value!==undefined)next=Math.max(next,lower.value)
  if(upper.value!==undefined)next=Math.min(next,upper.value)
  if(next!==original)ElMessage.warning(`输入超出 ${props.joint.name} 范围，已限制为 ${display(next)} ${props.unit}`)
  draft.value=display(next);invalid.value=false;dirty.value=false;focused.value=false;emit('preview',next);emit('commit',next)
}
function cancel(){cancelled.value=true;dirty.value=false;invalid.value=false;draft.value=display(editStart.value);emit('preview',editStart.value);focused.value=false;input.value?.blur()}
function onBlur(){if(cancelled.value){cancelled.value=false;return}finish()}
function step(modifier=1){const base=props.unit==='rad'?.01:props.unit==='deg'?1:props.unit==='m'?.001:props.unit==='cm'?.1:1;const shown=(parsed.value??props.value)*factor.value+base*modifier;draft.value=String(shown);dirty.value=true;invalid.value=false;const next=shown/factor.value;emit('preview',next);emit('commit',Math.min(upper.value??Infinity,Math.max(lower.value??-Infinity,next)))}
function onKeydown(event:KeyboardEvent){event.stopPropagation();if(event.key==='Enter'){event.preventDefault();finish();input.value?.blur()}else if(event.key==='Escape'){event.preventDefault();cancel()}else if(event.key==='ArrowUp'||event.key==='ArrowDown'){event.preventDefault();step((event.key==='ArrowUp'?1:-1)*(event.shiftKey?10:event.altKey?.1:1))}else if(event.key==='Home'&&lower.value!==undefined){event.preventDefault();draft.value=display(lower.value);dirty.value=true;emit('preview',lower.value);emit('commit',lower.value)}else if(event.key==='End'&&upper.value!==undefined){event.preventDefault();draft.value=display(upper.value);dirty.value=true;emit('preview',upper.value);emit('commit',upper.value)}}
function onWheel(event:WheelEvent){if(document.activeElement!==input.value)return;event.preventDefault();event.stopPropagation();step(event.deltaY<0?1:-1)}
</script>

<style scoped>
.joint-value-input{width:110px;height:28px;border:1px solid #36516a;border-radius:4px;background:#0c1721;color:#d9edf9;padding:0 8px;text-align:right;font:12px ui-monospace,SFMono-Regular,Consolas,monospace;font-variant-numeric:tabular-nums;outline:none}
.joint-value-input:hover{border-color:#4c7898}.joint-value-input:focus{border-color:#39aef0;box-shadow:0 0 0 2px #209de333}.joint-value-input.invalid{border-color:#e96363;box-shadow:0 0 0 2px #e9636329}.joint-value-input:disabled{opacity:.55;cursor:not-allowed}
</style>

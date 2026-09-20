<template>
  <aside ref="panel" class="structure-panel" data-testid="structure-tree-panel" aria-label="当前导入文件结构树" :class="{ collapsed }" :style="panelStyle">
    <header data-testid="structure-tree-titlebar" @pointerdown="startPanelMove">
      <span class="drag-mark">⠿</span><b>结构树</b>
      <span class="source-name" :title="sourceLabel">{{ sourceLabel }}</span>
      <button class="collapse-button" :aria-label="collapsed ? '展开结构树' : '收起结构树'" @pointerdown.stop @click="collapsed = !collapsed">{{ collapsed ? '▸' : '▾' }}</button>
      <button class="close-button" aria-label="关闭结构树" @pointerdown.stop @click="$emit('close')">×</button>
    </header>
    <div v-show="!collapsed" ref="body" class="structure-body" data-testid="structure-tree-canvas" @pointerdown="startCanvasPan" @wheel.prevent="zoomAt">
      <div class="canvas-controls">
        <button aria-label="缩小结构树" @pointerdown.stop @click="zoomBy(0.85)">−</button>
        <button aria-label="重置结构树视图" @pointerdown.stop @click="resetCanvas">{{ Math.round(scale * 100) }}%</button>
        <button aria-label="放大结构树" @pointerdown.stop @click="zoomBy(1.15)">＋</button>
      </div>
      <div class="structure-canvas" :style="canvasStyle">
      <div v-if="!store.scene.robotId" class="structure-empty">导入模型后显示结构</div>
      <div v-else-if="!forest.length" class="structure-empty">当前文件没有可显示的 Link</div>
      <ul v-else class="structure-forest"><StructureTreeBranch v-for="root in forest" :key="root.id" :node="root" /></ul>
      </div>
    </div>
    <div v-show="!collapsed" class="resize-handle" data-testid="structure-tree-resizer" aria-label="调整结构树窗口大小" @pointerdown="startPanelResize" />
  </aside>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import { useEditorStore } from '@/stores/editor'
import StructureTreeBranch, { type StructureNode } from './StructureTreeBranch.vue'

defineEmits<{ close: [] }>()
const store = useEditorStore()
const collapsed = ref(false)
const panel = ref<HTMLElement>(), body = ref<HTMLElement>()
const left = ref(16), top = ref(54), width = ref(420), height = ref(360)
const panX = ref(16), panY = ref(16), scale = ref(1)
let stopPointerAction: (() => void) | undefined
const panelStyle = computed(() => ({ left: `${left.value}px`, top: `${top.value}px`, width: `${width.value}px`, height: collapsed.value ? '45px' : `${height.value}px` }))
const canvasStyle = computed(() => ({ transform: `translate(${panX.value}px, ${panY.value}px) scale(${scale.value})` }))
const sourceLabel = computed(() => store.scene.sourceName || store.scene.displayName || store.scene.robotId || '当前模型')
const forest = computed<StructureNode[]>(() => {
  const links = new Map(store.scene.links.map(link => [link.id, link]))
  const jointsByParent = new Map<string, typeof store.scene.joints>()
  for (const joint of store.scene.joints) jointsByParent.set(joint.parent, [...(jointsByParent.get(joint.parent) || []), joint])
  const visited = new Set<string>()
  const build = (id: string): StructureNode | undefined => {
    const link = links.get(id)
    if (!link || visited.has(id)) return
    visited.add(id)
    const children: StructureNode['children'] = []
    for (const joint of jointsByParent.get(id) || []) {
      const child = build(joint.child)
      if (child) children.push({ joint: { id: joint.id, name: joint.name, type: joint.type }, link: child })
    }
    return { id: link.id, name: link.name, children }
  }
  const roots: StructureNode[] = []
  for (const id of store.scene.rootLinks) { const root = build(id); if (root) roots.push(root) }
  for (const link of store.scene.links) { const root = build(link.id); if (root) roots.push(root) }
  return roots
})

function clamp(value: number, minimum: number, maximum: number) { return Math.min(Math.max(value, minimum), Math.max(minimum, maximum)) }
function beginPointerAction(move: (event: PointerEvent) => void) {
  stopPointerAction?.()
  const stop = () => { window.removeEventListener('pointermove', move); window.removeEventListener('pointerup', stop); window.removeEventListener('pointercancel', stop); stopPointerAction = undefined }
  window.addEventListener('pointermove', move); window.addEventListener('pointerup', stop); window.addEventListener('pointercancel', stop); stopPointerAction = stop
}
function panelBounds() {
  const host = panel.value?.offsetParent as HTMLElement | null
  return { width: host?.clientWidth || window.innerWidth, height: host?.clientHeight || window.innerHeight }
}
function startPanelMove(event: PointerEvent) {
  if (event.button !== 0 || (event.target as HTMLElement).closest('button')) return
  event.preventDefault()
  const startX = event.clientX, startY = event.clientY, initialLeft = left.value, initialTop = top.value
  beginPointerAction(next => { const bounds = panelBounds(); left.value = clamp(initialLeft + next.clientX - startX, 0, bounds.width - width.value); top.value = clamp(initialTop + next.clientY - startY, 0, bounds.height - (collapsed.value ? 45 : height.value)) })
}
function startPanelResize(event: PointerEvent) {
  if (event.button !== 0) return
  event.preventDefault(); event.stopPropagation()
  const startX = event.clientX, startY = event.clientY, initialWidth = width.value, initialHeight = height.value
  beginPointerAction(next => { const bounds = panelBounds(); width.value = clamp(initialWidth + next.clientX - startX, 280, bounds.width - left.value); height.value = clamp(initialHeight + next.clientY - startY, 180, bounds.height - top.value) })
}
function startCanvasPan(event: PointerEvent) {
  if (event.button !== 0 || (event.target as HTMLElement).closest('button')) return
  event.preventDefault()
  const startX = event.clientX, startY = event.clientY, initialX = panX.value, initialY = panY.value
  beginPointerAction(next => { panX.value = initialX + next.clientX - startX; panY.value = initialY + next.clientY - startY })
}
function setScale(nextScale: number, clientX?: number, clientY?: number) {
  const next = clamp(nextScale, 0.4, 2.5), old = scale.value
  const rect = body.value?.getBoundingClientRect()
  const anchorX = clientX ?? (rect ? rect.left + rect.width / 2 : 0), anchorY = clientY ?? (rect ? rect.top + rect.height / 2 : 0)
  const localX = (anchorX - (rect?.left || 0) - panX.value) / old, localY = (anchorY - (rect?.top || 0) - panY.value) / old
  panX.value = anchorX - (rect?.left || 0) - localX * next; panY.value = anchorY - (rect?.top || 0) - localY * next; scale.value = next
}
function zoomAt(event: WheelEvent) { setScale(scale.value * (event.deltaY < 0 ? 1.1 : 0.9), event.clientX, event.clientY) }
function zoomBy(factor: number) { setScale(scale.value * factor) }
function resetCanvas() { panX.value = 16; panY.value = 16; scale.value = 1 }
onBeforeUnmount(() => stopPointerAction?.())
</script>

<style scoped>
.structure-panel{position:absolute;z-index:4;display:flex;flex-direction:column;min-width:280px;min-height:180px;border:1px solid #dbe2e8;border-radius:12px;background:#fdfdfdee;color:#27343e;box-shadow:0 10px 28px #07131f35;backdrop-filter:blur(8px);overflow:hidden}.structure-panel.collapsed{min-height:45px}.structure-panel header{height:45px;display:flex;align-items:center;gap:8px;padding:0 12px;border-bottom:1px solid #e7ebee;flex:0 0 auto;cursor:move;user-select:none}.drag-mark{color:#a9b2b9}.structure-panel header b{font-size:13px;white-space:nowrap}.source-name{min-width:0;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#96a0a8;font-size:10px}.structure-panel header button{border:0;background:transparent;color:#8d979e;cursor:pointer}.collapse-button{font-size:12px}.close-button{font-size:25px;line-height:1}.structure-body{position:relative;flex:1;min-height:0;overflow:hidden;cursor:grab;touch-action:none}.structure-body:active{cursor:grabbing}.structure-canvas{position:absolute;top:0;left:0;width:max-content;min-width:calc(100% - 32px);transform-origin:0 0;will-change:transform}.canvas-controls{position:absolute;z-index:3;top:8px;right:8px;display:flex;border:1px solid #dce4e9;border-radius:6px;background:#fff;box-shadow:0 2px 8px #18304418}.canvas-controls button{min-width:28px;height:25px;padding:0 6px;border:0;border-right:1px solid #e5ebef;background:transparent;color:#5d6c77;cursor:pointer;font-size:11px}.canvas-controls button:last-child{border-right:0}.structure-forest{display:flex;justify-content:center;gap:18px;width:max-content;min-width:100%;margin:0;padding:0}.structure-empty{display:grid;place-content:center;min-height:90px;color:#95a0a8;font-size:12px}.resize-handle{position:absolute;right:0;bottom:0;width:18px;height:18px;cursor:nwse-resize}.resize-handle::after{content:"";position:absolute;right:4px;bottom:4px;width:8px;height:8px;border-right:2px solid #8fa0ab;border-bottom:2px solid #8fa0ab}
</style>

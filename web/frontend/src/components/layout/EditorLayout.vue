<template>
  <main ref="studioElement" class="studio" data-testid="editor-layout" :style="{ '--bottom-dock-height': `${bottomHeight}px` }">
    <AppToolbar @import="run('file.importModel')" @validate="run('tools.validate')" @assemble="run('tools.assemble')" @export="run('file.export')" @command="run" />
    <section ref="workbenchElement" class="workbench" :style="{ gridTemplateColumns: `${leftWidth}px 6px minmax(360px, 1fr) 6px ${rightWidth}px` }">
      <LeftSidebar />
      <div class="pane-resizer pane-resizer--vertical" data-testid="left-resizer" role="separator" aria-label="调整左侧面板宽度" aria-orientation="vertical" :aria-valuenow="leftWidth" :aria-valuemin="LEFT_MIN" :aria-valuemax="LEFT_MAX" tabindex="0" @pointerdown="startResize('left', $event)" @keydown="resizeWithKeyboard('left', $event)" @dblclick="resetSize('left')" />
      <RobotViewport />
      <div class="pane-resizer pane-resizer--vertical" data-testid="right-resizer" role="separator" aria-label="调整右侧面板宽度" aria-orientation="vertical" :aria-valuenow="rightWidth" :aria-valuemin="RIGHT_MIN" :aria-valuemax="RIGHT_MAX" tabindex="0" @pointerdown="startResize('right', $event)" @keydown="resizeWithKeyboard('right', $event)" @dblclick="resetSize('right')" />
      <RightInspector />
    </section>
    <div class="pane-resizer pane-resizer--horizontal" data-testid="bottom-resizer" role="separator" aria-label="调整下部面板高度" aria-orientation="horizontal" :aria-valuenow="bottomHeight" :aria-valuemin="BOTTOM_MIN" :aria-valuemax="BOTTOM_MAX" tabindex="0" @pointerdown="startResize('bottom', $event)" @keydown="resizeWithKeyboard('bottom', $event)" @dblclick="resetSize('bottom')" />
    <BottomDock />
    <StatusBar />
    <ImportWizard v-model="importOpen" />
    <AssemblyWizard v-model="assemblyOpen" />
    <ExportDialog v-model="exportOpen" />
  </main>
</template>

<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useEditorStore } from '@/stores/editor'
import AppToolbar from './AppToolbar.vue'
import LeftSidebar from './LeftSidebar.vue'
import RightInspector from './RightInspector.vue'
import BottomDock from './BottomDock.vue'
import StatusBar from './StatusBar.vue'
import RobotViewport from '@/components/viewport/RobotViewport.vue'
import ImportWizard from '@/components/dialogs/ImportWizard.vue'
import AssemblyWizard from '@/components/dialogs/AssemblyWizard.vue'
import ExportDialog from '@/components/dialogs/ExportDialog.vue'
import type { CommandId } from '@/config/menuCommands'
import { pickPath } from '@/api/models'
import { clearWorkspace, openWorkspace, saveWorkspace } from '@/api/workspace'

type ResizeTarget = 'left' | 'right' | 'bottom'
const LEFT_DEFAULT = 270, RIGHT_DEFAULT = 310, BOTTOM_DEFAULT = 218
const LEFT_MIN = 190, LEFT_MAX = 480, RIGHT_MIN = 220, RIGHT_MAX = 520
const BOTTOM_MIN = 120, BOTTOM_MAX = 480, VIEWPORT_MIN = 360, WORKBENCH_MIN = 240, SPLITTERS_WIDTH = 12
const store = useEditorStore(), importOpen = ref(false), assemblyOpen = ref(false), exportOpen = ref(false)
const studioElement = ref<HTMLElement>(), workbenchElement = ref<HTMLElement>()
const leftWidth = ref(LEFT_DEFAULT), rightWidth = ref(RIGHT_DEFAULT), bottomHeight = ref(BOTTOM_DEFAULT)
let stopActiveResize: (() => void) | undefined

function clamp(value: number, minimum: number, maximum: number) { return Math.min(Math.max(value, minimum), Math.max(minimum, maximum)) }
function availableSideWidth(target: 'left' | 'right') {
  const total = workbenchElement.value?.clientWidth ?? window.innerWidth
  return total - (target === 'left' ? rightWidth.value : leftWidth.value) - VIEWPORT_MIN - SPLITTERS_WIDTH
}
function setSideWidth(target: 'left' | 'right', value: number) {
  if (target === 'left') leftWidth.value = clamp(value, LEFT_MIN, Math.min(LEFT_MAX, availableSideWidth(target)))
  else rightWidth.value = clamp(value, RIGHT_MIN, Math.min(RIGHT_MAX, availableSideWidth(target)))
}
function setBottomHeight(value: number) {
  const total = studioElement.value?.clientHeight ?? window.innerHeight
  bottomHeight.value = clamp(value, BOTTOM_MIN, Math.min(BOTTOM_MAX, total - 58 - 26 - 6 - WORKBENCH_MIN))
}
function startResize(target: ResizeTarget, event: PointerEvent) {
  if (event.button !== 0) return
  stopActiveResize?.(); event.preventDefault()
  const startX = event.clientX, startY = event.clientY
  const initial = target === 'left' ? leftWidth.value : target === 'right' ? rightWidth.value : bottomHeight.value
  document.body.classList.add(target === 'bottom' ? 'layout-resizing-row' : 'layout-resizing-column')
  const move = (next: PointerEvent) => {
    if (target === 'left') setSideWidth('left', initial + next.clientX - startX)
    else if (target === 'right') setSideWidth('right', initial + startX - next.clientX)
    else setBottomHeight(initial + startY - next.clientY)
  }
  const stop = () => {
    window.removeEventListener('pointermove', move); window.removeEventListener('pointerup', stop); window.removeEventListener('pointercancel', stop)
    document.body.classList.remove('layout-resizing-row', 'layout-resizing-column'); stopActiveResize = undefined
  }
  window.addEventListener('pointermove', move); window.addEventListener('pointerup', stop); window.addEventListener('pointercancel', stop); stopActiveResize = stop
}
function resizeWithKeyboard(target: ResizeTarget, event: KeyboardEvent) {
  const step = event.shiftKey ? 40 : 10
  if (target === 'left' && ['ArrowLeft', 'ArrowRight'].includes(event.key)) { event.preventDefault(); setSideWidth('left', leftWidth.value + (event.key === 'ArrowRight' ? step : -step)) }
  else if (target === 'right' && ['ArrowLeft', 'ArrowRight'].includes(event.key)) { event.preventDefault(); setSideWidth('right', rightWidth.value + (event.key === 'ArrowLeft' ? step : -step)) }
  else if (target === 'bottom' && ['ArrowUp', 'ArrowDown'].includes(event.key)) { event.preventDefault(); setBottomHeight(bottomHeight.value + (event.key === 'ArrowUp' ? step : -step)) }
}
function resetSize(target: ResizeTarget) {
  if (target === 'left') setSideWidth('left', LEFT_DEFAULT)
  else if (target === 'right') setSideWidth('right', RIGHT_DEFAULT)
  else setBottomHeight(BOTTOM_DEFAULT)
}
onBeforeUnmount(() => stopActiveResize?.())
function dispatch(id: CommandId) { window.dispatchEvent(new CustomEvent('morphology-command', { detail: id })) }
async function run(id: CommandId) {
  try {
    if (id === 'file.importModel') { importOpen.value = true; return }
    if (id === 'file.export' || id === 'tools.exportUrdf') { exportOpen.value = true; return }
    if (id === 'tools.assemble') { assemblyOpen.value = true; return }
    if (id === 'tools.validate') { await store.validate(); ElMessage.success('模型验证完成'); return }
    if (id === 'edit.undo') { await store.undo(); return }
    if (id === 'edit.redo') { await store.redo(); return }
    if (id === 'file.newWorkspace') { if (store.scene.robotId) await ElMessageBox.confirm('将清空当前工作区，是否继续？', '新建工作区'); store.scene = await clearWorkspace(); store.clearSelection(); return }
    if (id === 'file.openWorkspace') { const path = (await pickPath('file')).path; if (path) { store.scene = await openWorkspace(path); store.sceneGeneration++ } return }
    if (id === 'file.saveWorkspace') { const path = (await pickPath('save')).path; if (path) { await saveWorkspace(path, { translation_unit: 'mm', rotation_unit: 'deg', coordinate_space: 'parent' }); ElMessage.success('工作区已保存') } return }
    dispatch(id)
  } catch (error) { ElMessage.error(String(error)) }
}
</script>

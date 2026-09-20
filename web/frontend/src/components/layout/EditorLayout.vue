<template>
  <main ref="studioElement" class="studio" data-testid="editor-layout" :style="{ '--bottom-dock-height': `${bottomHeight}px` }" @dragenter.prevent="enterDropOverlay" @dragover.prevent="dropActive = true" @dragleave.prevent="hideDropOverlay" @drop.prevent="handleBrowserDrop">
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
    <div v-if="dropActive" class="file-drop-overlay" data-testid="file-drop-overlay"><div><b>释放以导入模型</b><span>支持 URDF、Xacro、MJCF、STEP 及模型目录</span></div></div>
    <ImportWizard v-model="importOpen" :initial-path="pendingImportPath" />
    <AssemblyWizard v-model="assemblyOpen" />
    <ExportDialog v-model="exportOpen" />
  </main>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
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
import { analyzePath, pickPath } from '@/api/models'
import { clearWorkspace, openWorkspace, saveWorkspace } from '@/api/workspace'

type ResizeTarget = 'left' | 'right' | 'bottom'
const LEFT_DEFAULT = 270, RIGHT_DEFAULT = 310, BOTTOM_DEFAULT = 218
const LEFT_MIN = 190, LEFT_MAX = 480, RIGHT_MIN = 220, RIGHT_MAX = 520
const BOTTOM_MIN = 120, BOTTOM_MAX = 480, VIEWPORT_MIN = 360, WORKBENCH_MIN = 240, SPLITTERS_WIDTH = 12
const store = useEditorStore(), importOpen = ref(false), assemblyOpen = ref(false), exportOpen = ref(false)
const dropActive = ref(false), pendingImportPath = ref('')
let dragDepth = 0
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
function enterDropOverlay() { dragDepth++; dropActive.value = true }
function hideDropOverlay() { dragDepth = Math.max(0, dragDepth - 1); if (!dragDepth) dropActive.value = false }
function browserDropPaths(event: DragEvent) {
  const files = [...(event.dataTransfer?.files || [])]
  const paths = files.map(file => (file as File & { path?: string }).path).filter((value): value is string => Boolean(value))
  const uri = event.dataTransfer?.getData('text/uri-list')?.split(/\r?\n/).find(value => value.startsWith('file://'))
  if (!paths.length && uri) paths.push(decodeURIComponent(uri.replace(/^file:\/\/\/?/, '')))
  return paths
}
async function importDroppedPath(path: string) {
  try {
    const result = await analyzePath(path)
    if (result.format === 'step') {
      pendingImportPath.value = path
      importOpen.value = true
      return
    }
    await store.open({ path })
    ElMessage.success('拖入的模型已载入三维工作区')
  } catch (error) { ElMessage.error(`无法导入拖入的文件：${error instanceof Error ? error.message : String(error)}`) }
}
function receiveDroppedFiles(event: Event) {
  const paths = (event as CustomEvent<{ paths?: string[] }>).detail?.paths || []
  if (!paths.length) return
  if (paths.length > 1) ElMessage.warning('一次仅导入一个模型，已选择第一个文件')
  void importDroppedPath(paths[0])
}
function handleBrowserDrop(event: DragEvent) {
  dragDepth = 0; dropActive.value = false
  const paths = browserDropPaths(event)
  if (paths.length) receiveDroppedFiles(new CustomEvent('morphology-files-dropped', { detail: { paths } }))
}
onMounted(() => window.addEventListener('morphology-files-dropped', receiveDroppedFiles))
onBeforeUnmount(() => { stopActiveResize?.(); window.removeEventListener('morphology-files-dropped', receiveDroppedFiles) })
function dispatch(id: CommandId) { window.dispatchEvent(new CustomEvent('morphology-command', { detail: id })) }
async function run(id: CommandId) {
  try {
    if (id === 'file.importModel') { pendingImportPath.value = ''; importOpen.value = true; return }
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

<style scoped>
.file-drop-overlay{position:fixed;z-index:10000;inset:12px;display:grid;place-items:center;border:2px dashed #55b8f3;border-radius:16px;background:#0a1725d9;pointer-events:none;color:#edf8ff}.file-drop-overlay>div{display:grid;gap:8px;padding:28px 42px;border-radius:12px;background:#14283a;text-align:center;box-shadow:0 16px 48px #0008}.file-drop-overlay b{font-size:20px}.file-drop-overlay span{color:#a9c8dc;font-size:12px}
</style>

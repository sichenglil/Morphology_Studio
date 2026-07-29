<template>
  <section class="model-preview" data-testid="model-preview">
    <div class="preview-heading"><b>UR5e + HX5 Right</b><small>软件操作演示</small></div>
    <div class="preview-frame" :aria-busy="loading">
      <span v-if="loading" class="preview-message">正在加载模型预览…</span>
      <img :key="imageKey" :src="source" alt="UR5e 与 HX5 Right 组合机械臂旋转预览" @load="loading=false" @error="fallback">
    </div>
    <el-button size="small" :loading="loadingModel" :disabled="!model" @click="openModel">加载到三维视图</el-button>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getModelRegistry, loadPackagedModel, type PackagedRobotModel } from '@/api/modelRegistry'
import { useEditorStore } from '@/stores/editor'

const store = useEditorStore()
const model = ref<PackagedRobotModel>()
const source = ref('/app-assets/previews/ur5e_hx5_right/robot.gif')
const loading = ref(true)
const loadingModel = ref(false)
const fallbackLevel = ref(0)
const imageKey = ref(0)

function fallback() {
  fallbackLevel.value++
  source.value = fallbackLevel.value === 1
    ? (model.value?.preview_png_url || '/app-assets/previews/ur5e_hx5_right/robot.png')
    : '/app-assets/placeholders/model-preview.png'
  imageKey.value++
  if (fallbackLevel.value > 1) loading.value = false
}

async function openModel() {
  if (!model.value) return
  loadingModel.value = true
  try {
    await loadPackagedModel(model.value.id)
    await store.refresh()
    store.clearSelection()
    ElMessage.success('组合机械臂已加载')
  } catch (error) {
    ElMessage.error(`模型加载失败：${String(error)}`)
  } finally {
    loadingModel.value = false
  }
}

onMounted(async () => {
  try {
    const response = await getModelRegistry()
    model.value = response.models.find(item => item.primary && item.available)
    if (model.value) source.value = model.value.preview_url
  } catch (error) {
    ElMessage.warning(`模型预览配置不可用：${String(error)}`)
  }
})
</script>

<style scoped>
.model-preview{flex:0 0 auto;padding:10px;border-bottom:1px solid #253542;display:grid;gap:8px}.preview-heading{display:flex;justify-content:space-between;align-items:center}.preview-heading b{font-size:12px;color:#d1e0eb}.preview-heading small{font-size:10px;color:#71889a}.preview-frame{position:relative;width:100%;aspect-ratio:16/9;max-height:150px;border:1px solid #2b4051;border-radius:6px;overflow:hidden;background:#101923;display:grid;place-items:center}.preview-frame img{width:100%;height:100%;object-fit:contain;display:block}.preview-message{position:absolute;z-index:1;color:#526774;font-size:11px;background:#f4f6f8cc;padding:4px 8px;border-radius:4px}
</style>

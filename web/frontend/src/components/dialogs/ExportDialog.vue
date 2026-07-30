<template>
  <el-dialog :model-value="modelValue" title="导出模型" width="620" @close="close">
    <div class="export-options">
      <button
        v-for="item in formats"
        :key="item.value"
        :class="{ selected: format === item.value }"
        @click="format = item.value"
      >
        <b>{{ item.label }}</b><span>{{ item.description }}</span>
      </button>
      <button disabled><b>Isaac USD</b><span>NOT_AVAILABLE_LOCAL</span></button>
    </div>

    <label class="output-label">
      输出文件或目录
      <div class="output-picker">
        <el-input v-model="output" :placeholder="selectedFormat.placeholder" />
        <el-button :loading="picking" @click="browseOutput">浏览</el-button>
      </div>
    </label>
    <el-alert title="导出写入用户选择的位置，不修改源模型" type="info" :closable="false" />

    <template #footer>
      <el-button @click="close">关闭</el-button>
      <el-button type="primary" :disabled="!output" @click="runExport">导出</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { exportModel, type ExportFormat } from '@/api/export'
import { pickPath } from '@/api/models'

defineProps<{ modelValue: boolean }>()
const emit = defineEmits(['update:modelValue'])
const output = ref('')
const format = ref<ExportFormat>('urdf')
const picking = ref(false)

const formats: Array<{
  value: ExportFormat
  label: string
  description: string
  extension: string
  filename: string
  placeholder: string
}> = [
  { value: 'urdf', label: 'URDF', description: '标准机器人描述', extension: '.urdf', filename: 'robot.urdf', placeholder: '选择 robot.urdf 的保存位置' },
  { value: 'package', label: 'Portable Package', description: '模型与资源目录', extension: '', filename: '', placeholder: '选择导出目录' },
  { value: 'package_zip', label: 'Portable ZIP', description: '模型、资源与校验报告压缩包', extension: '.zip', filename: 'robot_package.zip', placeholder: '选择 ZIP 的保存位置' },
  { value: 'mjcf', label: 'MJCF', description: 'MuJoCo XML', extension: '.xml', filename: 'robot.xml', placeholder: '选择 robot.xml 的保存位置' },
  { value: 'morphology', label: 'Morphology JSON', description: '形态结构数据', extension: '.json', filename: 'morphology.json', placeholder: '选择 JSON 的保存位置' },
]

const selectedFormat = computed(() => formats.find((item) => item.value === format.value) ?? formats[0])

function close() {
  emit('update:modelValue', false)
}

async function browseOutput() {
  picking.value = true
  try {
    const selected = selectedFormat.value
    const result = selected.value === 'package'
      ? await pickPath('directory')
      : await pickPath('save', { extension: selected.extension, filename: selected.filename })
    if (result.path) output.value = result.path
  } catch (error) {
    ElMessage.error(`无法打开路径选择器：${String(error)}`)
  } finally {
    picking.value = false
  }
}

async function runExport() {
  try {
    const result = await exportModel(format.value, output.value)
    ElMessage.success(`模型导出成功：${result.output}`)
    close()
  } catch (error) {
    ElMessage.error(String(error))
  }
}
</script>

<style scoped>
.output-label { display: grid; gap: 8px; }
.output-picker { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 8px; }
</style>

<template>
  <el-dialog :model-value="modelValue" title="导入机器人模型" width="920" @close="close">
    <el-steps :active="step" finish-status="success">
      <el-step title="选择来源" />
      <el-step title="解析与配置" />
      <el-step title="载入" />
    </el-steps>

    <div class="wizard-body">
      <label>模型文件或目录</label>
      <div class="path-row">
        <el-input v-model="path" placeholder="URDF、Xacro、MJCF 或模型目录" />
        <el-button :disabled="!path" @click="inspect">检测</el-button>
        <el-button @click="pick('file')">浏览文件</el-button>
        <el-button @click="pick('directory')">目录</el-button>
      </div>

      <template v-if="format === 'step'">
        <el-alert
          type="success"
          :closable="false"
          title="内置 OpenCascade：STEP 将在当前 EXE 内离线解析"
        >
          无需安装或启动外部 step2urdf。解析后请确认实体名称、父链接、关节类型和轴。
        </el-alert>
        <div class="step-actions">
          <el-button type="primary" :loading="parsing" @click="parseSelectedStep">
            {{ solids.length ? '重新解析 STEP' : '解析 STEP' }}
          </el-button>
          <span v-if="progress">{{ progress }}</span>
        </div>

        <el-table v-if="solids.length" :data="solids" max-height="360" row-key="index">
          <el-table-column label="实体" width="70" prop="index" />
          <el-table-column label="Link 名称" min-width="170">
            <template #default="scope"><el-input v-model="scope.row.name" /></template>
          </el-table-column>
          <el-table-column label="父实体" width="130">
            <template #default="scope">
              <el-select v-model="scope.row.parent" :disabled="scope.row.index === 0">
                <el-option label="根链接" :value="null" />
                <el-option
                  v-for="candidate in solids.slice(0, scope.row.index)"
                  :key="candidate.index"
                  :label="candidate.name"
                  :value="candidate.index"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="关节" width="130">
            <template #default="scope">
              <el-select v-model="scope.row.jointType" :disabled="scope.row.parent === null">
                <el-option label="固定" value="fixed" />
                <el-option label="旋转" value="revolute" />
                <el-option label="连续旋转" value="continuous" />
                <el-option label="移动" value="prismatic" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="关节轴 X/Y/Z" min-width="230">
            <template #default="scope">
              <div class="axis-row">
                <el-input-number v-for="(_, axis) in scope.row.axis" :key="axis" v-model="scope.row.axis[axis]" :step="0.1" controls-position="right" />
              </div>
            </template>
          </el-table-column>
        </el-table>
      </template>

      <template v-else>
        <label>入口文件（目录导入时可选）<el-input v-model="entry" /></label>
        <label>Package map（可选）<el-input v-model="packageMap" placeholder="YAML 路径" /></label>
        <label>Xacro 参数<el-input v-model="argumentsText" type="textarea" :rows="3" placeholder="name=value，每行一个" /></label>
      </template>

      <el-alert title="辅助模式：自动推断的关节语义必须由用户确认" type="info" :closable="false" />
    </div>

    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button
        type="primary"
        :loading="store.busy"
        :disabled="!path || (format === 'step' && !solids.length)"
        @click="load"
      >导入并显示</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { analyzePath, pickPath } from '@/api/models'
import { useEditorStore } from '@/stores/editor'
import { binaryStl, parseStepPath, toBase64, type StepSolid } from '@/step/directStepImport'

interface ConfiguredSolid extends StepSolid {
  index: number
  parent: number | null
  jointType: 'fixed' | 'revolute' | 'continuous' | 'prismatic'
  axis: number[]
}

defineProps<{ modelValue: boolean }>()
const emit = defineEmits(['update:modelValue'])
const store = useEditorStore()
const path = ref('')
const entry = ref('')
const packageMap = ref('')
const argumentsText = ref('')
const step = ref(0)
const format = ref('')
const parsing = ref(false)
const progress = ref('')
const solids = ref<ConfiguredSolid[]>([])

function close() { emit('update:modelValue', false) }

async function inspect() {
  if (!path.value) return
  const result = await analyzePath(path.value)
  format.value = result.format
  solids.value = []
  step.value = 1
}

async function pick(kind: 'file' | 'directory') {
  path.value = (await pickPath(kind)).path
  await inspect()
}

async function parseSelectedStep() {
  parsing.value = true
  progress.value = '正在加载 OpenCascade WebAssembly 并解析几何…'
  try {
    const parsed = await parseStepPath(path.value)
    solids.value = parsed.map((solid, index) => ({
      ...solid,
      index,
      parent: index === 0 ? null : 0,
      jointType: 'fixed',
      axis: [0, 0, 1],
    }))
    progress.value = `解析完成：${parsed.length} 个实体`
    ElMessage.success(progress.value)
  } catch (error) {
    progress.value = ''
    ElMessage.error(error instanceof Error ? error.message : String(error))
  } finally {
    parsing.value = false
  }
}

async function load() {
  try {
    if (format.value === 'step') {
      progress.value = '正在生成 STL 并建立机器人模型…'
      await store.openStep({
        source_path: path.value,
        name: path.value.split(/[\\/]/).pop()?.replace(/\.(step|stp)$/i, '') || 'step_robot',
        parts: solids.value.map((solid) => ({
          name: solid.name,
          parent: solid.parent,
          joint_type: solid.jointType,
          axis: solid.axis,
          stl: toBase64(binaryStl(solid)),
        })),
      })
    } else {
      const args = Object.fromEntries(argumentsText.value.split('\n').filter(Boolean).map((value) => value.split('=', 2) as [string, string]))
      await store.open({ path: path.value, entry: entry.value || undefined, arguments: args, package_map_path: packageMap.value || undefined })
    }
    step.value = 3
    close()
    ElMessage.success('模型已载入三维工作区')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : String(error))
  }
}
</script>

<style scoped>
.wizard-body { display: grid; gap: 14px; margin-top: 22px; }
.path-row, .step-actions, .axis-row { display: flex; gap: 8px; align-items: center; }
.axis-row :deep(.el-input-number) { width: 70px; }
</style>

<template>
  <header class="toolbar" data-testid="toolbar">
    <div class="brand"><span class="brand-mark">M</span><span>Morphology Studio</span></div>
    <AppMenuBar @command="$emit('command',$event)" />
    <div class="tool-actions">
      <el-button type="primary" @click="$emit('import')">导入模型</el-button>
      <el-button @click="$emit('assemble')">装配</el-button>
      <el-button :disabled="!store.scene.robotId" @click="$emit('validate')">验证</el-button>
      <el-button :disabled="!store.scene.robotId" @click="$emit('export')">导出</el-button>
      <el-button data-testid="undo" :disabled="!store.scene.history.canUndo" @click="store.undo">撤销</el-button>
      <el-button data-testid="redo" :disabled="!store.scene.history.canRedo" @click="store.redo">重做</el-button>
      <el-select v-model="store.renderQuality" size="small" style="width:105px" aria-label="渲染质量"><el-option label="性能" value="performance"/><el-option label="均衡" value="balanced"/><el-option label="质量" value="quality"/></el-select>
      <el-segmented v-model="store.mode" :options="modeOptions" size="small" />
    </div>
  </header>
</template>
<script setup lang="ts">import { useEditorStore } from '@/stores/editor';import AppMenuBar from './AppMenuBar.vue'; defineEmits(['import','assemble','validate','export','command']); const store=useEditorStore(); const modeOptions=[{label:'自动',value:'auto'},{label:'辅助',value:'assisted'},{label:'手动',value:'manual'}]</script>

<template>
 <aside class="inspector" data-testid="right-inspector"><div class="panel-tabs"><b>属性</b><span>语义</span></div>
  <div v-if="!store.selected" class="empty-panel inspector-empty">在模型树或三维视口中选择对象</div>
  <div v-else class="properties"><div class="selection-heading"><span :class="store.selectedType==='link'?'link-icon':'joint-icon'">{{store.selectedType==='link'?'◆':'◎'}}</span><div><b>{{store.selected.name}}</b><small>{{store.selectedType?.toUpperCase()}}</small></div></div>
   <el-collapse model-value="general"><el-collapse-item title="常规" name="general"><label>名称<el-input :model-value="store.selected.name" disabled /></label><label v-if="store.selectedType==='joint'">类型<el-input :model-value="(store.selected as JointNode).type" disabled /></label></el-collapse-item>
   <el-collapse-item title="变换" name="transform"><TransformInspector /></el-collapse-item>
   <el-collapse-item v-if="store.selectedType==='joint'" title="关节" name="joint"><JointInspector /></el-collapse-item>
   <el-collapse-item v-if="store.selectedType==='link'" title="几何与惯性" name="geometry"><p class="metric">Visuals <b>{{(store.selected as LinkNode).visuals.length}}</b></p><p class="metric">Collisions <b>{{(store.selected as LinkNode).collisions}}</b></p></el-collapse-item></el-collapse>
  </div>
 </aside>
</template>
<script setup lang="ts">import {useEditorStore} from '@/stores/editor'; import TransformInspector from '@/components/inspector/TransformInspector.vue'; import JointInspector from '@/components/inspector/JointInspector.vue'; import type {JointNode,LinkNode} from '@/types/scene'; const store=useEditorStore()</script>

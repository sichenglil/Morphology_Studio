<template>
  <section class="model-tree" data-testid="model-tree">
    <div class="tree-search"><el-input v-model="query" placeholder="搜索 Link / Joint" clearable /></div>
    <div v-if="!store.scene.robotId" class="empty-panel">尚未加载模型<br><small>点击顶部“导入模型”开始</small></div>
    <template v-else>
      <div class="robot-node"><span class="caret">▾</span><b>{{store.scene.displayName || store.scene.robotId}}</b></div>
      <div class="tree-section"><div class="section-title">LINKS <em>{{filteredLinks.length}}</em></div>
        <button v-for="link in filteredLinks" :key="link.id" class="tree-node" :class="{active:store.selectedId===link.id}" @click="store.select('link',link.id)"><span class="link-icon">◆</span><span>{{link.name}}</span></button>
      </div>
      <div class="tree-section"><div class="section-title">JOINTS <em>{{filteredJoints.length}}</em></div>
        <button v-for="joint in filteredJoints" :key="joint.id" class="tree-node" :class="{active:store.selectedId===joint.id}" @click="store.select('joint',joint.id)"><span class="joint-icon">◎</span><span>{{joint.name}}</span><small>{{joint.type}}</small></button>
      </div>
    </template>
  </section>
</template>
<script setup lang="ts">import {computed,ref} from 'vue'; import {useEditorStore} from '@/stores/editor'; const store=useEditorStore(); const query=ref(''); const match=(v:string)=>v.toLowerCase().includes(query.value.toLowerCase()); const filteredLinks=computed(()=>store.scene.links.filter(x=>match(x.name))); const filteredJoints=computed(()=>store.scene.joints.filter(x=>match(x.name)))</script>

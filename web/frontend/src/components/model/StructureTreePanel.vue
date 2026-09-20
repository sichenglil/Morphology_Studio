<template>
  <aside class="structure-panel" data-testid="structure-tree-panel" aria-label="当前导入文件结构树">
    <header>
      <span class="drag-mark">⠿</span><b>结构树</b>
      <span class="source-name" :title="sourceLabel">{{ sourceLabel }}</span>
      <button class="collapse-button" :aria-label="collapsed ? '展开结构树' : '收起结构树'" @click="collapsed = !collapsed">{{ collapsed ? '▸' : '▾' }}</button>
      <button class="close-button" aria-label="关闭结构树" @click="$emit('close')">×</button>
    </header>
    <div v-show="!collapsed" class="structure-body">
      <div v-if="!store.scene.robotId" class="structure-empty">导入模型后显示结构</div>
      <div v-else-if="!forest.length" class="structure-empty">当前文件没有可显示的 Link</div>
      <ul v-else class="structure-forest"><StructureTreeBranch v-for="root in forest" :key="root.id" :node="root" /></ul>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useEditorStore } from '@/stores/editor'
import StructureTreeBranch, { type StructureNode } from './StructureTreeBranch.vue'

defineEmits<{ close: [] }>()
const store = useEditorStore()
const collapsed = ref(false)
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
</script>

<style scoped>
.structure-panel{position:absolute;z-index:4;top:54px;left:16px;width:min(420px,calc(100% - 32px));max-height:calc(100% - 88px);display:flex;flex-direction:column;border:1px solid #dbe2e8;border-radius:12px;background:#fdfdfdee;color:#27343e;box-shadow:0 10px 28px #07131f35;backdrop-filter:blur(8px);overflow:hidden}.structure-panel header{height:45px;display:flex;align-items:center;gap:8px;padding:0 12px;border-bottom:1px solid #e7ebee;flex:0 0 auto}.drag-mark{color:#a9b2b9}.structure-panel header b{font-size:13px;white-space:nowrap}.source-name{min-width:0;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#96a0a8;font-size:10px}.structure-panel header button{border:0;background:transparent;color:#8d979e;cursor:pointer}.collapse-button{font-size:12px}.close-button{font-size:25px;line-height:1}.structure-body{min-height:110px;overflow:auto;padding:18px}.structure-forest{display:flex;justify-content:center;gap:18px;width:max-content;min-width:100%;margin:0;padding:0}.structure-empty{display:grid;place-content:center;min-height:90px;color:#95a0a8;font-size:12px}
</style>

<template>
  <li class="structure-branch">
    <button class="structure-link" :class="{ active: store.selectedType === 'link' && store.selectedId === node.id }" :title="node.name" @click="store.select('link', node.id)">{{ node.name }}</button>
    <ul v-if="node.children.length" class="structure-children">
      <li v-for="child in node.children" :key="child.joint.id" class="joint-branch">
        <button class="structure-joint" :class="{ active: store.selectedType === 'joint' && store.selectedId === child.joint.id }" :title="`${child.joint.name} · ${child.joint.type}`" @click="store.select('joint', child.joint.id)">{{ child.joint.name }} · {{ child.joint.type }}</button>
        <StructureTreeBranch :node="child.link" />
      </li>
    </ul>
  </li>
</template>

<script setup lang="ts">
import { useEditorStore } from '@/stores/editor'

export interface StructureNode {
  id: string
  name: string
  children: Array<{ joint: { id: string; name: string; type: string }; link: StructureNode }>
}

defineProps<{ node: StructureNode }>()
const store = useEditorStore()
</script>

<style scoped>
.structure-branch,.joint-branch{position:relative;display:flex;flex-direction:column;align-items:center;min-width:92px;list-style:none}.structure-link,.structure-joint{position:relative;z-index:1;max-width:150px;border:1px solid #d5dde4;background:#f8fafb;color:#40505d;border-radius:6px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;cursor:pointer}.structure-link{padding:4px 9px;font-size:11px;box-shadow:0 1px 3px #18304412}.structure-joint{margin-top:18px;padding:1px 5px;border:0;background:transparent;color:#8b98a2;font-size:9px}.structure-link:hover,.structure-link.active{border-color:#2f9dd4;background:#e9f7fe;color:#147cab}.structure-joint:hover,.structure-joint.active{color:#147cab;background:#e9f7fe}.structure-children{display:flex;justify-content:center;gap:10px;margin:0;padding:0}.joint-branch::before{content:"";position:absolute;top:0;left:50%;height:18px;border-left:1px solid #cbd5dc}.structure-children>.joint-branch:not(:only-child)::after{content:"";position:absolute;top:0;left:0;right:0;border-top:1px solid #cbd5dc}.structure-children>.joint-branch:first-child::after{left:50%}.structure-children>.joint-branch:last-child::after{right:50%}
</style>

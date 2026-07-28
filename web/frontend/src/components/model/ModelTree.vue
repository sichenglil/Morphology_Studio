<template>
  <section class="model-tree" data-testid="model-tree">
    <div class="tree-search"><el-input v-model="query" placeholder="搜索 Link / Joint" clearable /></div>
    <div v-if="!store.scene.robotId" class="empty-panel">尚未加载模型<br><small>点击顶部“导入模型”开始</small></div>
    <template v-else>
      <div class="robot-node"><span>▼</span><b>{{ store.scene.displayName || store.scene.robotId }}</b></div>
      <section class="tree-region links-region">
        <div class="section-title">LINKS <em>{{ filteredLinks.length }} / {{ store.scene.links.length }}</em></div>
        <div ref="linksScroll" class="tree-scroll links-scroll" data-testid="links-scroll" tabindex="0" role="region" aria-label="Links 列表" @scroll="onScroll" @keydown="navigate">
          <div v-if="virtual" class="virtual-spacer" :style="{ height: `${filteredLinks.length * rowHeight}px` }">
            <button v-for="(link, offset) in visibleLinks" :key="link.id" class="tree-node virtual-row" :style="{ transform: `translateY(${(virtualStart + offset) * rowHeight}px)` }" :class="{ active: store.selectedId === link.id }" :aria-current="store.selectedId === link.id ? 'true' : undefined" :data-link-id="link.id" @click="store.select('link', link.id)"><span class="link-icon">◆</span><span>{{ link.name }}</span></button>
          </div>
          <button v-else v-for="link in filteredLinks" :key="link.id" class="tree-node" :class="{ active: store.selectedId === link.id }" :aria-current="store.selectedId === link.id ? 'true' : undefined" :data-link-id="link.id" @click="store.select('link', link.id)"><span class="link-icon">◆</span><span>{{ link.name }}</span></button>
        </div>
      </section>
      <section class="tree-region joints-region">
        <div class="section-title">JOINTS <em>{{ filteredJoints.length }}</em></div>
        <div class="tree-scroll joints-scroll" tabindex="0" role="region" aria-label="Joints 列表">
          <button v-for="joint in filteredJoints" :key="joint.id" class="tree-node" :class="{ active: store.selectedId === joint.id }" :aria-current="store.selectedId === joint.id ? 'true' : undefined" @click="store.select('joint', joint.id)"><span class="joint-icon">◎</span><span>{{ joint.name }}</span><small>{{ joint.type }}</small></button>
        </div>
      </section>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useEditorStore } from '@/stores/editor'

const store = useEditorStore()
const query = ref('')
const linksScroll = ref<HTMLElement>()
const scrollTop = ref(0)
const clientHeight = ref(0)
const rowHeight = 32
let observer: ResizeObserver | undefined

const match = (value: string) => value.toLowerCase().includes(query.value.toLowerCase())
const filteredLinks = computed(() => store.scene.links.filter((item) => match(item.name)))
const filteredJoints = computed(() => store.scene.joints.filter((item) => match(item.name)))
const virtual = computed(() => filteredLinks.value.length > 200)
const virtualStart = computed(() => Math.max(0, Math.floor(scrollTop.value / rowHeight) - 5))
const visibleLinks = computed(() => virtual.value
  ? filteredLinks.value.slice(virtualStart.value, Math.min(filteredLinks.value.length, virtualStart.value + Math.ceil(clientHeight.value / rowHeight) + 10))
  : filteredLinks.value)

function onScroll() { scrollTop.value = linksScroll.value?.scrollTop || 0 }

function scrollTo(index: number) {
  const element = linksScroll.value
  if (!element || index < 0) return
  if (virtual.value) {
    const top = index * rowHeight
    const bottom = top + rowHeight
    if (top < element.scrollTop) element.scrollTop = top
    else if (bottom > element.scrollTop + element.clientHeight) element.scrollTop = bottom - element.clientHeight
  } else {
    nextTick(() => Array.from(element.querySelectorAll<HTMLElement>('[data-link-id]')).find((node) => node.dataset.linkId === filteredLinks.value[index].id)?.scrollIntoView?.({ block: 'nearest' }))
  }
}

function navigate(event: KeyboardEvent) {
  if (!['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', 'Home', 'End', 'Enter'].includes(event.key)) return
  event.preventDefault()
  let index = filteredLinks.value.findIndex((item) => item.id === store.selectedId)
  const page = Math.max(1, Math.floor((linksScroll.value?.clientHeight || rowHeight) / rowHeight))
  if (event.key === 'Home') index = 0
  else if (event.key === 'End') index = filteredLinks.value.length - 1
  else if (event.key === 'ArrowDown') index = Math.min(filteredLinks.value.length - 1, index + 1)
  else if (event.key === 'ArrowUp') index = Math.max(0, index - 1)
  else if (event.key === 'PageDown') index = Math.min(filteredLinks.value.length - 1, index + page)
  else if (event.key === 'PageUp') index = Math.max(0, index - page)
  if (index >= 0) { store.select('link', filteredLinks.value[index].id); scrollTo(index) }
}

watch(() => store.selectedId, (id) => { const index = filteredLinks.value.findIndex((item) => item.id === id); if (index >= 0) scrollTo(index) })
watch(() => store.scene.robotId, () => { scrollTop.value = 0; if (linksScroll.value) linksScroll.value.scrollTop = 0 })
onMounted(() => {
  clientHeight.value = linksScroll.value?.clientHeight || 320
  if (import.meta.env.DEV) nextTick(() => console.debug({
    backendLinkCount: store.scene.links.length,
    storeLinkCount: store.scene.links.length,
    filteredLinkCount: filteredLinks.value.length,
    renderedLinkCount: linksScroll.value?.querySelectorAll('[data-link-id]').length || 0,
  }))
  if (typeof ResizeObserver === 'undefined') return
  observer = new ResizeObserver((entries) => { clientHeight.value = Math.max(0, entries[0]?.contentRect.height || clientHeight.value) })
  if (linksScroll.value) observer.observe(linksScroll.value)
})
onBeforeUnmount(() => observer?.disconnect())
</script>

<style scoped>
.model-tree{flex:1 1 auto;min-height:0;display:grid;grid-template-rows:auto auto minmax(0,1fr) minmax(72px,35%);overflow:hidden}.tree-search,.robot-node{flex:0 0 auto}.tree-region{min-height:0;display:flex;flex-direction:column;overflow:hidden}.tree-region+.tree-region{border-top:1px solid #253542}.section-title{flex:0 0 auto}.tree-scroll{flex:1 1 auto;min-height:0;overflow-y:auto;overflow-x:hidden;overscroll-behavior:contain;scrollbar-gutter:stable;padding:2px 7px}.tree-scroll:focus-visible{outline:1px solid #31a8ed;outline-offset:-1px}.virtual-spacer{position:relative}.virtual-row{position:absolute;left:0;right:0;top:0;height:32px}.tree-node{min-height:32px}.tree-node span:nth-child(2){overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
</style>

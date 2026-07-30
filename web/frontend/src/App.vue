<template><EditorLayout /></template>
<script setup lang="ts">
import { onMounted } from 'vue'
import EditorLayout from '@/components/layout/EditorLayout.vue'

onMounted(() => {
  fetch('/api/startup/ui-interactive', { method: 'POST' }).catch(() => undefined)
  window.setTimeout(() => {
    import('@/step/directStepImport')
      .then(({ prewarmStepEngine }) => prewarmStepEngine())
      .then(() => fetch('/api/startup/opencascade-ready', { method: 'POST' }))
      .catch((error) => fetch('/api/startup/opencascade-failed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: String(error) }),
      }))
  }, 750)
})
</script>

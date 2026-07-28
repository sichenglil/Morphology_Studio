<template>
  <main class="studio" data-testid="editor-layout">
    <AppToolbar @import="importOpen=true" @validate="store.validate()" @assemble="assemblyOpen=true" @export="exportOpen=true" />
    <section class="workbench">
      <LeftSidebar />
      <RobotViewport />
      <RightInspector />
    </section>
    <BottomDock />
    <StatusBar />
    <ImportWizard v-model="importOpen" />
    <AssemblyWizard v-model="assemblyOpen" />
    <ExportDialog v-model="exportOpen" />
  </main>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { useEditorStore } from '@/stores/editor'
import AppToolbar from './AppToolbar.vue'; import LeftSidebar from './LeftSidebar.vue'; import RightInspector from './RightInspector.vue'; import BottomDock from './BottomDock.vue'; import StatusBar from './StatusBar.vue'
import RobotViewport from '@/components/viewport/RobotViewport.vue'; import ImportWizard from '@/components/dialogs/ImportWizard.vue'; import AssemblyWizard from '@/components/dialogs/AssemblyWizard.vue'; import ExportDialog from '@/components/dialogs/ExportDialog.vue'
const store=useEditorStore(); const importOpen=ref(false); const assemblyOpen=ref(false); const exportOpen=ref(false)
</script>

import { createPinia, setActivePinia } from 'pinia'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import ModelTree from '@/components/model/ModelTree.vue'
import StructureTreePanel from '@/components/model/StructureTreePanel.vue'
import JointControlPanel from '@/components/joints/JointControlPanel.vue'
import ValidationPanel from '@/components/validation/ValidationPanel.vue'
import EditorLayout from '@/components/layout/EditorLayout.vue'
import { useEditorStore } from '@/stores/editor'

vi.mock('@/api/models', () => ({
  analyzePath: vi.fn(async () => ({ format: 'urdf', entries: [] })),
  pickPath: vi.fn(async () => ({ path: '' })),
}))

const sampleScene = {
  robotId: 'sample', rootLinks: ['base'], resources: [],
  revision:0,rootTransform:{xyz:[0,0,0],rpy:[0,0,0]},assemblyJoints:[],history:{canUndo:false,canRedo:false},
  links: [{id:'base',name:'base',parentJoint:null,visuals:[],collisions:0,inertial:null},{id:'tool',name:'tool',parentJoint:'hinge',visuals:[],collisions:0,inertial:null}],
  joints: [{id:'hinge',name:'hinge',type:'revolute',parent:'base',child:'tool',origin:{xyz:[0,0,1],rpy:[0,0,0]},axis:[0,0,1],limit:{lower:-1,upper:1},value:0}],
}

beforeEach(() => { setActivePinia(createPinia()); vi.restoreAllMocks() })

describe('editor stores and panels', () => {
  it('synchronizes model tree selection with the store', async () => {
    const store=useEditorStore(); store.scene=sampleScene
    const wrapper=mount(ModelTree,{global:{stubs:{ElInput:true}}})
    const nodes=wrapper.findAll('.tree-node'); expect(nodes.length).toBe(3)
    await nodes[1].trigger('click'); expect(store.selectedId).toBe('tool'); expect(store.selectedType).toBe('link')
  })

  it('shows movable joints and validation state', () => {
    const store=useEditorStore(); store.scene=sampleScene
    const joints=mount(JointControlPanel,{global:{stubs:{ElSlider:true}}})
    expect(joints.text()).toContain('hinge')
    store.validation={errors:0,warnings:1,exportReady:true,diagnostics:[{severity:'WARNING',code:'test',message:'review'}]}
    const validation=mount(ValidationPanel,{global:{stubs:{ElButton:true}}})
    expect(validation.text()).toContain('1 警告'); expect(validation.text()).toContain('review')
  })

  it('shows the imported file as an interactive kinematic structure tree', async () => {
    const store=useEditorStore(); store.scene={...sampleScene,sourceName:'sample.urdf'}
    const wrapper=mount(StructureTreePanel)
    expect(wrapper.text()).toContain('sample.urdf')
    expect(wrapper.findAll('.structure-link').map(node=>node.text())).toEqual(['base','tool'])
    expect(wrapper.get('.structure-joint').text()).toContain('hinge · revolute')
    await wrapper.get('.structure-joint').trigger('click')
    expect(store.selectedType).toBe('joint'); expect(store.selectedId).toBe('hinge')
    await wrapper.get('[aria-label="关闭结构树"]').trigger('click')
    expect(wrapper.emitted('close')).toHaveLength(1)
  })

  it('moves and resizes the structure window and pans and zooms its canvas', async () => {
    const store=useEditorStore(); store.scene={...sampleScene,sourceName:'sample.urdf'}
    const wrapper=mount(StructureTreePanel)
    await wrapper.get('[data-testid="structure-tree-titlebar"]').trigger('pointerdown',{button:0,clientX:20,clientY:60})
    window.dispatchEvent(new MouseEvent('pointermove',{clientX:80,clientY:100})); await wrapper.vm.$nextTick()
    expect(wrapper.get('[data-testid="structure-tree-panel"]').attributes('style')).toContain('left: 76px')
    await wrapper.get('[data-testid="structure-tree-resizer"]').trigger('pointerdown',{button:0,clientX:496,clientY:414})
    window.dispatchEvent(new MouseEvent('pointermove',{clientX:536,clientY:454})); await wrapper.vm.$nextTick()
    expect(wrapper.get('[data-testid="structure-tree-panel"]').attributes('style')).toContain('width: 460px')
    await wrapper.get('[data-testid="structure-tree-canvas"]').trigger('pointerdown',{button:0,clientX:100,clientY:120})
    window.dispatchEvent(new MouseEvent('pointermove',{clientX:125,clientY:145})); await wrapper.vm.$nextTick()
    expect(wrapper.get('.structure-canvas').attributes('style')).toContain('translate(41px, 41px)')
    await wrapper.get('[aria-label="放大结构树"]').trigger('click')
    expect(wrapper.get('.structure-canvas').attributes('style')).toContain('scale(1.15)')
    window.dispatchEvent(new MouseEvent('pointerup'))
  })

  it('renders the viewport-first application regions', () => {
    const wrapper=mount(EditorLayout,{global:{stubs:{AppToolbar:true,LeftSidebar:true,RightInspector:true,BottomDock:true,StatusBar:true,RobotViewport:true,ImportWizard:true,AssemblyWizard:true,ExportDialog:true}}})
    expect(wrapper.get('[data-testid="editor-layout"]').attributes('data-testid')).toBe('editor-layout')
  })

  it('directly imports a path received from native file drop', async () => {
    const store=useEditorStore(); store.open=vi.fn(async()=>undefined) as typeof store.open
    const wrapper=mount(EditorLayout,{global:{stubs:{AppToolbar:true,LeftSidebar:true,RightInspector:true,BottomDock:true,StatusBar:true,RobotViewport:true,ImportWizard:true,AssemblyWizard:true,ExportDialog:true}}})
    window.dispatchEvent(new CustomEvent('morphology-files-dropped',{detail:{paths:['fixtures/robot.urdf']}}))
    await flushPromises()
    expect(store.open).toHaveBeenCalledWith({path:'fixtures/robot.urdf'})
    wrapper.unmount()
  })
})

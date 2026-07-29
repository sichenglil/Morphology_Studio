import { createPinia, setActivePinia } from 'pinia'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import ModelTree from '@/components/model/ModelTree.vue'
import JointControlPanel from '@/components/joints/JointControlPanel.vue'
import ValidationPanel from '@/components/validation/ValidationPanel.vue'
import EditorLayout from '@/components/layout/EditorLayout.vue'
import { useEditorStore } from '@/stores/editor'

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

  it('renders the viewport-first application regions', () => {
    const wrapper=mount(EditorLayout,{global:{stubs:{AppToolbar:true,LeftSidebar:true,RightInspector:true,BottomDock:true,StatusBar:true,RobotViewport:true,ImportWizard:true,AssemblyWizard:true,ExportDialog:true}}})
    expect(wrapper.get('[data-testid="editor-layout"]').attributes('data-testid')).toBe('editor-layout')
  })
})

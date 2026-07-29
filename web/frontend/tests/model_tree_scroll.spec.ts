import { createPinia, setActivePinia } from 'pinia'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'
import ModelTree from '@/components/model/ModelTree.vue'
import { useEditorStore } from '@/stores/editor'

const links = (count: number) => Array.from({ length: count }, (_, index) => ({
  id: `link-${index}`, name: `link-${index}`, parentJoint: null, visuals: [], collisions: 0, inertial: null,
}))

function mountTree(count: number) {
  const store = useEditorStore()
  store.scene = { robotId: 'stress-model', rootLinks: ['link-0'], links: links(count), joints: [], resources: [], revision: 0, rootTransform: { xyz: [0, 0, 0], rpy: [0, 0, 0] }, assemblyJoints: [], history: { canUndo: false, canRedo: false } }
  return { store, wrapper: mount(ModelTree, { global: { stubs: { ElInput: { template: '<input />' } } } }) }
}

beforeEach(() => setActivePinia(createPinia()))

describe('model tree scrolling and virtualization', () => {
  it('renders a small 20-link model without virtualization', () => {
    const { wrapper } = mountTree(20)
    expect(wrapper.findAll('[data-link-id]')).toHaveLength(20)
    expect(wrapper.find('.virtual-spacer').exists()).toBe(false)
  })

  it('renders every link when the list has 100 entries', () => {
    const { wrapper } = mountTree(100)
    expect(wrapper.findAll('[data-link-id]')).toHaveLength(100)
    expect(wrapper.text()).toContain('100 / 100')
  })

  for (const count of [500, 1000]) it(`virtualizes ${count} links without truncating the data count`, () => {
    const { wrapper } = mountTree(count)
    expect(wrapper.text()).toContain(`${count} / ${count}`)
    expect(wrapper.findAll('[data-link-id]').length).toBeGreaterThan(0)
    expect(wrapper.findAll('[data-link-id]').length).toBeLessThan(50)
    expect(wrapper.get('.virtual-spacer').attributes('style')).toContain(`${count * 32}px`)
  })

  it('selects and reveals the last virtualized link with the End key', async () => {
    const { store, wrapper } = mountTree(1000)
    await wrapper.get('[data-testid="links-scroll"]').trigger('keydown', { key: 'End' })
    expect(store.selectedId).toBe('link-999')
    expect((wrapper.get('[data-testid="links-scroll"]').element as HTMLElement).scrollTop).toBeGreaterThan(0)
  })

  it('restores the complete list after clearing a search filter', async () => {
    const { wrapper } = mountTree(100)
    ;(wrapper.vm as unknown as { query: string }).query = 'link-99'
    await wrapper.vm.$nextTick()
    expect(wrapper.findAll('[data-link-id]')).toHaveLength(1)
    ;(wrapper.vm as unknown as { query: string }).query = ''
    await wrapper.vm.$nextTick()
    expect(wrapper.findAll('[data-link-id]')).toHaveLength(100)
  })
})

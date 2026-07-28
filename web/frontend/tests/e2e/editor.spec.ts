import path from 'node:path'
import { expect, test } from '@playwright/test'

for (const viewport of [{width:1440,height:900},{width:1920,height:1080}]) {
  test(`editor layout ${viewport.width}x${viewport.height}`, async ({page}) => {
    await page.setViewportSize(viewport)
    await page.goto('/')
    await expect(page.getByTestId('editor-layout')).toBeVisible()
    await expect(page.getByTestId('robot-viewport')).toBeVisible()
    await expect(page.getByTestId('model-tree')).toBeVisible()
    await expect(page.getByTestId('right-inspector')).toBeVisible()
    await expect(page.getByTestId('bottom-dock')).toBeVisible()
  })
}

test('loads a real portable URDF into tree and viewport', async ({page}) => {
  await page.setViewportSize({width:1440,height:900})
  await page.goto('/')
  await page.getByRole('button',{name:'导入模型',exact:true}).click()
  const model=path.resolve('../../build/packages/ur5e/robot.urdf')
  await page.getByPlaceholder('URDF、Xacro、MJCF 或模型目录').fill(model)
  await page.getByRole('button',{name:'导入并显示',exact:true}).click()
  await expect(page.getByText('13 Links')).toBeVisible()
  await expect(page.getByText('12 Joints')).toBeVisible()
  await expect(page.getByRole('button',{name:'◎ shoulder_pan_joint revolute',exact:true})).toBeVisible()
})

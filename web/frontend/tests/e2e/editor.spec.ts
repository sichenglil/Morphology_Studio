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

test('loads the generic portable URDF into tree and viewport', async ({page}) => {
  await page.setViewportSize({width:1440,height:900})
  await page.goto('/')
  await page.getByRole('button',{name:'导入模型',exact:true}).click()
  const model=path.resolve('../../assets/robot_models/ur5e_hx5_right/robot.urdf')
  await page.getByPlaceholder('URDF、Xacro、MJCF 或模型目录').fill(model)
  await page.getByRole('button',{name:'导入并显示',exact:true}).click()
  await expect(page.getByText('40 Links')).toBeVisible()
  await expect(page.getByText('39 Joints')).toBeVisible()
  await expect(page.getByTestId('structure-tree-panel')).toHaveCount(0)
  await page.getByTestId('open-structure-tree').click()
  await expect(page.getByTestId('structure-tree-panel')).toBeVisible()
  await expect(page.getByTestId('structure-tree-panel')).toContainText('robot.urdf')
  await expect(page.getByTestId('structure-tree-panel').locator('.structure-link')).toHaveCount(40)
  await page.getByRole('button',{name:'关闭结构树'}).click()
  await expect(page.getByTestId('structure-tree-panel')).toHaveCount(0)
})

test('mouse selection and transform toolbar acceptance', async ({page}) => {
  const pageErrors:string[]=[];page.on('pageerror',error=>pageErrors.push(error.message))
  await page.setViewportSize({width:1440,height:900})
  await page.goto('/')
  await page.getByRole('button',{name:'导入模型',exact:true}).click()
  await page.getByPlaceholder('URDF、Xacro、MJCF 或模型目录').fill(path.resolve('../../assets/robot_models/ur5e_hx5_right/robot.urdf'))
  await page.getByRole('button',{name:'导入并显示',exact:true}).click()
  await page.getByRole('button',{name:/ur5e_base_link$/}).first().click()
  await expect(page.locator('[data-testid="robot-viewport"] canvas')).toHaveCount(1)
  await expect(page.getByText('已选: ur5e_base_link')).toBeVisible()
  await page.screenshot({path:path.resolve('../../build/ui/acceptance/transform/link_selected.png')})
  await page.keyboard.press('KeyE')
  await expect(page.getByTestId('transform-toolbar')).toContainText('旋转 E')
  await page.screenshot({path:path.resolve('../../build/ui/acceptance/transform/rotate_mode.png')})
  await page.getByRole('button',{name:'装配编辑'}).click()
  await page.getByRole('button',{name:/ur5e_upper_arm_link$/}).first().click()
  await expect(page.getByText('已选: ur5e_upper_arm_link')).toBeVisible()
  await page.screenshot({path:path.resolve('../../build/ui/acceptance/transform/kinematic_gizmo.png')})
  expect(pageErrors).toEqual([])
})

for (const model of [
  {name:'ur5e-hx5-right',path:'../../assets/robot_models/ur5e_hx5_right/robot.urdf'},
]) test(`${model.name} joint preview is local and persistent`,async({page})=>{
  test.setTimeout(120_000)
  let commits=0;page.on('request',request=>{if(request.url().includes('/joint-states/commit'))commits++})
  await page.setViewportSize({width:1440,height:900});await page.goto('/?debugPerformance=1');await page.getByRole('button',{name:'导入模型',exact:true}).click();await page.getByPlaceholder('URDF、Xacro、MJCF 或模型目录').fill(path.resolve(model.path));await page.getByRole('button',{name:'导入并显示',exact:true}).click();await expect(page.getByTestId('performance-panel')).toBeVisible();
  await expect.poll(()=>page.evaluate(async()=>{try{await(window as unknown as {benchmarkJointRuntime:(iterations:number)=>Promise<unknown>}).benchmarkJointRuntime(1);return true}catch{return false}}),{timeout:15000}).toBe(true);const benchmark=await page.evaluate(()=>((window as unknown as {benchmarkJointRuntime:(iterations:number)=>Promise<{fps:number;averageUpdateMs:number;metrics:{sceneRebuilds:number;meshLoads:number}}>} ).benchmarkJointRuntime(120)));expect(benchmark.averageUpdateMs).toBeLessThan(1);expect(benchmark.metrics.sceneRebuilds).toBe(1)
  const canvas=page.locator('[data-testid="robot-viewport"] canvas');await canvas.evaluate(element=>element.dataset.runtimeIdentity='stable');const handle=page.locator('.joint-row .el-slider__button-wrapper').first(),box=await handle.boundingBox();expect(box).not.toBeNull();await page.mouse.move(box!.x+box!.width/2,box!.y+box!.height/2);await page.mouse.down();await page.mouse.move(box!.x+box!.width/2+120,box!.y+box!.height/2,{steps:30});expect(commits).toBe(0);await page.mouse.up();await page.waitForTimeout(150);if(commits===0){await handle.focus();await page.keyboard.press('ArrowRight')}await expect.poll(()=>commits).toBe(1);await expect(canvas).toHaveAttribute('data-runtime-identity','stable');await expect(page.getByTestId('performance-panel')).toContainText('Rebuilds 1');
  console.log(`PERF ${model.name}: ${JSON.stringify(benchmark)} | ${await page.getByTestId('performance-panel').innerText()}`)
})



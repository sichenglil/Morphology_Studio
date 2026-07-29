import fs from 'node:fs'
import path from 'node:path'
import { expect, test } from '@playwright/test'

test('capture UR5e and HX5 hand assembly workflow', async ({ page }) => {
  test.skip(process.env.CAPTURE_ASSEMBLY_DEMO !== '1', 'capture-only workflow')
  test.setTimeout(120_000)

  const output = path.resolve('../../artifacts/temporary/assembly-demo-frames')
  const ur5e = path.resolve('../../assets/assembly_demo_models/ur5e/robot.urdf')
  const hand = path.resolve(
    '../../assets/assembly_demo_models/hx5_d20_rev2_right/robot.urdf',
  )
  const exported = path.resolve(
    '../../artifacts/temporary/assembly-demo-export/ur5e_hx5_right.urdf',
  )
  fs.mkdirSync(output, { recursive: true })
  fs.mkdirSync(path.dirname(exported), { recursive: true })
  for (const file of fs.readdirSync(output)) fs.rmSync(path.join(output, file))
  if (fs.existsSync(exported)) fs.rmSync(exported)

  await page.setViewportSize({ width: 1280, height: 720 })
  await page.goto('/')
  let frame = 0
  const capture = async (count = 1) => {
    for (let index = 0; index < count; index++) {
      await page.screenshot({
        path: path.join(output, `${String(frame++).padStart(3, '0')}.png`),
      })
      await page.waitForTimeout(70)
    }
  }
  const blurPrivatePath = async (input: ReturnType<typeof page.locator>) => {
    await input.evaluate((element) => {
      const target = element as HTMLElement
      target.style.filter = 'blur(6px)'
      target.style.userSelect = 'none'
    })
  }

  await capture(6)
  await page.getByRole('button', { name: '导入模型', exact: true }).click()
  await capture(7)
  const ur5eInput = page.getByPlaceholder('URDF、Xacro、MJCF 或模型目录')
  await ur5eInput.fill(ur5e)
  await blurPrivatePath(ur5eInput)
  await capture(8)
  await page.getByRole('button', { name: '导入并显示', exact: true }).click()
  await expect(page.getByText('13 Links')).toBeVisible()
  await page.waitForTimeout(1_500)
  await capture(12)

  await page.getByTestId('toolbar').getByRole('button', { name: '装配', exact: true }).click()
  await capture(7)
  await page.locator('.assembly-grid .el-select').click()
  await page.getByRole('option', { name: 'tool0', exact: true }).click()
  const handInput = page.getByPlaceholder('选择另一个模型文件')
  await handInput.fill(hand)
  await blurPrivatePath(handInput)
  await page.getByPlaceholder('填写子模型根 Link').fill('world')
  await capture(12)
  await page.getByRole('button', { name: '创建 fixed 连接', exact: true }).click()
  await expect(page.getByText('40 Links')).toBeVisible()
  await page.waitForTimeout(2_000)
  await capture(12)

  await page.getByTestId('toolbar').getByRole('button', { name: '导出', exact: true }).click()
  await capture(6)
  const exportDialog = page.getByLabel('导出模型')
  const outputInput = exportDialog.locator('input')
  await outputInput.fill(exported)
  await blurPrivatePath(outputInput)
  await capture(10)
  await exportDialog.getByRole('button', { name: '导出', exact: true }).click()
  await expect.poll(() => fs.existsSync(exported)).toBeTruthy()
  const message = page.locator('.el-message').last()
  await expect(message).toBeVisible()
  await message.evaluate((element) => {
    const content = element.querySelector('.el-message__content')
    if (content) content.textContent = '模型导出成功'
  })
  await capture(14)
})

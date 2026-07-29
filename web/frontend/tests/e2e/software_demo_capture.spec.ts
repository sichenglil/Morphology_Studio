import fs from 'node:fs'
import path from 'node:path'
import { expect, test } from '@playwright/test'

test('capture real robot operation inside Morphology Studio', async ({ page }) => {
  test.skip(process.env.CAPTURE_SOFTWARE_DEMO !== '1', 'capture-only workflow')
  test.setTimeout(90_000)
  const output = path.resolve('../../artifacts/temporary/software-demo-frames')
  fs.mkdirSync(output, { recursive: true })
  for (const file of fs.readdirSync(output)) fs.rmSync(path.join(output, file))

  await page.setViewportSize({ width: 1280, height: 720 })
  await page.goto('/')
  await expect(page.getByTestId('model-preview')).toBeVisible()
  await page.getByRole('button', { name: '加载到三维视图', exact: true }).click()
  await expect(page.getByText('40 Links')).toBeVisible()
  await expect(page.locator('[data-testid="robot-viewport"] canvas')).toHaveCount(1)
  // Mesh resources arrive asynchronously after the scene manifest. Wait for
  // the real arm to be painted before recording the first visible frame.
  await page.waitForTimeout(3_000)
  await page.locator('[data-testid="model-preview"]').evaluate((element) => {
    ;(element as HTMLElement).style.display = 'none'
  })

  const capture = async (index: number) => {
    await page.waitForTimeout(55)
    await page.screenshot({ path: path.join(output, `${String(index).padStart(3, '0')}.png`) })
  }
  let frame = 0
  for (let index = 0; index < 7; index++) await capture(frame++)

  const handle = page
    .locator('[data-joint-id="ur5e_shoulder_pan_joint"] .el-slider__button-wrapper')
  await handle.scrollIntoViewIfNeeded()
  const box = await handle.boundingBox()
  expect(box).not.toBeNull()
  const startX = box!.x + box!.width / 2
  const y = box!.y + box!.height / 2
  await page.mouse.move(startX, y)
  await page.mouse.down()
  for (let step = 0; step <= 22; step++) {
    await page.mouse.move(startX + step * 8, y)
    await capture(frame++)
  }
  for (let step = 21; step >= 0; step--) {
    await page.mouse.move(startX + step * 8, y)
    await capture(frame++)
  }
  await page.mouse.up()
  for (let index = 0; index < 7; index++) await capture(frame++)
})

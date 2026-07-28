import fs from 'node:fs'
import path from 'node:path'
import { expect, test } from '@playwright/test'

const fixture = path.resolve('../../build/ui/acceptance/scroll-panels/links-100.urdf')
const shots = path.resolve('../../build/ui/acceptance/scroll-panels')

test.beforeAll(() => {
  fs.mkdirSync(shots, { recursive: true })
  const linkXml = Array.from({ length: 100 }, (_, index) => `<link name="link_${index}"><visual><geometry><box size="0.02 0.02 0.02"/></geometry></visual></link>`).join('')
  const jointXml = Array.from({ length: 99 }, (_, index) => `<joint name="joint_${index}" type="fixed"><parent link="link_${index}"/><child link="link_${index + 1}"/><origin xyz="0.03 0 0"/></joint>`).join('')
  fs.writeFileSync(fixture, `<robot name="scroll_acceptance">${linkXml}${jointXml}</robot>`)
})

async function load(page: import('@playwright/test').Page) {
  await page.goto('/')
  await page.getByRole('button', { name: '导入模型', exact: true }).click()
  await page.getByPlaceholder('URDF、Xacro、MJCF 或模型目录').fill(fixture)
  await page.getByRole('button', { name: '导入并显示', exact: true }).click()
  await expect(page.getByText('100 Links')).toBeVisible()
  await expect(page.getByTestId('links-scroll')).toBeVisible()
}

test('Links scroll independently and keyboard selection reaches the final item', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 })
  await load(page)
  const list = page.getByTestId('links-scroll')
  const dimensions = await list.evaluate((element) => ({ client: element.clientHeight, scroll: element.scrollHeight, overflowY: getComputedStyle(element).overflowY, rendered: element.querySelectorAll('[data-link-id]').length }))
  console.log(`LINK_PANEL_METRICS ${JSON.stringify(dimensions)}`)
  expect(dimensions).toMatchObject({ client: expect.any(Number), scroll: expect.any(Number), overflowY: 'auto', rendered: 100 })
  expect(await list.evaluate((element) => element.scrollHeight > element.clientHeight)).toBe(true)
  await page.screenshot({ path: path.join(shots, 'links_top.png') })
  await list.hover({ position: { x: 120, y: 120 } }); await page.mouse.wheel(0, 550)
  await expect.poll(() => list.evaluate((element) => element.scrollTop)).toBeGreaterThan(0)
  await page.screenshot({ path: path.join(shots, 'links_middle.png') })
  await list.focus(); await page.keyboard.press('End')
  await expect(page.getByText('已选: link_99')).toBeVisible()
  await expect.poll(() => list.evaluate((element) => element.scrollTop + element.clientHeight >= element.scrollHeight - 2)).toBe(true)
  await page.screenshot({ path: path.join(shots, 'last_link_selected.png') })
  await page.screenshot({ path: path.join(shots, 'links_bottom.png') })
})

test('Resources and Semantics remain accessible without resetting Links scroll', async ({ page }) => {
  await page.setViewportSize({ width: 1100, height: 700 }); await load(page)
  const list = page.getByTestId('links-scroll'); await list.evaluate((element) => { element.scrollTop = 300; element.dispatchEvent(new Event('scroll')) })
  const before = await list.evaluate((element) => element.scrollTop)
  await page.getByRole('tab', { name: '资源' }).click(); await expect(page.getByTestId('resource-browser')).toBeVisible(); await page.screenshot({ path: path.join(shots, 'resources_visible.png') })
  await page.getByRole('tab', { name: '模型' }).click(); expect(await list.evaluate((element) => element.scrollTop)).toBe(before)
  await page.getByRole('tab', { name: '语义' }).click(); await expect(page.getByTestId('semantic-inspector')).toBeVisible(); await page.screenshot({ path: path.join(shots, 'semantics_visible.png') })
  await page.screenshot({ path: path.join(shots, 'compact_window.png') })
})

test('large-window layout keeps all work areas visible', async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 1080 }); await load(page)
  for (const id of ['links-scroll', 'robot-viewport', 'right-inspector', 'bottom-dock']) await expect(page.getByTestId(id)).toBeVisible()
  await page.screenshot({ path: path.join(shots, 'large_window.png') })
  const viewport = page.getByTestId('robot-viewport'); const before = await viewport.screenshot()
  const list = page.getByTestId('links-scroll'); const box = await list.boundingBox(); await page.mouse.move(box!.x + 20, box!.y + 20); await page.mouse.wheel(0, 250)
  expect(await viewport.screenshot()).toEqual(before)
  await page.screenshot({ path: path.join(shots, 'scroll_not_affecting_viewport.png') })
})

test('wheel over the Three.js viewport still zooms the camera', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 }); await load(page)
  const canvas = page.locator('[data-testid="robot-viewport"] canvas')
  await page.waitForTimeout(200); const before = await canvas.screenshot(); const box = await canvas.boundingBox(); expect(box).not.toBeNull()
  await page.mouse.move(box!.x + box!.width / 2, box!.y + box!.height / 2); await page.mouse.wheel(0, -600); await page.waitForTimeout(200)
  expect(await canvas.screenshot()).not.toEqual(before)
})

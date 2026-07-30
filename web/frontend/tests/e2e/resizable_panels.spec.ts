import { expect, test, type Locator, type Page } from '@playwright/test'

async function drag(page: Page, handle: Locator, deltaX: number, deltaY: number) {
  const box = await handle.boundingBox()
  if (!box) throw new Error('Resize handle is not visible')
  const x = box.x + box.width / 2
  const y = box.y + box.height / 2
  await page.mouse.move(x, y)
  await page.mouse.down()
  await page.mouse.move(x + deltaX, y + deltaY, { steps: 5 })
  await page.mouse.up()
}

test('left, right and bottom panels can be resized', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto('/')

  const left = page.getByTestId('left-sidebar')
  const right = page.getByTestId('right-inspector')
  const bottom = page.getByTestId('bottom-dock')
  const leftBefore = await left.boundingBox()
  const rightBefore = await right.boundingBox()
  const bottomBefore = await bottom.boundingBox()

  await drag(page, page.getByTestId('left-resizer'), 80, 0)
  await drag(page, page.getByTestId('right-resizer'), -70, 0)
  await drag(page, page.getByTestId('bottom-resizer'), 0, -60)

  await expect.poll(async () => (await left.boundingBox())?.width).toBeCloseTo((leftBefore?.width ?? 0) + 80, 0)
  await expect.poll(async () => (await right.boundingBox())?.width).toBeCloseTo((rightBefore?.width ?? 0) + 70, 0)
  await expect.poll(async () => (await bottom.boundingBox())?.height).toBeCloseTo((bottomBefore?.height ?? 0) + 60, 0)
})

test('resize handles support keyboard control and reset', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto('/')
  const left = page.getByTestId('left-sidebar')
  const handle = page.getByTestId('left-resizer')
  const initial = await left.boundingBox()

  await handle.focus()
  await handle.press('ArrowRight')
  await expect.poll(async () => (await left.boundingBox())?.width).toBeCloseTo((initial?.width ?? 0) + 10, 0)

  await handle.dblclick()
  await expect.poll(async () => (await left.boundingBox())?.width).toBeCloseTo(initial?.width ?? 0, 0)
})

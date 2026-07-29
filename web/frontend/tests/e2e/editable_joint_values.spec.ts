import fs from 'node:fs'
import path from 'node:path'
import {expect,test} from '@playwright/test'

const output=path.resolve('../../build/ui/acceptance/editable-joint-values')
test('editable joint values synchronize preview, units, limits and poses',async({page})=>{
  fs.mkdirSync(output,{recursive:true});let commits=0;page.on('request',request=>{if(request.url().includes('/joint-states/commit'))commits++})
  await page.setViewportSize({width:1440,height:900});await page.goto('/?debugPerformance=1')
  await page.locator('[data-testid="toolbar"] button').filter({hasText:/导入模型|瀵煎叆妯/}).click()
  await page.locator('.el-dialog input').first().fill(path.resolve('../../assets/robot_models/ur5e_hx5_right/robot.urdf'));await page.locator('.el-dialog__footer .el-button--primary').click()
  const row=page.locator('[data-joint-id="ur5e_shoulder_pan_joint"]'),input=row.locator('input');await expect(input).toBeVisible();await page.screenshot({path:path.join(output,'joint_value_idle.png')})
  await input.focus();await page.screenshot({path:path.join(output,'joint_value_focused.png')});await input.fill('1.');await page.screenshot({path:path.join(output,'joint_value_editing.png')});expect(commits).toBe(0)
  await input.fill('-0.5');await page.screenshot({path:path.join(output,'joint_value_negative.png')});await page.keyboard.press('Enter');await expect.poll(()=>commits).toBe(1)
  await page.getByTestId('rotation-unit').click();await page.locator('.el-select-dropdown__item').filter({hasText:'deg'}).last().click();await expect(input).toHaveValue(/-28\.648/);await page.screenshot({path:path.join(output,'joint_value_degrees.png')})
  await input.fill('999');await page.screenshot({path:path.join(output,'joint_value_limit_warning.png')});await page.keyboard.press('Enter');await expect.poll(()=>commits).toBe(2);await page.screenshot({path:path.join(output,'slider_numeric_sync.png')})
  const last=page.locator('.joint-row').last();await last.scrollIntoViewIfNeeded();await expect(last.locator('input')).toBeVisible();await page.screenshot({path:path.join(output,'last_joint_editable.png')})
  await page.getByRole('button',{name:/保存姿态|淇濆瓨濮/}).click();await page.locator('.el-message-box input').fill('inspection_pose');await page.locator('.el-message-box__btns .el-button--primary').click();await page.getByRole('button',{name:/全部归零|鍏ㄩ儴褰/}).click();await page.waitForTimeout(150);await page.getByTestId('joint-controls').getByRole('button',{name:'加载',exact:true}).click();await page.waitForTimeout(150);await page.screenshot({path:path.join(output,'pose_loaded.png')})
  await expect(page.getByTestId('performance-panel')).toContainText('Rebuilds 1')
})


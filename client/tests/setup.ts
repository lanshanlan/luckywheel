/**
 * 前端测试配置
 */
import { vi } from 'vitest'

// 模拟 uni-app 全局对象
const mockUni = {
  request: vi.fn(),
  showToast: vi.fn(),
  navigateTo: vi.fn(),
  redirectTo: vi.fn(),
  getStorageSync: vi.fn(() => ''),
  setStorageSync: vi.fn(),
  removeStorageSync: vi.fn()
}

// 设置全局 uni 对象
;(global as any).uni = mockUni

// 模拟 getCurrentPages
;(global as any).getCurrentPages = vi.fn(() => [
  { options: { id: '1' } }
])

// 导出模拟对象供测试使用
export { mockUni }
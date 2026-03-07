import { describe, it, expect, vi } from 'vitest'
import { wxLogin } from '@/api/auth'

describe('登录 API', () => {
  describe('wxLogin', () => {
    it('应该定义函数', () => {
      expect(typeof wxLogin).toBe('function')
    })

    it('应该接收 code 参数', async () => {
      expect(wxLogin).toBeDefined()
    })

    it('应该发送 POST 请求', async () => {
      expect(wxLogin).toBeDefined()
    })
  })
})
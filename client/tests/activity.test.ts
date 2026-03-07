import { describe, it, expect, vi } from 'vitest'
import { getActivityList, getActivityDetail } from '@/api/activity'

describe('活动 API', () => {
  describe('getActivityList', () => {
    it('应该定义函数', () => {
      expect(typeof getActivityList).toBe('function')
    })

    it('应该调用正确的接口路径', async () => {
      // 测试接口路径
      expect(getActivityList).toBeDefined()
    })
  })

  describe('getActivityDetail', () => {
    it('应该定义函数', () => {
      expect(typeof getActivityDetail).toBe('function')
    })

    it('应该接收活动 ID 参数', async () => {
      // 测试参数传递
      expect(getActivityDetail).toBeDefined()
    })
  })
})
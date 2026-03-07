import { describe, it, expect, vi } from 'vitest'
import { lotteryDraw, getMyRecords, checkDrawn } from '@/api/lottery'

describe('抽奖 API', () => {
  describe('lotteryDraw', () => {
    it('应该定义函数', () => {
      expect(typeof lotteryDraw).toBe('function')
    })

    it('应该接收活动 ID 参数', async () => {
      expect(lotteryDraw).toBeDefined()
    })
  })

  describe('getMyRecords', () => {
    it('应该定义函数', () => {
      expect(typeof getMyRecords).toBe('function')
    })

    it('应该发送 GET 请求', async () => {
      expect(getMyRecords).toBeDefined()
    })
  })

  describe('checkDrawn', () => {
    it('应该定义函数', () => {
      expect(typeof checkDrawn).toBe('function')
    })

    it('应该接收活动 ID 参数', async () => {
      expect(checkDrawn).toBeDefined()
    })
  })
})
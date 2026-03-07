// 抽奖相关API
import { request } from './index'

// 执行抽奖
export function lotteryDraw(activityId: number) {
  return request({
    url: '/api/lottery/draw',
    method: 'POST',
    data: { activity_id: activityId }
  })
}

// 获取我的抽奖记录
export function getMyRecords() {
  return request({
    url: '/api/lottery/records',
    method: 'GET'
  })
}

// 检查是否已抽奖
export function checkDrawn(activityId: number) {
  return request({
    url: `/api/lottery/check/${activityId}`,
    method: 'GET'
  })
}
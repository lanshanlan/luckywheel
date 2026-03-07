// 活动相关API
import { request } from './index'

// 获取活动列表
export function getActivityList() {
  return request({
    url: '/api/activities',
    method: 'GET'
  })
}

// 获取活动详情
export function getActivityDetail(id: number) {
  return request({
    url: `/api/activities/${id}`,
    method: 'GET'
  })
}
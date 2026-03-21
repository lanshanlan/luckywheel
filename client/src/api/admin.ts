// 管理接口 API
import { request } from './index'

// 检查是否为管理员
export function checkAdmin() {
  return request({
    url: '/api/admin/check'
  })
}

// ============ 活动管理 ============

// 创建活动
export function createActivity(data: {
  title: string
  description?: string
  status?: number
  start_time?: string
  end_time?: string
}) {
  return request({
    url: '/api/admin/activities',
    method: 'POST',
    data
  })
}

// 修改活动
export function updateActivity(id: number, data: {
  title?: string
  description?: string
  status?: number
  start_time?: string
  end_time?: string
}) {
  return request({
    url: `/api/admin/activities/${id}`,
    method: 'PUT',
    data
  })
}

// 删除活动
export function deleteActivity(id: number) {
  return request({
    url: `/api/admin/activities/${id}`,
    method: 'DELETE'
  })
}

// ============ 奖品管理 ============

// 添加奖品
export function createPrize(data: {
  activity_id: number
  name: string
  image_url?: string
  probability: number
  stock: number
  sort_order?: number
  prize_type?: number      // 0-普通奖品，1-神秘大奖
  guarantee_count?: number // 心愿次数
}) {
  return request({
    url: '/api/admin/prizes',
    method: 'POST',
    data
  })
}

// 修改奖品
export function updatePrize(id: number, data: {
  name?: string
  image_url?: string
  probability?: number
  stock?: number
  sort_order?: number
  prize_type?: number      // 0-普通奖品，1-神秘大奖
  guarantee_count?: number // 心愿次数
}) {
  return request({
    url: `/api/admin/prizes/${id}`,
    method: 'PUT',
    data
  })
}

// 删除奖品
export function deletePrize(id: number) {
  return request({
    url: `/api/admin/prizes/${id}`,
    method: 'DELETE'
  })
}

// ============ 抽奖记录管理 ============

// 获取所有抽奖记录
export function getAllRecords(activityId?: number) {
  const url = activityId
    ? `/api/admin/records?activity_id=${activityId}`
    : '/api/admin/records'
  return request({ url })
}
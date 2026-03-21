// 用户信息相关API
import { request } from './index'

// 获取用户信息
export function getUserProfile() {
  return request({
    url: '/api/user/profile',
    method: 'GET'
  })
}

// 更新用户昵称
export function updateUserProfile(data: { nickname: string }) {
  return request({
    url: '/api/user/profile',
    method: 'PUT',
    data
  })
}
// 登录相关API
import { request } from './index'

// 微信登录
export function wxLogin(code: string) {
  return request({
    url: '/api/auth/login',
    method: 'POST',
    data: { code }
  })
}
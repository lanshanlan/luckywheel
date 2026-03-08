// 请求封装
// const BASE_URL = 'http://localhost:8000' // 开发环境
const BASE_URL = 'https://www.lanshan.tech' // 生产环境

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
}

interface ApiResponse<T = any> {
  code: number
  data: T
  message: string
}

// 获取存储的token
function getToken(): string {
  return uni.getStorageSync('token') || ''
}

// 请求拦截
function request<T = any>(options: RequestOptions): Promise<ApiResponse<T>> {
  return new Promise((resolve, reject) => {
    const token = getToken()

    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      success: (res: any) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          // token过期，跳转登录
          uni.removeStorageSync('token')
          uni.showToast({
            title: '请先登录',
            icon: 'none'
          })
          reject(new Error('未登录'))
        } else {
          reject(new Error(res.data?.detail || '请求失败'))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

export { request, BASE_URL }
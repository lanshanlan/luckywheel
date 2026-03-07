<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { wxLogin,
  // devLogin
} from '@/api/auth'

// 是否为开发环境
// const IS_DEV = false // 生产环境改为 false

onLaunch(() => {
  console.log('App Launch')
  // 应用启动时自动登录
  autoLogin()
})

onShow(() => {
  console.log('App Show')
})

onHide(() => {
  console.log('App Hide')
})

// 自动登录
async function autoLogin() {
  const token = uni.getStorageSync('token')
  if (token) {
    console.log('已有token，跳过登录')
    return
  }

  try {
    // 开发环境使用模拟登录
    // if (IS_DEV) {
    //   console.log('开发环境，使用模拟登录')
    //   const res = await devLogin()
    //   if (res?.token) {
    //     uni.setStorageSync('token', res.token)
    //     console.log('模拟登录成功')
    //   }
    //   return
    // }

    // 生产环境使用微信登录
    const loginRes = await new Promise<UniApp.LoginRes>((resolve, reject) => {
      uni.login({
        success: resolve,
        fail: reject
      })
    })

    if (!loginRes.code) {
      console.error('获取登录code失败')
      return
    }

    const res = await wxLogin(loginRes.code)
    console.log('test res', res)
    if (res?.token) {
      uni.setStorageSync('token', res.token)
      console.log('登录成功')
    }
  } catch (e) {
    console.error('自动登录失败', e)
  }
}
</script>

<style>
/* 全局样式 */
page {
  background-color: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
}

/* 通用样式 */
.container {
  padding: 20rpx;
}

.btn-primary {
  background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%);
  color: #fff;
  border-radius: 50rpx;
  padding: 24rpx 48rpx;
  font-size: 32rpx;
  text-align: center;
}

.text-center {
  text-align: center;
}

.mt-20 {
  margin-top: 20rpx;
}

.mt-40 {
  margin-top: 40rpx;
}
</style>
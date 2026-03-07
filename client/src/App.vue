<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'

onLaunch(() => {
  console.log('App Launch')
})

onShow(() => {
  console.log('App Show')
})

onHide(() => {
  console.log('App Hide')
})
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
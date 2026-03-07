<template>
  <view class="container">
    <!-- 活动标题 -->
    <view class="activity-header">
      <text class="activity-title">{{ activity.title }}</text>
      <text class="activity-desc">{{ activity.description }}</text>
    </view>

    <!-- 轮盘组件 -->
    <view class="wheel-container">
      <LuckyWheel
        :prizes="prizes"
        :spinning="spinning"
        :result-index="resultIndex"
        @spin="handleSpin"
      />
    </view>

    <!-- 结果弹窗 -->
    <view v-if="showResult" class="result-modal" @click="closeResult">
      <view class="result-content" @click.stop>
        <text class="result-title">{{ isWon ? '恭喜中奖！' : '很遗憾' }}</text>
        <text class="result-prize">{{ resultPrize }}</text>
        <button class="btn-close" @click="closeResult">关闭</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import LuckyWheel from '@/components/LuckyWheel/LuckyWheel.vue'
import { getActivityDetail } from '@/api/activity'
import { lotteryDraw, checkDrawn } from '@/api/lottery'

interface Prize {
  id: number
  name: string
  probability: number
  sort_order: number
}

interface Activity {
  id: number
  title: string
  description: string
  prizes: Prize[]
}

const activityId = ref<number>(0)
const activity = ref<Activity>({
  id: 0,
  title: '',
  description: '',
  prizes: []
})
const prizes = ref<Prize[]>([])
const spinning = ref(false)
const resultIndex = ref(-1)
const showResult = ref(false)
const isWon = ref(false)
const resultPrize = ref('')

onMounted(() => {
  // 获取页面参数
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  activityId.value = Number(currentPage.options?.id || 0)

  if (activityId.value) {
    loadActivity()
    checkUserDrawn()
  }
})

async function loadActivity() {
  try {
    const res = await getActivityDetail(activityId.value)
    activity.value = res
    prizes.value = res.prizes || []
  } catch (e) {
    console.error('加载活动失败', e)
  }
}

async function checkUserDrawn() {
  try {
    const res = await checkDrawn(activityId.value)
    if (res?.has_drawn) {
      uni.showToast({
        title: '您已参与过本次活动',
        icon: 'none'
      })
    }
  } catch (e) {
    console.error('检查抽奖状态失败', e)
  }
}

async function handleSpin() {
  if (spinning.value) return

  spinning.value = true
  resultIndex.value = -1

  try {
    const res = await lotteryDraw(activityId.value)

    if (res?.is_won && res.prize) {
      const idx = prizes.value.findIndex(p => p.id === res.prize.id)
      resultIndex.value = idx >= 0 ? idx : -1
      isWon.value = true
      resultPrize.value = res.prize.name
    } else {
      // 未中奖，指向"谢谢参与"
      const thanksIndex = prizes.value.findIndex(p => p.name.includes('谢谢'))
      resultIndex.value = thanksIndex >= 0 ? thanksIndex : 0
      isWon.value = false
      resultPrize.value = '谢谢参与，下次再接再厉！'
    }

    // 等待轮盘动画完成
    setTimeout(() => {
      showResult.value = true
      spinning.value = false
    }, 3000)
  } catch (e: any) {
    spinning.value = false
    uni.showToast({
      title: e.message || '抽奖失败',
      icon: 'none'
    })
  }
}

function closeResult() {
  showResult.value = false
}
</script>

<style scoped>
.container {
  min-height: 100vh;
  background: linear-gradient(180deg, #FF6B35 0%, #FF8E53 50%, #FFF5F0 100%);
  padding: 40rpx;
}

.activity-header {
  text-align: center;
  margin-bottom: 40rpx;
}

.activity-title {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 16rpx;
}

.activity-desc {
  display: block;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
}

.wheel-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 40rpx;
}

.result-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.result-content {
  background: #fff;
  border-radius: 24rpx;
  padding: 60rpx 80rpx;
  text-align: center;
}

.result-title {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #FF6B35;
  margin-bottom: 20rpx;
}

.result-prize {
  display: block;
  font-size: 32rpx;
  color: #333;
  margin-bottom: 40rpx;
}

.btn-close {
  background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%);
  color: #fff;
  border-radius: 50rpx;
  padding: 20rpx 60rpx;
  font-size: 28rpx;
  border: none;
}
</style>
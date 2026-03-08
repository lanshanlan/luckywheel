<template>
  <view class="container">
    <!-- 背景装饰 -->
    <view class="bg-decoration">
      <view class="gift-box left"></view>
      <view class="gift-box right"></view>
      <view class="light-spot spot1"></view>
      <view class="light-spot spot2"></view>
      <view class="light-spot spot3"></view>
    </view>

    <!-- 大标题 -->
    <view class="main-title">
      <text class="title-text">幸运大抽奖</text>
      <view class="title-decoration"></view>
    </view>

    <!-- 活动信息 -->
    <view class="activity-info">
      <text class="activity-name">{{ activity.title }}</text>
      <text class="activity-desc">{{ activity.description }}</text>
    </view>

    <!-- 轮盘组件 -->
    <view class="wheel-container">
      <view class="wheel-outer-ring">
        <view class="wheel-light-dots">
          <view v-for="n in 12" :key="n" class="light-dot" :style="{ transform: `rotate(${(n-1) * 30}deg) translateY(-260rpx)` }"></view>
        </view>
        <LuckyWheel
          :prizes="prizes"
          :spinning="spinning"
          :result-index="resultIndex"
          @spin="handleSpin"
        />
      </view>
    </view>

    <!-- 开始抽奖按钮 -->
    <view class="start-btn-wrapper">
      <view
        class="start-btn"
        :class="{ disabled: spinning }"
        @click="handleStartClick"
      >
        <text class="btn-text">开始抽奖</text>
      </view>
    </view>

    <!-- 结果弹窗 -->
    <view v-if="showResult" class="result-modal" @click="closeResult">
      <view class="result-content" @click.stop>
        <view class="result-icon" :class="isWon ? 'win' : 'lose'">
          <text class="icon-text">{{ isWon ? '🎉' : '😊' }}</text>
        </view>
        <text class="result-title">{{ isWon ? '恭喜中奖！' : '很遗憾' }}</text>
        <text class="result-prize">{{ resultPrize }}</text>
        <view class="btn-close" @click="closeResult">
          <text>确定</text>
        </view>
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

function handleStartClick() {
  if (spinning.value) return
  handleSpin()
}

async function handleSpin() {
  if (spinning.value) return

  spinning.value = true
  resultIndex.value = -1
  isWon.value = false
  resultPrize.value = ''

  try {
    const res = await lotteryDraw(activityId.value)

    if (res?.prize) {
      // 找到奖品在轮盘中的索引位置
      const idx = prizes.value.findIndex(p => p.id === res.prize.id)
      resultIndex.value = idx >= 0 ? idx : 0

      // 根据后端返回的 is_won 判断是否真正中奖
      isWon.value = res.is_won
      resultPrize.value = res.prize.name
    } else {
      // 异常情况，没有返回奖品，定位到谢谢惠顾
      const thanksIndex = prizes.value.findIndex(p => p.name.includes('谢谢') || p.name.includes('惠顾'))
      resultIndex.value = thanksIndex >= 0 ? thanksIndex : 0
      isWon.value = false
      resultPrize.value = '谢谢惠顾'
    }

    // 动画持续4秒后显示结果
    setTimeout(() => {
      showResult.value = true
      spinning.value = false
    }, 4000)
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
  background: linear-gradient(180deg, #667eea 0%, #764ba2 50%, #8B5CF6 100%);
  padding: 40rpx;
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.gift-box {
  position: absolute;
  width: 120rpx;
  height: 120rpx;
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  border-radius: 20rpx;
  opacity: 0.6;
}

.gift-box::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 20rpx;
  background: #FF6B6B;
  transform: translateY(-50%);
}

.gift-box::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 20rpx;
  background: #FF6B6B;
  transform: translateX(-50%);
}

.gift-box.left {
  left: 30rpx;
  bottom: 300rpx;
  transform: rotate(-15deg);
}

.gift-box.right {
  right: 30rpx;
  bottom: 350rpx;
  transform: rotate(15deg);
}

.light-spot {
  position: absolute;
  width: 200rpx;
  height: 200rpx;
  background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
  border-radius: 50%;
}

.spot1 {
  top: 100rpx;
  left: -50rpx;
}

.spot2 {
  top: 200rpx;
  right: -80rpx;
}

.spot3 {
  bottom: 200rpx;
  left: 50%;
  transform: translateX(-50%);
}

/* 主标题 */
.main-title {
  text-align: center;
  margin-top: 40rpx;
  margin-bottom: 30rpx;
  position: relative;
  z-index: 1;
}

.title-text {
  display: block;
  font-size: 56rpx;
  font-weight: bold;
  color: #fff;
  text-shadow: 0 4rpx 8rpx rgba(0, 0, 0, 0.3);
  letter-spacing: 8rpx;
}

.title-decoration {
  width: 120rpx;
  height: 6rpx;
  background: linear-gradient(90deg, transparent, #FFD700, transparent);
  margin: 20rpx auto 0;
  border-radius: 3rpx;
}

/* 活动信息 */
.activity-info {
  text-align: center;
  margin-bottom: 40rpx;
  position: relative;
  z-index: 1;
}

.activity-name {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #FFD700;
  margin-bottom: 10rpx;
}

.activity-desc {
  display: block;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

/* 轮盘容器 */
.wheel-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 40rpx 0;
  position: relative;
  z-index: 1;
}

.wheel-outer-ring {
  position: relative;
  width: 620rpx;
  height: 620rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}

.wheel-light-dots {
  position: absolute;
  width: 100%;
  height: 100%;
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.light-dot {
  position: absolute;
  width: 16rpx;
  height: 16rpx;
  background: #FFD700;
  border-radius: 50%;
  left: 50%;
  top: 50%;
  margin-left: -8rpx;
  margin-top: -8rpx;
  box-shadow: 0 0 10rpx #FFD700;
}

.light-dot:nth-child(odd) {
  background: #fff;
  box-shadow: 0 0 10rpx #fff;
}

/* 开始按钮 */
.start-btn-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 60rpx;
  position: relative;
  z-index: 1;
}

.start-btn {
  background: linear-gradient(180deg, #FF8E53 0%, #FF6B35 100%);
  padding: 30rpx 100rpx;
  border-radius: 60rpx;
  box-shadow: 0 8rpx 20rpx rgba(255, 107, 53, 0.5), inset 0 -4rpx 10rpx rgba(0, 0, 0, 0.1);
  border: 4rpx solid #FFD700;
}

.start-btn.disabled {
  background: linear-gradient(180deg, #ccc 0%, #999 100%);
  box-shadow: none;
  border-color: #ddd;
}

.btn-text {
  color: #fff;
  font-size: 40rpx;
  font-weight: bold;
  letter-spacing: 4rpx;
}

/* 结果弹窗 */
.result-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.result-content {
  background: linear-gradient(180deg, #fff 0%, #f8f8f8 100%);
  border-radius: 30rpx;
  padding: 60rpx 80rpx;
  text-align: center;
  width: 80%;
  max-width: 600rpx;
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.3);
}

.result-icon {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto 30rpx;
}

.result-icon.win {
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
}

.result-icon.lose {
  background: linear-gradient(135deg, #E0E0E0 0%, #BDBDBD 100%);
}

.icon-text {
  font-size: 60rpx;
}

.result-title {
  display: block;
  font-size: 44rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

.result-prize {
  display: block;
  font-size: 32rpx;
  color: #666;
  margin-bottom: 50rpx;
  line-height: 1.5;
}

.btn-close {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 24rpx 80rpx;
  border-radius: 40rpx;
  font-size: 32rpx;
  display: inline-block;
}
</style>
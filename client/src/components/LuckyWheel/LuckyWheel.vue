<template>
  <view class="wheel-wrapper">
    <!-- 外圈装饰 -->
    <view class="outer-ring">
      <view class="light-dots">
        <view v-for="n in 12" :key="n" class="dot" :style="getDotStyle(n)"></view>
      </view>

      <!-- 轮盘主体 -->
      <view class="wheel-container">
        <view
          class="wheel-rotate"
          :style="wheelStyle"
        >
          <!-- 扇形背景 (使用 conic-gradient) -->
          <view class="wheel-sectors" :style="sectorsStyle"></view>

          <!-- 奖品文字 -->
          <view
            v-for="(prize, index) in prizes"
            :key="'text-'+prize.id"
            class="prize-text"
            :style="getTextStyle(index)"
          >
            <text class="prize-name">{{ formatPrizeName(prize.name) }}</text>
          </view>

          <!-- 分割线 -->
          <view
            v-for="(prize, index) in prizes"
            :key="'line-'+prize.id"
            class="sector-line"
            :style="getLineStyle(index)"
          ></view>
        </view>
      </view>
    </view>

    <!-- 指针 -->
    <view class="pointer">
      <view class="pointer-top"></view>
      <view class="pointer-circle"></view>
    </view>

    <!-- 中心按钮 -->
    <view
      class="center-btn"
      :class="{ disabled: spinning, pulse: !spinning }"
      @click="handleClick"
    >
      <text class="btn-text">{{ spinning ? '中' : '开始' }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Prize {
  id: number
  name: string
  probability: number
  sort_order: number
}

interface Props {
  prizes: Prize[]
  spinning: boolean
  resultIndex: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'spin'): void
}>()

const rotationAngle = ref(0)

const sectorAngle = computed(() => {
  return props.prizes.length > 0 ? 360 / props.prizes.length : 0
})

// 扇形颜色
const colors = [
  '#FF6B6B', // 红色
  '#4ECDC4', // 青色
  '#45B7D1', // 蓝色
  '#96CEB4', // 绿色
  '#FFEAA7', // 黄色
  '#DDA0DD', // 紫色
]

// 轮盘旋转样式
const wheelStyle = computed(() => ({
  transform: `rotate(${rotationAngle.value}deg)`,
  transition: props.spinning ? 'transform 4s cubic-bezier(0.2, 0.8, 0.2, 1)' : 'none'
}))

// 扇形背景样式 (conic-gradient)
const sectorsStyle = computed(() => {
  if (props.prizes.length === 0) return {}

  let gradient = 'conic-gradient('
  props.prizes.forEach((_, index) => {
    const startDeg = index * sectorAngle.value
    const endDeg = (index + 1) * sectorAngle.value
    const color = colors[index % colors.length]
    gradient += `${color} ${startDeg}deg ${endDeg}deg`
    if (index < props.prizes.length - 1) {
      gradient += ', '
    }
  })
  gradient += ')'

  return {
    background: gradient
  }
})

// 格式化奖品名称
function formatPrizeName(name: string) {
  if (name.length > 6) {
    return name.substring(0, 6) + '...'
  }
  return name
}

// 获取文字位置样式
function getTextStyle(index: number) {
  const angle = sectorAngle.value
  // 文字放在扇形的中间位置
  const textAngle = index * angle + angle / 2 - 90
  const textRadius = 32 // 百分比

  const rad = textAngle * Math.PI / 180
  const x = 50 + textRadius * Math.cos(rad)
  const y = 50 + textRadius * Math.sin(rad)

  return {
    left: `${x}%`,
    top: `${y}%`,
    transform: `translate(-50%, -50%) rotate(${textAngle + 90}deg)`,
  }
}

// 获取分割线样式
function getLineStyle(index: number) {
  const angle = index * sectorAngle.value
  return {
    transform: `rotate(${angle}deg)`,
  }
}

// 获取装饰灯点位置
function getDotStyle(n: number) {
  const angle = (n - 1) * 30
  return {
    transform: `rotate(${angle}deg) translateY(-275rpx)`,
  }
}

function handleClick() {
  if (!props.spinning) {
    emit('spin')
  }
}

// 监听结果索引变化，触发旋转动画
watch(() => props.resultIndex, (newIndex, oldIndex) => {
  // 当结果索引从无效变为有效时，开始旋转
  if (newIndex >= 0 && oldIndex < 0 && props.spinning) {
    const baseRotation = 360 * 8 // 转8圈
    // 计算奖品位置对应的偏移角度
    // 指针在顶部(12点方向)，需要计算让目标扇形旋转到顶部的角度
    const prizeOffset = (props.prizes.length - newIndex) * sectorAngle.value - sectorAngle.value / 2
    // 添加随机偏移，让结果更自然
    const randomOffset = (Math.random() - 0.5) * sectorAngle.value * 0.6
    rotationAngle.value += baseRotation + prizeOffset + randomOffset
  }
})
</script>

<style scoped>
.wheel-wrapper {
  position: relative;
  width: 560rpx;
  height: 560rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 外圈装饰 */
.outer-ring {
  width: 540rpx;
  height: 540rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FF8C00 100%);
  padding: 16rpx;
  box-shadow: 0 10rpx 40rpx rgba(0, 0, 0, 0.3);
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 灯点 */
.light-dots {
  position: absolute;
  width: 100%;
  height: 100%;
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.dot {
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

.dot:nth-child(odd) {
  background: #fff;
  box-shadow: 0 0 10rpx #fff;
}

/* 轮盘容器 */
.wheel-container {
  width: 500rpx;
  height: 500rpx;
  border-radius: 50%;
  background: #fff;
  overflow: hidden;
  position: relative;
}

.wheel-rotate {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  position: relative;
}

/* 扇形背景 */
.wheel-sectors {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

/* 分割线 */
.sector-line {
  position: absolute;
  width: 2rpx;
  height: 50%;
  background: #fff;
  left: 50%;
  top: 0;
  margin-left: -1rpx;
  transform-origin: 50% 100%;
}

/* 奖品文字 */
.prize-text {
  position: absolute;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.prize-name {
  font-size: 24rpx;
  font-weight: bold;
  color: #fff;
  text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.4);
  text-align: center;
  line-height: 1.3;
  white-space: nowrap;
}

/* 指针 */
.pointer {
  position: absolute;
  top: -20rpx;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pointer-top {
  width: 0;
  height: 0;
  border-left: 20rpx solid transparent;
  border-right: 20rpx solid transparent;
  border-top: 50rpx solid #FF6B6B;
  filter: drop-shadow(0 4rpx 8rpx rgba(0, 0, 0, 0.3));
}

.pointer-circle {
  width: 24rpx;
  height: 24rpx;
  background: #FF6B6B;
  border-radius: 50%;
  margin-top: -12rpx;
  border: 4rpx solid #fff;
  box-shadow: 0 4rpx 8rpx rgba(0, 0, 0, 0.3);
}

/* 中心按钮 */
.center-btn {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 140rpx;
  height: 140rpx;
  border-radius: 50%;
  background: linear-gradient(180deg, #FFD700 0%, #FFA500 50%, #FF8C00 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.3), inset 0 -4rpx 10rpx rgba(0, 0, 0, 0.1);
  z-index: 30;
  border: 6rpx solid #FFD700;
}

.center-btn.disabled {
  background: linear-gradient(180deg, #ccc 0%, #999 100%);
  border-color: #ddd;
}

.center-btn.pulse {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.3), 0 0 0 0 rgba(255, 215, 0, 0.4);
  }
  50% {
    box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.4), 0 0 0 20rpx rgba(255, 215, 0, 0);
  }
}

.btn-text {
  color: #fff;
  font-size: 36rpx;
  font-weight: bold;
  text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.2);
}
</style>
<template>
  <view class="wheel-wrapper">
    <!-- 轮盘背景 -->
    <view class="wheel-bg">
      <!-- 轮盘扇形 -->
      <view
        v-for="(prize, index) in prizes"
        :key="prize.id"
        class="wheel-sector"
        :style="getSectorStyle(index)"
      >
        <text class="prize-name">{{ prize.name }}</text>
      </view>
    </view>

    <!-- 指针 -->
    <view class="wheel-pointer">
      <view class="pointer-triangle"></view>
    </view>

    <!-- 中心按钮 -->
    <view
      class="wheel-center"
      :class="{ disabled: spinning }"
      @click="handleClick"
    >
      <text class="center-text">{{ spinning ? '抽奖中' : '抽奖' }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

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

const sectorAngle = computed(() => {
  return props.prizes.length > 0 ? 360 / props.prizes.length : 0
})

const colors = [
  '#FF6B35', '#FF8E53', '#FFB347', '#FFD700',
  '#4CAF50', '#8BC34A', '#03A9F4', '#00BCD4'
]

function getSectorStyle(index: number) {
  const angle = sectorAngle.value
  const rotation = index * angle - 90
  const color = colors[index % colors.length]

  return {
    transform: `rotate(${rotation}deg) skewY(${-(90 - angle)}deg)`,
    backgroundColor: color
  }
}

function handleClick() {
  if (!props.spinning) {
    emit('spin')
  }
}
</script>

<style scoped>
.wheel-wrapper {
  position: relative;
  width: 600rpx;
  height: 600rpx;
}

.wheel-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 0 20rpx rgba(0, 0, 0, 0.3);
}

.wheel-sector {
  position: absolute;
  width: 50%;
  height: 50%;
  left: 50%;
  top: 0;
  transform-origin: 0% 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.prize-name {
  transform: skewY(45deg) rotate(22deg);
  font-size: 20rpx;
  color: #fff;
  text-align: center;
  width: 100rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.wheel-pointer {
  position: absolute;
  top: -20rpx;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.pointer-triangle {
  width: 0;
  height: 0;
  border-left: 20rpx solid transparent;
  border-right: 20rpx solid transparent;
  border-top: 40rpx solid #FF6B35;
}

.wheel-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.3);
  z-index: 20;
}

.wheel-center.disabled {
  background: #ccc;
}

.center-text {
  color: #fff;
  font-size: 28rpx;
  font-weight: bold;
}
</style>
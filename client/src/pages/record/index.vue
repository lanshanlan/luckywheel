<template>
  <view class="container">
    <view class="record-list">
      <view
        v-for="item in records"
        :key="item.id"
        class="record-card"
      >
        <view class="record-info">
          <text class="record-activity">{{ item.activity_title }}</text>
          <text class="record-time">{{ formatTime(item.created_at) }}</text>
        </view>
        <view class="record-result">
          <text v-if="item.is_won" class="won">{{ item.prize_name }}</text>
          <text v-else class="not-won">未中奖</text>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view v-if="records.length === 0" class="empty-state">
      <text>暂无抽奖记录</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMyRecords } from '@/api/lottery'

interface Record {
  id: number
  activity_id: number
  activity_title: string
  prize_id: number | null
  prize_name: string | null
  is_won: boolean
  created_at: string
}

const records = ref<Record[]>([])

onMounted(() => {
  loadRecords()
})

async function loadRecords() {
  try {
    const res = await getMyRecords()
    records.value = res || []
  } catch (e) {
    console.error('加载记录失败', e)
  }
}

function formatTime(time: string) {
  const date = new Date(time)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.container {
  padding: 20rpx;
  min-height: 100vh;
}

.record-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.record-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.record-info {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.record-activity {
  font-size: 30rpx;
  color: #333;
  font-weight: 500;
}

.record-time {
  font-size: 24rpx;
  color: #999;
}

.record-result {
  text-align: right;
}

.won {
  font-size: 28rpx;
  color: #FF6B35;
  font-weight: bold;
}

.not-won {
  font-size: 28rpx;
  color: #999;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400rpx;
  color: #999;
}
</style>
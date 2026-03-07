<template>
  <view class="container">
    <!-- 活动列表 -->
    <view class="activity-list">
      <view
        v-for="item in activityList"
        :key="item.id"
        class="activity-card"
        @click="goToLottery(item.id)"
      >
        <view class="activity-info">
          <text class="activity-title">{{ item.title }}</text>
          <text class="activity-desc">{{ item.description }}</text>
          <view class="activity-status">
            <text :class="['status-tag', getStatusClass(item.status)]">
              {{ getStatusText(item.status) }}
            </text>
          </view>
        </view>
        <view class="activity-arrow">
          <text class="arrow">→</text>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view v-if="activityList.length === 0" class="empty-state">
      <text>暂无活动</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getActivityList } from '@/api/activity'

interface Activity {
  id: number
  title: string
  description: string
  status: number
}

const activityList = ref<Activity[]>([])

onMounted(() => {
  loadActivities()
})

async function loadActivities() {
  try {
    const res = await getActivityList()
    activityList.value = res.data || []
  } catch (e) {
    console.error('加载活动失败', e)
  }
}

function getStatusClass(status: number) {
  const map: Record<number, string> = {
    0: 'status-pending',
    1: 'status-active',
    2: 'status-ended'
  }
  return map[status] || 'status-pending'
}

function getStatusText(status: number) {
  const map: Record<number, string> = {
    0: '未开始',
    1: '进行中',
    2: '已结束'
  }
  return map[status] || '未知'
}

function goToLottery(activityId: number) {
  uni.navigateTo({
    url: `/pages/lottery/index?id=${activityId}`
  })
}
</script>

<style scoped>
.container {
  padding: 20rpx;
  min-height: 100vh;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.activity-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.activity-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.activity-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.activity-desc {
  font-size: 26rpx;
  color: #999;
}

.activity-status {
  margin-top: 10rpx;
}

.status-tag {
  display: inline-block;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
}

.status-pending {
  background: #FFF3E0;
  color: #FF9800;
}

.status-active {
  background: #E8F5E9;
  color: #4CAF50;
}

.status-ended {
  background: #FAFAFA;
  color: #999;
}

.activity-arrow {
  padding: 20rpx;
}

.arrow {
  font-size: 36rpx;
  color: #ccc;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400rpx;
  color: #999;
}
</style>
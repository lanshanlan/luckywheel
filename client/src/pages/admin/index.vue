<template>
  <view class="container">
    <!-- 标签切换 -->
    <view class="tabs">
      <view
        :class="['tab', activeTab === 'activities' ? 'active' : '']"
        @click="activeTab = 'activities'"
      >
        活动管理
      </view>
      <view
        :class="['tab', activeTab === 'records' ? 'active' : '']"
        @click="activeTab = 'records'"
      >
        抽奖记录
      </view>
    </view>

    <!-- 活动管理 -->
    <view v-if="activeTab === 'activities'" class="tab-content">
      <!-- 创建活动按钮 -->
      <view class="create-btn" @click="showCreateActivity = true">
        <text>+ 创建活动</text>
      </view>

      <!-- 活动列表 -->
      <view class="activity-list">
        <view v-for="item in activities" :key="item.id" class="activity-item">
          <view class="activity-header">
            <text class="activity-title">{{ item.title }}</text>
            <text :class="['status', getStatusClass(item.status)]">
              {{ getStatusText(item.status) }}
            </text>
          </view>
          <text class="activity-desc">{{ item.description || '暂无描述' }}</text>
          <view class="activity-actions">
            <text class="action-btn" @click="editActivity(item)">编辑</text>
            <text class="action-btn danger" @click="handleDeleteActivity(item.id)">删除</text>
            <text class="action-btn primary" @click="showPrizeManager(item)">奖品管理</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 抽奖记录 -->
    <view v-if="activeTab === 'records'" class="tab-content">
      <view class="record-list">
        <view v-for="item in records" :key="item.id" class="record-item">
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
      <view v-if="records.length === 0" class="empty">
        <text>暂无抽奖记录</text>
      </view>
    </view>

    <!-- 创建/编辑活动弹窗 -->
    <view v-if="showCreateActivity" class="modal" @click="showCreateActivity = false">
      <view class="modal-content" @click.stop>
        <text class="modal-title">{{ editingActivity ? '编辑活动' : '创建活动' }}</text>
        <view class="form-item">
          <text class="label">活动标题</text>
          <input v-model="activityForm.title" class="input" placeholder="请输入活动标题" />
        </view>
        <view class="form-item">
          <text class="label">活动描述</text>
          <textarea v-model="activityForm.description" class="textarea" placeholder="请输入活动描述" />
        </view>
        <view class="form-item">
          <text class="label">活动状态</text>
          <picker :value="activityForm.status" :range="statusOptions" range-key="label" @change="onStatusChange">
            <view class="picker">{{ statusOptions[activityForm.status].label }}</view>
          </picker>
        </view>
        <view class="modal-actions">
          <button class="btn-cancel" @click="closeActivityModal">取消</button>
          <button class="btn-confirm" @click="handleSaveActivity">保存</button>
        </view>
      </view>
    </view>

    <!-- 奖品管理弹窗 -->
    <view v-if="showPrizeModal" class="modal" @click="showPrizeModal = false">
      <view class="modal-content prize-modal" @click.stop>
        <text class="modal-title">{{ currentActivity?.title }} - 奖品管理</text>

        <!-- 添加奖品 -->
        <view class="prize-form">
          <input v-model="prizeForm.name" class="input" placeholder="奖品名称" />
          <input v-model.number="prizeForm.probability" class="input" type="digit" placeholder="概率(0-1)" />
          <input v-model.number="prizeForm.stock" class="input" type="number" placeholder="库存" />
          <button class="btn-add" @click="handleAddPrize">添加奖品</button>
        </view>

        <!-- 奖品列表 -->
        <view class="prize-list">
          <view v-for="prize in prizes" :key="prize.id" class="prize-item">
            <text class="prize-name">{{ prize.name }}</text>
            <text class="prize-info">概率: {{ prize.probability }} | 库存: {{ prize.stock }}</text>
            <text class="delete-btn" @click="handleDeletePrize(prize.id)">删除</text>
          </view>
        </view>

        <button class="btn-close" @click="showPrizeModal = false">关闭</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  checkAdmin,
  createActivity,
  updateActivity,
  deleteActivity,
  createPrize,
  deletePrize,
  getAllRecords
} from '@/api/admin'
import { getActivityList, getActivityDetail } from '@/api/activity'

interface Activity {
  id: number
  title: string
  description: string
  status: number
  prizes?: Prize[]
}

interface Prize {
  id: number
  name: string
  probability: number
  stock: number
  sort_order: number
}

interface Record {
  id: number
  activity_id: number
  activity_title: string
  prize_id: number | null
  prize_name: string | null
  is_won: boolean
  created_at: string
}

const activeTab = ref<'activities' | 'records'>('activities')
const activities = ref<Activity[]>([])
const records = ref<Record[]>([])
const prizes = ref<Prize[]>([])

const showCreateActivity = ref(false)
const showPrizeModal = ref(false)
const editingActivity = ref<Activity | null>(null)
const currentActivity = ref<Activity | null>(null)

const activityForm = ref({
  title: '',
  description: '',
  status: 1
})

const prizeForm = ref({
  name: '',
  probability: 0.1,
  stock: 1,
  sort_order: 0
})

const statusOptions = [
  { label: '未开始', value: 0 },
  { label: '进行中', value: 1 },
  { label: '已结束', value: 2 }
]

onMounted(() => {
  checkAdminPermission()
  loadData()
})

async function checkAdminPermission() {
  try {
    await checkAdmin()
  } catch (e) {
    uni.showToast({ title: '无权限访问', icon: 'none' })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  }
}

async function loadData() {
  await Promise.all([loadActivities(), loadRecords()])
}

async function loadActivities() {
  try {
    const res = await getActivityList()
    activities.value = res || []
  } catch (e) {
    console.error('加载活动失败', e)
  }
}

async function loadRecords() {
  try {
    const res = await getAllRecords()
    records.value = res || []
  } catch (e) {
    console.error('加载记录失败', e)
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

function formatTime(time: string) {
  const date = new Date(time)
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

function onStatusChange(e: any) {
  activityForm.value.status = e.detail.value
}

function editActivity(activity: Activity) {
  editingActivity.value = activity
  activityForm.value = {
    title: activity.title,
    description: activity.description || '',
    status: activity.status
  }
  showCreateActivity.value = true
}

function closeActivityModal() {
  showCreateActivity.value = false
  editingActivity.value = null
  activityForm.value = { title: '', description: '', status: 1 }
}

async function handleSaveActivity() {
  if (!activityForm.value.title.trim()) {
    uni.showToast({ title: '请输入活动标题', icon: 'none' })
    return
  }

  try {
    if (editingActivity.value) {
      await updateActivity(editingActivity.value.id, activityForm.value)
      uni.showToast({ title: '修改成功', icon: 'success' })
    } else {
      await createActivity(activityForm.value)
      uni.showToast({ title: '创建成功', icon: 'success' })
    }
    closeActivityModal()
    loadActivities()
  } catch (e: any) {
    uni.showToast({ title: e.message || '操作失败', icon: 'none' })
  }
}

async function handleDeleteActivity(id: number) {
  const res = await new Promise<boolean>((resolve) => {
    uni.showModal({
      title: '确认删除',
      content: '删除后无法恢复，确定要删除吗？',
      success: (result) => resolve(result.confirm)
    })
  })

  if (!res) return

  try {
    await deleteActivity(id)
    uni.showToast({ title: '删除成功', icon: 'success' })
    loadActivities()
  } catch (e: any) {
    uni.showToast({ title: e.message || '删除失败', icon: 'none' })
  }
}

async function showPrizeManager(activity: Activity) {
  currentActivity.value = activity
  showPrizeModal.value = true

  try {
    const res = await getActivityDetail(activity.id)
    prizes.value = res.prizes || []
  } catch (e) {
    console.error('加载奖品失败', e)
  }
}

async function handleAddPrize() {
  if (!prizeForm.value.name.trim()) {
    uni.showToast({ title: '请输入奖品名称', icon: 'none' })
    return
  }
  if (!currentActivity.value) return

  try {
    await createPrize({
      activity_id: currentActivity.value.id,
      name: prizeForm.value.name,
      probability: prizeForm.value.probability,
      stock: prizeForm.value.stock,
      sort_order: prizeForm.value.sort_order
    })
    uni.showToast({ title: '添加成功', icon: 'success' })
    prizeForm.value = { name: '', probability: 0.1, stock: 1, sort_order: 0 }

    // 刷新奖品列表
    const res = await getActivityDetail(currentActivity.value.id)
    prizes.value = res.prizes || []
  } catch (e: any) {
    uni.showToast({ title: e.message || '添加失败', icon: 'none' })
  }
}

async function handleDeletePrize(id: number) {
  try {
    await deletePrize(id)
    uni.showToast({ title: '删除成功', icon: 'success' })
    if (currentActivity.value) {
      const res = await getActivityDetail(currentActivity.value.id)
      prizes.value = res.prizes || []
    }
  } catch (e: any) {
    uni.showToast({ title: e.message || '删除失败', icon: 'none' })
  }
}
</script>

<style scoped>
.container {
  min-height: 100vh;
  background: #f5f5f5;
}

.tabs {
  display: flex;
  background: #fff;
  border-bottom: 1rpx solid #eee;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 30rpx 0;
  font-size: 30rpx;
  color: #666;
}

.tab.active {
  color: #FF6B35;
  border-bottom: 4rpx solid #FF6B35;
}

.tab-content {
  padding: 20rpx;
}

.create-btn {
  background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%);
  color: #fff;
  text-align: center;
  padding: 24rpx;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
}

.activity-list, .record-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.activity-item, .record-item {
  background: #fff;
  border-radius: 12rpx;
  padding: 24rpx;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10rpx;
}

.activity-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.status {
  font-size: 24rpx;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
}

.status-pending { background: #FFF3E0; color: #FF9800; }
.status-active { background: #E8F5E9; color: #4CAF50; }
.status-ended { background: #FAFAFA; color: #999; }

.activity-desc {
  font-size: 26rpx;
  color: #999;
  margin-bottom: 16rpx;
}

.activity-actions {
  display: flex;
  gap: 20rpx;
}

.action-btn {
  font-size: 26rpx;
  color: #666;
  padding: 8rpx 20rpx;
  border: 1rpx solid #ddd;
  border-radius: 8rpx;
}

.action-btn.primary {
  color: #FF6B35;
  border-color: #FF6B35;
}

.action-btn.danger {
  color: #f56c6c;
  border-color: #f56c6c;
}

.record-info {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.record-activity {
  font-size: 28rpx;
  color: #333;
}

.record-time {
  font-size: 24rpx;
  color: #999;
}

.record-result {
  text-align: right;
}

.won {
  color: #FF6B35;
  font-weight: bold;
}

.not-won {
  color: #999;
}

.empty {
  text-align: center;
  padding: 100rpx 0;
  color: #999;
}

/* 弹窗样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 20rpx;
  padding: 40rpx;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-title {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 30rpx;
  text-align: center;
}

.form-item {
  margin-bottom: 24rpx;
}

.label {
  display: block;
  font-size: 28rpx;
  color: #666;
  margin-bottom: 10rpx;
}

.input, .textarea {
  width: 100%;
  padding: 20rpx;
  border: 1rpx solid #ddd;
  border-radius: 10rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.textarea {
  height: 150rpx;
}

.picker {
  padding: 20rpx;
  border: 1rpx solid #ddd;
  border-radius: 10rpx;
  font-size: 28rpx;
}

.modal-actions {
  display: flex;
  gap: 20rpx;
  margin-top: 40rpx;
}

.btn-cancel, .btn-confirm {
  flex: 1;
  padding: 24rpx;
  border-radius: 10rpx;
  font-size: 30rpx;
  border: none;
}

.btn-cancel {
  background: #f5f5f5;
  color: #666;
}

.btn-confirm {
  background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%);
  color: #fff;
}

/* 奖品管理 */
.prize-modal {
  max-height: 85vh;
}

.prize-form {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 30rpx;
}

.prize-form .input {
  flex: 1;
  min-width: 150rpx;
}

.btn-add {
  background: #FF6B35;
  color: #fff;
  font-size: 26rpx;
  padding: 16rpx 24rpx;
  border-radius: 8rpx;
  border: none;
}

.prize-list {
  margin-bottom: 30rpx;
}

.prize-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  background: #f9f9f9;
  border-radius: 10rpx;
  margin-bottom: 16rpx;
}

.prize-name {
  font-size: 28rpx;
  color: #333;
}

.prize-info {
  font-size: 24rpx;
  color: #999;
}

.delete-btn {
  font-size: 26rpx;
  color: #f56c6c;
}

.btn-close {
  width: 100%;
  padding: 24rpx;
  background: #f5f5f5;
  border-radius: 10rpx;
  font-size: 30rpx;
  border: none;
  color: #666;
}
</style>
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
      <!-- 活动筛选器 -->
      <view class="filter-section">
        <picker :value="selectedActivityIndex" :range="activityFilterOptions" range-key="title" @change="onActivityFilterChange">
          <view class="filter-picker">
            <text class="filter-label">选择活动:</text>
            <text class="filter-value">{{ activityFilterOptions[selectedActivityIndex]?.title || '全部活动' }}</text>
            <text class="picker-arrow">▼</text>
          </view>
        </picker>
      </view>

      <!-- 统计信息卡片 -->
      <view v-if="statistics" class="statistics-section">
        <view class="stat-card">
          <text class="stat-value">{{ statistics.total_draws }}</text>
          <text class="stat-label">总抽奖</text>
        </view>
        <view class="stat-card">
          <text class="stat-value">{{ statistics.win_count }}</text>
          <text class="stat-label">中奖数</text>
        </view>
        <view class="stat-card">
          <text class="stat-value">{{ (statistics.win_rate * 100).toFixed(2) }}%</text>
          <text class="stat-label">中奖率</text>
        </view>
      </view>

      <!-- 记录列表 -->
      <view class="record-list" @scrolltolower="loadMoreRecords">
        <view v-for="item in records" :key="item.id" class="record-item">
          <view class="record-header">
            <text class="record-user">{{ item.user_nickname }}</text>
            <text class="record-separator">-</text>
            <text class="record-activity">{{ item.activity_title }}</text>
          </view>
          <text class="record-time">{{ formatTime(item.created_at) }}</text>
          <text v-if="item.is_won" class="record-prize">奖品: {{ item.prize_name }}</text>
          <text v-else class="record-no-prize">未中奖</text>
        </view>
        <view v-if="loading" class="loading-tip">加载中...</view>
        <view v-if="!hasMore && records.length > 0" class="loading-tip">没有更多了</view>
      </view>
      <view v-if="records.length === 0 && !loading" class="empty">
        <text>暂无抽奖记录</text>
      </view>
    </view>

    <!-- 创建/编辑活动弹窗 -->
    <view v-if="showCreateActivity" class="modal" @click="showCreateActivity = false">
      <view class="modal-content activity-modal" @click.stop>
        <!-- 头部 -->
        <view class="activity-modal-header">
          <text class="activity-modal-title">{{ editingActivity ? '编辑活动' : '创建活动' }}</text>
        </view>

        <!-- 表单区域 -->
        <view class="activity-form-section">
          <view class="activity-form-row">
            <view class="activity-form-group">
              <text class="activity-form-label">活动标题 <text class="required">*</text></text>
              <input v-model="activityForm.title" class="activity-form-input" placeholder="请输入活动标题" />
            </view>
          </view>
          <view class="activity-form-row">
            <view class="activity-form-group">
              <text class="activity-form-label">活动描述</text>
              <textarea v-model="activityForm.description" class="activity-form-textarea" placeholder="请输入活动描述（选填）" />
            </view>
          </view>
          <view class="activity-form-row">
            <view class="activity-form-group">
              <text class="activity-form-label">活动状态</text>
              <picker :value="activityForm.status" :range="statusOptions" range-key="label" @change="onStatusChange">
                <view class="activity-picker">
                  <text>{{ statusOptions[activityForm.status].label }}</text>
                  <text class="picker-arrow">▼</text>
                </view>
              </picker>
            </view>
          </view>
          <view class="activity-form-row">
            <view class="activity-form-group">
              <text class="activity-form-label">活动开始时间</text>
              <picker mode="date" :value="activityForm.start_time" @change="onStartDateChange">
                <view class="activity-picker">
                  <text>{{ activityForm.start_time || '请选择日期' }}</text>
                  <text class="picker-arrow">▼</text>
                </view>
              </picker>
            </view>
          </view>
          <view class="activity-form-row">
            <view class="activity-form-group">
              <text class="activity-form-label">抽奖间隔（天）</text>
              <input v-model.number="activityForm.draw_interval_days" class="activity-form-input" type="number" placeholder="默认1天" />
            </view>
          </view>
        </view>

        <!-- 底部按钮 -->
        <view class="activity-modal-footer">
          <button class="btn-activity-cancel" @click="closeActivityModal">取消</button>
          <button class="btn-activity-confirm" @click="handleSaveActivity">保存</button>
        </view>
      </view>
    </view>

    <!-- 奖品管理弹窗 -->
    <view v-if="showPrizeModal" class="modal" @click="showPrizeModal = false">
      <view class="modal-content prize-modal" @click.stop>
        <!-- 头部 -->
        <view class="prize-modal-header">
          <text class="prize-modal-title">{{ currentActivity?.title }}</text>
          <text class="prize-modal-subtitle">奖品管理</text>
        </view>

        <!-- 可滚动内容区域：添加奖品表单 + 奖品列表 -->
        <scroll-view class="prize-scroll-content" scroll-y>
          <!-- 添加奖品表单 -->
          <view class="prize-form-section">
            <view class="section-title">添加奖品</view>
            <view class="prize-form-row">
              <view class="form-group name-group">
                <text class="form-label">奖品名称</text>
                <input v-model="prizeForm.name" class="form-input" placeholder="请输入奖品名称" />
              </view>
            </view>
            <view class="prize-form-row two-col">
              <view class="form-group">
                <text class="form-label">中奖概率 <text class="label-hint">(0-1之间)</text></text>
                <input v-model="prizeForm.probability" class="form-input" type="text" placeholder="如 0.1" />
              </view>
              <view class="form-group">
                <text class="form-label">库存数量</text>
                <input v-model.number="prizeForm.stock" class="form-input" type="number" placeholder="库存" />
              </view>
            </view>
            <view class="prize-form-row">
              <view class="form-group full-width">
                <text class="form-label">奖品类型</text>
                <picker :value="prizeForm.prize_type" :range="prizeTypeOptions" range-key="label" @change="onPrizeTypeChange">
                  <view class="form-picker">
                    <text>{{ prizeTypeOptions[prizeForm.prize_type].label }}</text>
                    <text class="picker-arrow">▼</text>
                  </view>
                </picker>
              </view>
            </view>
            <view v-if="prizeForm.prize_type === 1" class="prize-form-row two-col">
              <view class="form-group">
                <text class="form-label">心愿次数 <text class="label-hint">(抽N次必得)</text></text>
                <input v-model.number="prizeForm.guarantee_count" class="form-input" type="number" placeholder="如 10" />
              </view>
            </view>
            <button class="btn-add-prize" @click="handleAddPrize">+ 添加奖品</button>
          </view>

          <!-- 奖品列表 -->
          <view class="prize-list-section">
            <view class="section-header">
              <text class="section-title">奖品列表</text>
              <text class="prize-count">{{ sortedPrizes.length }} 个奖品</text>
            </view>
            <view v-if="sortedPrizes.length === 0" class="empty-list">
              <text class="empty-icon">🎁</text>
              <text class="empty-text">暂无奖品，快去添加吧</text>
            </view>
            <view v-else class="prize-cards">
              <view v-for="(prize, index) in sortedPrizes" :key="prize.id" class="prize-card">
                <view class="prize-card-left">
                  <view class="prize-index" :style="{ backgroundColor: getPrizeColor(index) }">{{ index + 1 }}</view>
                  <view class="prize-info-wrap">
                    <view class="prize-name-row">
                      <text class="prize-card-name">{{ prize.name }}</text>
                      <text v-if="prize.prize_type === 1" class="mystery-badge">神秘大奖</text>
                    </view>
                    <view class="prize-card-meta">
                      <text class="meta-item">
                        <text class="meta-value">{{ (prize.probability * 100).toFixed(2) }}%</text>
                        <text class="meta-label">概率</text>
                      </text>
                      <text class="meta-divider">|</text>
                      <text class="meta-item">
                        <text class="meta-value">{{ prize.stock }}</text>
                        <text class="meta-label">库存</text>
                      </text>
                      <template v-if="prize.prize_type === 1 && prize.guarantee_count > 0">
                        <text class="meta-divider">|</text>
                        <text class="meta-item">
                          <text class="meta-value guarantee">{{ prize.guarantee_count }}次</text>
                          <text class="meta-label">心愿</text>
                        </text>
                      </template>
                    </view>
                  </view>
                </view>
                <view class="delete-btn-wrap" @click="handleDeletePrize(prize.id)">
                  <text class="delete-icon">×</text>
                </view>
              </view>
            </view>
          </view>
        </scroll-view>

        <view class="prize-modal-footer">
          <button class="btn-close-modal" @click="showPrizeModal = false">完成</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import {
  checkAdmin,
  createActivity,
  updateActivity,
  deleteActivity,
  createPrize,
  deletePrize,
  getAllRecords,
  getRecordsStatistics
} from '@/api/admin'
import { getActivityList, getActivityDetail } from '@/api/activity'

interface Activity {
  id: number
  title: string
  description: string
  status: number
  start_time?: string
  end_time?: string
  draw_interval_days?: number
  prizes?: Prize[]
}

interface Prize {
  id: number
  name: string
  probability: number
  stock: number
  sort_order: number
  prize_type: number    // 0-普通奖品，1-神秘大奖
  guarantee_count: number // 心愿次数
}

interface LotteryRecordItem {
  id: number
  activity_id: number
  activity_title: string
  user_id?: number
  user_nickname: string
  prize_id: number | null
  prize_name: string | null
  is_won: boolean
  created_at: string
}

interface ActivityStatistics {
  total_draws: number
  win_count: number
  win_rate: number
  activity_id?: number
  activity_title?: string
}

const activeTab = ref<'activities' | 'records'>('activities')
const activities = ref<Activity[]>([])
const records = ref<LotteryRecordItem[]>([])
const prizes = ref<Prize[]>([])

// 抽奖记录相关状态
const selectedActivityId = ref<number | null>(null)  // 选中的活动ID，null表示全部
const statistics = ref<ActivityStatistics | null>(null)  // 统计数据
const page = ref(0)  // 当前页码
const pageSize = ref(20)  // 每页数量
const loading = ref(false)  // 加载中
const hasMore = ref(true)  // 是否有更多数据

const showCreateActivity = ref(false)
const showPrizeModal = ref(false)
const editingActivity = ref<Activity | null>(null)
const currentActivity = ref<Activity | null>(null)

// 排序后的奖品列表：神秘大奖排在最前面
const sortedPrizes = computed(() => {
  return [...prizes.value].sort((a, b) => {
    // 神秘大奖 (prize_type === 1) 排在前面
    if (a.prize_type === 1 && b.prize_type !== 1) return -1
    if (a.prize_type !== 1 && b.prize_type === 1) return 1
    // 相同类型保持原有顺序（稳定排序）
    return 0
  })
})

const activityForm = ref({
  title: '',
  description: '',
  status: 1,
  start_time: '',
  draw_interval_days: 1
})

const prizeForm = ref({
  name: '',
  probability: '',
  stock: 1,
  sort_order: 0,
  prize_type: 0,       // 0-普通奖品，1-神秘大奖
  guarantee_count: 0   // 心愿次数
})

const prizeTypeOptions = [
  { label: '普通奖品', value: 0 },
  { label: '神秘大奖', value: 1 }
]

const statusOptions = [
  { label: '未开始', value: 0 },
  { label: '进行中', value: 1 },
  { label: '已结束', value: 2 }
]

// 活动筛选器选项
const activityFilterOptions = computed(() => {
  return [{ id: null, title: '全部活动' }, ...activities.value.map(a => ({ id: a.id, title: a.title }))]
})

const selectedActivityIndex = computed(() => {
  if (selectedActivityId.value === null) return 0
  const idx = activities.value.findIndex(a => a.id === selectedActivityId.value)
  return idx >= 0 ? idx + 1 : 0
})

onShow(() => {
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
  await Promise.all([loadActivities(), loadRecords(), loadStatistics()])
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
    const res = await getAllRecords({
      activityId: selectedActivityId.value || undefined,
      limit: pageSize.value,
      offset: page.value * pageSize.value
    })
    if (page.value === 0) {
      records.value = res || []
    } else {
      records.value = [...records.value, ...(res || [])]
    }
    hasMore.value = (res || []).length >= pageSize.value
  } catch (e) {
    console.error('加载记录失败', e)
  }
}

async function loadStatistics() {
  try {
    const res = await getRecordsStatistics(selectedActivityId.value || undefined)
    statistics.value = res
  } catch (e) {
    console.error('加载统计数据失败', e)
  }
}

async function loadMoreRecords() {
  if (loading.value || !hasMore.value) return
  loading.value = true
  page.value++
  await loadRecords()
  loading.value = false
}

async function onActivityFilterChange(e: any) {
  const index = e.detail.value
  if (index === 0) {
    selectedActivityId.value = null
  } else {
    selectedActivityId.value = activities.value[index - 1].id
  }
  // 重置分页并重新加载
  page.value = 0
  records.value = []
  hasMore.value = true
  await Promise.all([loadRecords(), loadStatistics()])
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

// 奖品颜色配置
const prizeColors = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
  '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
  '#FFB6C1', '#87CEEB', '#DDA0DD', '#F0E68C'
]

function getPrizeColor(index: number): string {
  return prizeColors[index % prizeColors.length]
}

function onStatusChange(e: any) {
  activityForm.value.status = e.detail.value
}

function onStartDateChange(e: any) {
  activityForm.value.start_time = e.detail.value
}

function onPrizeTypeChange(e: any) {
  // picker 返回的是字符串，需要转换为数字
  prizeForm.value.prize_type = parseInt(e.detail.value)
  if (prizeForm.value.prize_type === 1) {
    // 切换为神秘大奖时，默认心愿次数为10
    if (prizeForm.value.guarantee_count === 0) {
      prizeForm.value.guarantee_count = 10
    }
  } else {
    // 切换为普通奖品时清空心愿次数
    prizeForm.value.guarantee_count = 0
  }
}

function editActivity(activity: Activity) {
  editingActivity.value = activity
  activityForm.value = {
    title: activity.title,
    description: activity.description || '',
    status: activity.status,
    start_time: activity.start_time ? activity.start_time.split('T')[0] : '',
    draw_interval_days: activity.draw_interval_days || 1
  }
  showCreateActivity.value = true
}

function closeActivityModal() {
  showCreateActivity.value = false
  editingActivity.value = null
  activityForm.value = { title: '', description: '', status: 1, start_time: '', draw_interval_days: 1 }
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

  // 将概率字符串转换为数字
  const probability = parseFloat(prizeForm.value.probability)
  if (isNaN(probability) || probability < 0 || probability > 1) {
    uni.showToast({ title: '请输入有效的概率值(0-1)', icon: 'none' })
    return
  }

  // 神秘大奖验证
  if (prizeForm.value.prize_type === 1 && prizeForm.value.guarantee_count < 2) {
    uni.showToast({ title: '心愿次数至少为2次', icon: 'none' })
    return
  }

  try {
    await createPrize({
      activity_id: currentActivity.value.id,
      name: prizeForm.value.name,
      probability: probability,
      stock: prizeForm.value.stock,
      sort_order: prizeForm.value.sort_order,
      prize_type: prizeForm.value.prize_type,
      guarantee_count: prizeForm.value.guarantee_count
    })
    uni.showToast({ title: '添加成功', icon: 'success' })
    prizeForm.value = { name: '', probability: '', stock: 1, sort_order: 0, prize_type: 0, guarantee_count: 0 }

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

.empty {
  text-align: center;
  padding: 100rpx 0;
  color: #999;
}

/* 筛选器样式 */
.filter-section {
  background: #fff;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
}

.filter-picker {
  display: flex;
  align-items: center;
  padding: 24rpx;
  gap: 12rpx;
}

.filter-label {
  font-size: 28rpx;
  color: #666;
}

.filter-value {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
  flex: 1;
}

.filter-picker .picker-arrow {
  font-size: 20rpx;
  color: #999;
}

/* 统计卡片样式 */
.statistics-section {
  display: flex;
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.stat-card {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12rpx;
  padding: 24rpx 16rpx;
  text-align: center;
}

.stat-card:nth-child(2) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card:nth-child(3) {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-value {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 8rpx;
}

.stat-label {
  display: block;
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.9);
}

/* 加载提示 */
.loading-tip {
  text-align: center;
  padding: 30rpx;
  color: #999;
  font-size: 26rpx;
}

/* 记录项样式 */
.record-item {
  background: #fff;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.record-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8rpx;
}

.record-user {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
}

.record-separator {
  font-size: 28rpx;
  color: #999;
}

.record-activity {
  font-size: 28rpx;
  color: #666;
}

.record-time {
  font-size: 24rpx;
  color: #999;
}

.record-prize {
  font-size: 28rpx;
  color: #FF6B35;
  font-weight: 500;
}

.record-no-prize {
  font-size: 28rpx;
  color: #999;
}

/* 弹窗基础样式 */
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
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
}

/* 创建/编辑活动弹窗样式 */
.activity-modal {
  max-height: 85vh;
  padding: 0;
  display: flex;
  flex-direction: column;
}

/* 弹窗头部 */
.activity-modal-header {
  background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%);
  padding: 40rpx 30rpx;
  text-align: center;
  flex-shrink: 0;
}

.activity-modal-title {
  display: block;
  font-size: 36rpx;
  font-weight: 600;
  color: #fff;
}

/* 表单区域 */
.activity-form-section {
  padding: 30rpx;
  background: #FAFAFA;
  flex: 1;
  overflow-y: auto;
}

.activity-form-row {
  margin-bottom: 24rpx;
}

.activity-form-row:last-child {
  margin-bottom: 0;
}

.activity-form-group {
  display: flex;
  flex-direction: column;
}

.activity-form-label {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
  margin-bottom: 12rpx;
}

.activity-form-label .required {
  color: #FF6B35;
}

.activity-form-input {
  height: 84rpx;
  padding: 0 24rpx;
  background: #fff;
  border: 2rpx solid #E0E0E0;
  border-radius: 12rpx;
  font-size: 30rpx;
  color: #333;
  box-sizing: border-box;
}

.activity-form-input:focus {
  border-color: #FF6B35;
}

.activity-form-textarea {
  width: 100%;
  height: 160rpx;
  padding: 20rpx 24rpx;
  background: #fff;
  border: 2rpx solid #E0E0E0;
  border-radius: 12rpx;
  font-size: 30rpx;
  color: #333;
  box-sizing: border-box;
}

.activity-form-textarea:focus {
  border-color: #FF6B35;
}

.activity-picker {
  height: 84rpx;
  padding: 0 24rpx;
  background: #fff;
  border: 2rpx solid #E0E0E0;
  border-radius: 12rpx;
  font-size: 30rpx;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
}

.picker-arrow {
  font-size: 20rpx;
  color: #999;
}

/* 弹窗底部 */
.activity-modal-footer {
  padding: 20rpx 30rpx 40rpx;
  background: #fff;
  border-top: 1rpx solid #EEEEEE;
  display: flex;
  gap: 20rpx;
  flex-shrink: 0;
}

.btn-activity-cancel,
.btn-activity-confirm {
  flex: 1;
  height: 88rpx;
  border-radius: 12rpx;
  font-size: 32rpx;
  font-weight: 500;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-activity-cancel {
  background: #F5F5F5;
  color: #666;
}

.btn-activity-confirm {
  background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%);
  color: #fff;
  box-shadow: 0 4rpx 16rpx rgba(255, 107, 53, 0.3);
}

.btn-activity-confirm:active {
  opacity: 0.9;
}

/* 奖品管理弹窗样式 */
.prize-modal {
  max-height: 85vh;
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 弹窗头部 */
.prize-modal-header {
  background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%);
  padding: 40rpx 30rpx;
  text-align: center;
  flex-shrink: 0;
}

.prize-modal-title {
  display: block;
  font-size: 36rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8rpx;
}

.prize-modal-subtitle {
  display: block;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.9);
}

/* 可滚动内容区域 */
.prize-scroll-content {
  flex: 1;
  height: 0;
  overflow-y: auto;
}

/* 表单区域 */
.prize-form-section {
  padding: 30rpx;
  background: #FAFAFA;
  border-bottom: 1rpx solid #EEEEEE;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 24rpx;
}

.prize-form-row {
  display: flex;
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.prize-form-row.two-col {
  flex-direction: row;
}

.prize-form-row.two-col .form-group {
  flex: 1;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.name-group {
  width: 100%;
}

.form-group.full-width {
  width: 100%;
}

.form-label {
  font-size: 24rpx;
  color: #666;
  margin-bottom: 10rpx;
}

.label-hint {
  font-size: 20rpx;
  color: #999;
  font-weight: normal;
}

.form-input {
  height: 76rpx;
  padding: 0 24rpx;
  background: #fff;
  border: 2rpx solid #E0E0E0;
  border-radius: 12rpx;
  font-size: 28rpx;
  color: #333;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #FF6B35;
}

.form-picker {
  height: 76rpx;
  padding: 0 24rpx;
  background: #fff;
  border: 2rpx solid #E0E0E0;
  border-radius: 12rpx;
  font-size: 28rpx;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
}

.btn-add-prize {
  width: 100%;
  height: 80rpx;
  background: #FF6B35;
  color: #fff;
  font-size: 30rpx;
  font-weight: 500;
  border-radius: 12rpx;
  border: none;
  margin-top: 10rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-add-prize:active {
  opacity: 0.9;
}

/* 奖品列表区域 */
.prize-list-section {
  padding: 24rpx 30rpx;
  background: #fff;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.prize-count {
  font-size: 24rpx;
  color: #999;
}

.empty-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 0;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #bbb;
}

/* 奖品卡片列表 */
.prize-cards {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.prize-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx;
  background: #F8F9FA;
  border-radius: 16rpx;
  border: 1rpx solid #F0F0F0;
}

.prize-card-left {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.prize-index {
  width: 52rpx;
  height: 52rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 26rpx;
  font-weight: 600;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.prize-info-wrap {
  flex: 1;
  min-width: 0;
}

.prize-card-name {
  display: block;
  font-size: 30rpx;
  font-weight: 500;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.prize-name-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 8rpx;
}

.mystery-badge {
  font-size: 20rpx;
  color: #fff;
  background: linear-gradient(135deg, #9B59B6 0%, #8E44AD 100%);
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  flex-shrink: 0;
}

.prize-card-meta {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.meta-item {
  font-size: 24rpx;
}

.meta-value {
  color: #FF6B35;
  font-weight: 600;
}

.meta-label {
  color: #999;
  margin-left: 4rpx;
}

.meta-divider {
  color: #ddd;
  font-size: 22rpx;
}

.delete-btn-wrap {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFEEEE;
  border-radius: 50%;
  flex-shrink: 0;
}

.delete-icon {
  font-size: 40rpx;
  color: #FF6B6B;
  line-height: 1;
}

/* 弹窗底部 */
.prize-modal-footer {
  padding: 20rpx 30rpx 40rpx;
  background: #fff;
  border-top: 1rpx solid #EEEEEE;
  flex-shrink: 0;
}

.btn-close-modal {
  width: 100%;
  height: 88rpx;
  background: #F5F5F5;
  color: #666;
  font-size: 32rpx;
  font-weight: 500;
  border-radius: 16rpx;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
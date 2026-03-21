<template>
  <view class="container">
    <!-- Tab 切换 -->
    <view class="tabs">
      <view
        :class="['tab', activeTab === 'profile' ? 'active' : '']"
        @click="activeTab = 'profile'"
      >
        个人资料
      </view>
      <view
        :class="['tab', activeTab === 'records' ? 'active' : '']"
        @click="activeTab = 'records'"
      >
        中奖记录
      </view>
    </view>

    <!-- 我的信息 Tab -->
    <view v-if="activeTab === 'profile'" class="profile-content">
      <view class="profile-card">
        <!-- 头像 -->
        <!-- <view class="avatar-section">
          <image
            v-if="userProfile.avatar_url"
            :src="userProfile.avatar_url"
            class="avatar"
            mode="aspectFill"
          />
          <view v-else class="avatar avatar-default">
            <text class="avatar-text">{{ defaultAvatarText }}</text>
          </view>
        </view> -->

        <!-- 昵称 -->
        <view class="nickname-section">
          <text class="label">昵称</text>
          <view class="nickname-row">
            <text class="nickname">{{ userProfile.nickname || '未设置' }}</text>
            <text class="edit-btn" @click="showEditNickname = true">编辑</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 中奖记录 Tab -->
    <view v-if="activeTab === 'records'" class="records-content">
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

    <!-- 编辑昵称弹窗 -->
    <view v-if="showEditNickname" class="modal" @click="showEditNickname = false">
      <view class="modal-content" @click.stop>
        <view class="modal-title">修改昵称</view>
        <input
          v-model="newNickname"
          class="nickname-input"
          placeholder="请输入昵称（最多20字）"
          maxlength="20"
        />
        <view class="modal-buttons">
          <view class="btn-cancel" @click="showEditNickname = false">取消</view>
          <view class="btn-confirm" @click="handleSaveNickname">保存</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getMyRecords } from '@/api/lottery'
import { getUserProfile, updateUserProfile } from '@/api/user'

interface Record {
  id: number
  activity_id: number
  activity_title: string
  prize_id: number | null
  prize_name: string | null
  is_won: boolean
  created_at: string
}

interface UserProfile {
  id: number
  nickname: string | null
  avatar_url: string | null
  created_at: string
}

const activeTab = ref<'profile' | 'records'>('profile')
const records = ref<Record[]>([])
const userProfile = ref<UserProfile>({
  id: 0,
  nickname: null,
  avatar_url: null,
  created_at: ''
})
const showEditNickname = ref(false)
const newNickname = ref('')

const defaultAvatarText = computed(() => {
  if (userProfile.value.nickname) {
    return userProfile.value.nickname.charAt(0)
  }
  return '用'
})

onShow(() => {
  loadUserProfile()
  loadRecords()
})

async function loadUserProfile() {
  try {
    const res = await getUserProfile()
    userProfile.value = res
    newNickname.value = res.nickname || ''
  } catch (e) {
    console.error('加载用户信息失败', e)
  }
}

async function loadRecords() {
  try {
    const res = await getMyRecords()
    records.value = res || []
  } catch (e) {
    console.error('加载记录失败', e)
  }
}

async function handleSaveNickname() {
  const nickname = newNickname.value.trim()

  if (!nickname) {
    uni.showToast({ title: '昵称不能为空', icon: 'none' })
    return
  }

  if (nickname.length > 20) {
    uni.showToast({ title: '昵称不能超过20个字符', icon: 'none' })
    return
  }

  try {
    await updateUserProfile({ nickname })
    userProfile.value.nickname = nickname
    showEditNickname.value = false
    uni.showToast({ title: '修改成功', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message || '修改失败', icon: 'none' })
  }
}

function formatTime(time: string) {
  const date = new Date(time)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.container {
  min-height: 100vh;
  background: #f5f5f5;
}

/* Tab 切换样式 */
.tabs {
  display: flex;
  background: #fff;
  border-bottom: 1rpx solid #eee;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 28rpx 0;
  font-size: 30rpx;
  color: #666;
  position: relative;
}

.tab.active {
  color: #FF6B35;
  font-weight: 500;
}

.tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60rpx;
  height: 4rpx;
  background: #FF6B35;
  border-radius: 2rpx;
}

/* 我的信息样式 */
.profile-content {
  padding: 30rpx;
}

.profile-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 40rpx;
}

.avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 40rpx;
}

.avatar {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
}

.avatar-default {
  background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 60rpx;
  color: #fff;
  font-weight: bold;
}

.nickname-section {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.label {
  font-size: 26rpx;
  color: #999;
}

.nickname-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nickname {
  font-size: 34rpx;
  color: #333;
  font-weight: 500;
}

.edit-btn {
  font-size: 28rpx;
  color: #FF6B35;
  padding: 8rpx 24rpx;
  border: 1rpx solid #FF6B35;
  border-radius: 8rpx;
}

/* 中奖记录样式 */
.records-content {
  padding: 20rpx;
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
  width: 80%;
  max-width: 600rpx;
}

.modal-title {
  font-size: 34rpx;
  font-weight: bold;
  color: #333;
  text-align: center;
  margin-bottom: 40rpx;
}

.nickname-input {
  width: 100%;
  height: 88rpx;
  padding: 0 24rpx;
  border: 2rpx solid #e0e0e0;
  border-radius: 12rpx;
  font-size: 30rpx;
  box-sizing: border-box;
}

.nickname-input:focus {
  border-color: #FF6B35;
}

.modal-buttons {
  display: flex;
  gap: 20rpx;
  margin-top: 40rpx;
}

.btn-cancel,
.btn-confirm {
  flex: 1;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12rpx;
  font-size: 30rpx;
}

.btn-cancel {
  background: #f5f5f5;
  color: #666;
}

.btn-confirm {
  background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%);
  color: #fff;
}
</style>
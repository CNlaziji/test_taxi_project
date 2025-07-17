<template>
  <div class="ranking-container">
    <header class="top-bar">
      <button class="back-button" @click="goBack">&lt; 返回</button>
      <div class="tab-container">
        <div class="tab-item" :class="{ active: activeTab === 'congestion' }" @click="switchTab('congestion')">
          拥堵指数排行榜
        </div>
        <div class="tab-item" :class="{ active: activeTab === 'rideHailing' }" @click="switchTab('rideHailing')">
          易打车指数排行榜
        </div>
      </div>
      <!-- 添加右上角logo -->
      <!-- 修正文件扩展名从.png为.jpg -->
      <img src="@/assets/logo3.jpg" alt="Logo" class="header-logo">
    </header>

    <!-- 内容区域 -->
    <div class="content-area">
      <component :is="currentComponent"></component>
    </div>
  </div>
</template>

<script>
import CongestionRanking from './CongestionRanking.vue'
import RideHailingRanking from './RideHailingRanking.vue'

export default {
  components: {
    CongestionRanking,
    RideHailingRanking
  },
  data() {
    return {
      activeTab: 'congestion',
      currentComponent: 'CongestionRanking'
    }
  },
  methods: {
    goBack() {
      this.$router.push('/home')
    },
    switchTab(tab) {
      this.activeTab = tab
      this.currentComponent = tab === 'congestion' ? 'CongestionRanking' : 'RideHailingRanking'
    }
  }
}
</script>

<style scoped>
/* 基础样式 */
.ranking-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 20px;
}

/* 顶部操作栏 */
.top-bar {
  background-color: #2c3e50;
  color: white;
  padding: 15px 20px;
  position: relative;
}

/* 添加logo样式 */
.header-logo {
  position: absolute;
  top: 50%;
  right: 20px;
  transform: translateY(-50%);
  width: 160px; /* 从80px放大到160px */
  height: auto;
  cursor: pointer;
  transition: all 0.3s ease;
}

.header-logo:hover {
  transform: translateY(-50%) scale(1.05);
}
.back-button {
  background: none;
  border: none;
  color: white;
  font-size: 16px;
  cursor: pointer;
  padding: 5px 10px;
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  transition: color 0.3s ease; /* 添加过渡效果使颜色变化更平滑 */
}

.back-button:hover {
  color: #3498db; /* 悬停时变为蓝色，与项目整体风格一致 */
}

.tab-container {
  display: flex;
  justify-content: center;
  margin: 0 auto;
  max-width: 600px;
}

.tab-item {
  padding: 10px 20px;
  margin: 0 10px;
  cursor: pointer;
  border-bottom: 3px solid transparent;
}

.tab-item.active {
  border-bottom: 3px solid #3498db;
  font-weight: bold;
}

/* 内容区域 */
.content-area {
  padding: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .tab-container {
    flex-direction: column;
    align-items: center;
  }
  .tab-item {
    margin: 5px 0;
  }
}
</style>
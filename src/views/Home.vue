<template>
  <div class="home-container">
    <!-- 顶部操作栏 -->
    <header class="top-bar">
      <div class="welcome-message">欢迎 👤 {{ username }}！</div>
      <div class="top-actions">
        <router-link to="/login" class="logout-button">退出登录</router-link>
        <span class="divider">|</span>
        <router-link to="/home" class="home-link">首页</router-link>
      </div>
    </header>

    <!-- 信息区 -->
    <div class="info-section">
      <div class="date-card">
        <div class="day-name">{{ currentDate.dayName }}</div>
        <div class="date">{{ currentDate.month }} {{ currentDate.day }}, {{ currentDate.year }}</div>
      </div>
      <div class="clock">
        <div class="time">{{ currentTime }}</div>
      </div>
    </div>

    <!-- 功能入口 -->
    <div class="features-grid">
      <!-- 交通大数据概览 -->
      <el-card class="feature-card" @click="goToFeature('overview')">
        <div class="feature-icon">🚥</div>
        <div class="feature-title">出租车活动热力分析</div>
      </el-card>
      
      <!-- 附近最佳候车点 -->
      <el-card class="feature-card" @click="navigateToBigDataShow"> <!-- 修改方法名 -->
        <!-- 修改卡片标题（如果存在） -->
        <h3>客流趋势可视化</h3>
        <div class="feature-icon">🚗</div>
        <h3 class="feature-title">客流趋势分析</h3>
        <p class="feature-desc text-gray-light">分析出租车的流量变化趋势</p>
      </el-card>
      
      <!-- 排行榜 -->
      <el-card class="feature-card" @click="goToFeature('ranking')">
        <div class="feature-icon">📊</div>
        <div class="feature-title">排行榜</div>
      </el-card>
    </div>

    <!-- 右下角logo -->
    <div class="footer-logo">
      <img src="@/assets/logo3.jpg" alt="Logo" class="logo-image">
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '用户', // 实际项目中应从登录状态获取
      currentDate: {},
      currentTime: ''
    };
  },
  mounted() {
    this.updateDateTime();
    setInterval(this.updateDateTime, 1000);
  },
  methods: {
    updateDateTime() {
      const now = new Date();
      const dayNames = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'];
      const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

      this.currentDate = {
        dayName: dayNames[now.getDay()],
        month: monthNames[now.getMonth()],
        day: now.getDate(),
        year: now.getFullYear()
      };

      // 格式化时间 HH:MM:SS
      this.currentTime = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    },
    goToFeature(feature) {
      switch(feature) {
        case 'overview':
          this.$router.push('/big-data'); // 跳转到大数据服务页面
          break;
        case 'busstop':
          alert('跳转到附近最佳候车点页面');
          // this.$router.push('/busstop');
          break;
        case 'ranking':
          alert('跳转到排行榜页面');
          this.$router.push('/ranking'); // 添加路由跳转代码
          break;
      }
    }
  }
};
</script>

<script setup>
import { useRouter } from 'vue-router'; // 添加router导入
const router = useRouter(); // 初始化router实例

// 修改导航方法名以匹配新组件
const navigateToBigDataShow = () => {
  router.push('/best-waiting-point'); // 路由路径无需修改
};
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background-size: cover; /* 保持图片比例并覆盖整个容器 */
  background-position: center; /* 图片居中显示 */
  background-attachment: fixed; /* 固定背景图片，防止滚动时移动 */
  padding: 20px;
  color: white;
  background-image: url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80');
  margin: 0; /* 移除默认外边距 */
  background-repeat: no-repeat; /* 防止图片重复 */
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.welcome-message {
  font-size: 1.2rem;
  font-weight: bold;
}

.top-actions {
  display: flex;
  gap: 15px;
}

.logout-button, .home-link {
  color: white;
  text-decoration: none;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: all 0.3s ease; /* 添加过渡效果 */
}

.logout-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.home-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.divider {
  opacity: 0.5;
}

.info-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 60px;
  flex-wrap: wrap;
  gap: 20px;
}

.date-card {
  background-color: rgba(255, 255, 255, 0.2);
  padding: 15px 25px;
  border-radius: 8px;
  backdrop-filter: blur(5px);
}

.day-name {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.date {
  font-size: 1.1rem;
  opacity: 0.9;
}

.clock {
  background-color: rgba(255, 255, 255, 0.2);
  padding: 15px 25px;
  border-radius: 8px;
  backdrop-filter: blur(5px);
}

.time {
  font-size: 1.5rem;
  font-family: monospace;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.feature-card {
  background-color: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 12px;
  padding: 30px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.feature-card:hover {
  transform: translateY(-5px);
  background-color: rgba(255, 255, 255, 0.25);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.feature-title {
  font-size: 1.2rem;
  font-weight: bold;
  color: white; /* 添加字体颜色设置 */
}

/* 移动端适配 */
@media (max-width: 768px) {
  .info-section {
    flex-direction: column;
    align-items: stretch;
  }

  .date-card, .clock {
    text-align: center;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}

.feature-desc {
  margin-top: 10px;
  font-size: 0.9rem;
  opacity: 0.8;
}

/* 添加浅灰色文本样式 */
.text-gray-light {
  color: #cccccc;
}

/* 右下角logo样式 */
.footer-logo {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 100;
  opacity: 0.85;
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.footer-logo:hover {
  opacity: 1;
  transform: scale(1.05);
}

.logo-image {
  width: 220px; /* 缩小一倍，恢复原始尺寸 */
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .footer-logo {
    bottom: 15px;
    right: 15px;
  }
  
  .logo-image {
    width: 90px;
  }
}
</style>
<template>
  <div class="ride-hailing-ranking">
    <h2 class="ranking-title">易打车指数排行榜</h2>

    <div class="ranking-content">
      <div class="location-list">
        <div class="list-item" v-for="(item, index) in animatedData" :key="index" :style="{animationDelay: index * 0.1 + 's'}">
          <div class="rank-number">{{ index + 1 }}</div>
          <div class="location-name">{{ item.location }}</div>
          <div class="ranking-value">{{ item.displayValue.toFixed(0) }}</div>
        </div>
      </div>

      <div class="chart-container">
        <div id="rideHailingChart" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { dataAPI } from '@/api/api'; // ✅ 引入 dataAPI

export default {
  data() {
    return {
      rideHailingData: [], // ✅ 修改为初始空数组，数据从后端获取
      animatedData: [] // 用于数值动画的数据
    }
  },
  mounted() {
    this.fetchRideHailingData(); // ✅ 新增：调用获取数据的方法
  },
  methods: {
    async fetchRideHailingData() { // ✅ 新增：异步获取数据的方法
      try {
        const response = await dataAPI.getRideHailingIndex(); // 调用新的API接口
        // 假设后端返回的数据结构是 { ride_hailing_index: [{ location: 'xxx', value: 123 }, ...] }
        this.rideHailingData = response.data.ride_hailing_index;
        console.log('易打车指数数据:', this.rideHailingData);
        this.initDataAnimation(); // 数据获取后初始化动画
        this.$nextTick(() => {
          this.initChart(); // 数据获取后初始化图表
        });
      } catch (error) {
        console.error('获取易打车指数数据失败:', error);
        // 可以添加错误提示给用户
      }
    },
    initDataAnimation() {
      // 初始化动画数据
      this.animatedData = this.rideHailingData.map(item => ({
        ...item,
        displayValue: 0
      }))

      // 数值增长动画
      this.animatedData.forEach((item, index) => {
        const duration = 1500 // 动画持续时间
        const frameRate = 30 // 帧率
        const totalFrames = (duration / 1000) * frameRate
        const increment = item.value / totalFrames
        let currentFrame = 0

        const animationInterval = setInterval(() => {
          currentFrame++
          item.displayValue += increment

          if (currentFrame >= totalFrames || item.displayValue >= item.value) {
            item.displayValue = item.value
            clearInterval(animationInterval)
          }
        }, 1000 / frameRate)
      })
    },
    initChart() {
      try {
        // 获取图表容器
        const chartDom = document.getElementById('rideHailingChart')
        if (!chartDom) {
          console.error('图表容器元素未找到')
          return
        }

        // 销毁已有实例
        if (window.rideHailingChartInstance) {
          window.rideHailingChartInstance.dispose()
        }

        // 初始化图表
        const myChart = echarts.init(chartDom)
        window.rideHailingChartInstance = myChart // 保存实例引用

        const option = {
          tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            data: this.rideHailingData.map(item => item.location), // ✅ 使用后端数据
            axisLabel: {
              color: '#666',
              rotate: 30,
              interval: 0
            }
          },
          yAxis: {
            type: 'value',
            name: '推荐指数',
            nameLocation: 'middle',
            nameGap: 40,
            axisLine: { lineStyle: { color: '#ccc' }},
            axisLabel: { color: '#666' }
          },
          series: [{
            data: this.rideHailingData.map(item => item.value), // ✅ 使用后端数据
            type: 'bar',
            label: { 
              show: true, 
              position: 'top',
              color: '#333'
            },
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#2ecc71' },  // 浅绿色
                { offset: 1, color: '#27ae60' }   // 深绿色
              ])
            },
            barWidth: 30,
            animationDuration: 1500,
            animationEasing: 'elasticOut'
          }]
        }

        myChart.setOption(option)

        // 响应窗口大小变化
        const resizeHandler = () => myChart.resize()
        window.addEventListener('resize', resizeHandler)

        // 组件销毁时清理
        this.$on('hook:beforeDestroy', () => {
          window.removeEventListener('resize', resizeHandler)
          if (window.rideHailingChartInstance) {
            window.rideHailingChartInstance.dispose()
            window.rideHailingChartInstance = null
          }
        })

        console.log('图表初始化成功')
      } catch (error) {
        console.error('图表初始化失败:', error)
      }
    }
  }
}
</script>

<style scoped>
/* 样式保持不变 */
.ride-hailing-ranking {
  padding: 20px;
}

.ranking-title {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 24px;
  font-weight: bold;
}

.ranking-content {
  display: flex;
  gap: 20px;
  align-items: stretch;
  min-height: 400px;
}

.location-list {
  flex: 1;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.list-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  background-color: #f8f9fa;
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateY(10px);
  animation: fadeInUp 0.5s forwards;
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.list-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(52, 152, 219, 0.15);
  background-color: #f0f7ff;
}

.rank-number {
  width: 30px;
  height: 30px;
  line-height: 30px;
  text-align: center;
  color: white;
  background-color: #3498db;
  border-radius: 50%;
  margin-right: 15px;
  font-weight: bold;
}

.location-name {
  flex: 1;
  font-size: 16px;
  color: #333;
}

.ranking-value {
  color: #2980b9;
  font-weight: bold;
  font-size: 18px;
  min-width: 50px;
  text-align: right;
}

.chart-container {
  flex: 1.5;
  height: 400px;
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.chart {
  width: 100%;
  height: 100%;
}
</style>
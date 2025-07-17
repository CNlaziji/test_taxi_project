<template>
  <div class="congestion-ranking">
    <h2 class="ranking-title">当下拥堵指数排行</h2>

    <div class="ranking-content">
      <div class="location-list">
        <div class="list-item" v-for="(item, index) in congestionData" :key="index">
          <div class="rank-number">{{ index + 1 }}</div>
          <div class="location-name">{{ item.location }}</div>
          <div class="congestion-value">{{ item.value }}</div>
        </div>
      </div>

      <div class="chart-container">
        <div id="congestionChart" class="chart"></div>
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
      congestionData: [] // ✅ 修改为初始空数组，数据从后端获取
    }
  },
  mounted() {
    this.fetchCongestionData(); // ✅ 新增：调用获取数据的方法
  },
  methods: {
    async fetchCongestionData() { // ✅ 新增：异步获取数据的方法
      try {
        const response = await dataAPI.getCongestionIndex(); // 调用新的API接口
        // 假设后端返回的数据结构是 { congestion_index: [{ location: 'xxx', value: 123 }, ...] }
        this.congestionData = response.data.congestion_index;
        console.log('拥堵指数数据:', this.congestionData);
        this.$nextTick(() => {
          this.initChart(); // 数据获取后初始化图表
        });
      } catch (error) {
        console.error('获取拥堵指数数据失败:', error);
        // 可以添加错误提示给用户
      }
    },
    initChart() {
      const chartDom = document.getElementById('congestionChart')
      const myChart = echarts.init(chartDom)

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          max: 300,
          name: '指数',
          nameLocation: 'middle',
          nameGap: 30
        },
        yAxis: {
          type: 'category',
          data: this.congestionData.map(item => item.location), // ✅ 使用后端数据
          inverse: true
        },
        series: [{
          data: this.congestionData.map(item => item.value), // ✅ 使用后端数据
          type: 'bar',
          label: {
            show: true,
            position: 'right'
          },
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#3498db' },
              { offset: 1, color: '#2980b9' }
            ])
          }
        }]
      }

      myChart.setOption(option)

      // 响应窗口大小变化
      window.addEventListener('resize', () => {
        myChart.resize()
      })
    }
  }
}
</script>

<style scoped>
/* 样式保持不变 */
.ranking-title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.ranking-content {
  display: flex;
  gap: 20px;
  height: 400px;
}

.location-list {
  flex: 1;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  overflow-y: auto;
}

.list-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.rank-number {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #3498db;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-weight: bold;
}

.location-name {
  flex: 1;
}

.congestion-value {
  color: #e74c3c;
  font-weight: bold;
}

.chart-container {
  flex: 2;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 15px;
}

.chart {
  width: 100%;
  height: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ranking-content {
    flex-direction: column;
    height: auto;
  }
  .location-list,
  .chart-container {
    width: 100%;
    height: 300px;
  }
}
</style>
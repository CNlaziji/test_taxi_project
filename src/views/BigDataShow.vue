<template>
  <div class="data-analysis-container">
    <div class="top-bar">
      <button class="back-btn" @click="goBack">&lt; 返回</button>
      <h1 class="page-title">数据分析与洞察</h1>
      <img src="@/assets/logo3.jpg" alt="Logo" class="header-logo"> </div>

    <div class="data-indicators-buttons">
      <el-button
        :class="{ 'active': activeChart === 'passengerCount' }"
        @click="loadAndRenderChart('passengerCount')"
      >
        载客数量
      </el-button>
      <el-button
        :class="{ 'active': activeChart === 'weeklyFlow' }"
        @click="loadAndRenderChart('weeklyFlow')"
      >
        周客流量
      </el-button>
      <el-button
        :class="{ 'active': activeChart === 'tripInfo' }"
        @click="loadAndRenderChart('tripInfo')"
      >
        行程信息
      </el-button>
      <el-button
        :class="{ 'active': activeChart === 'currentPassengerFlow' }"
        @click="loadAndRenderChart('currentPassengerFlow')"
      >
        当前客流
      </el-button>
      <el-button
        :class="{ 'active': activeChart === 'tripShare' }"
        @click="loadAndRenderChart('tripShare')"
      >
        运客行程分享
      </el-button>
      </div>

    <div class="chart-display-area">
      <div v-if="activeChart" id="mainChart" class="chart-canvas"></div>
      <div v-else class="chart-placeholder">
        <p>请选择一个指标以显示数据图表</p>
      </div>
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <p>数据加载中...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { dataAPI } from '@/api/api'; // 请确保这个路径是正确的
import * as echarts from 'echarts'; // 引入 ECharts
import 'echarts-gl'; // **新增：引入 ECharts GL 以支持三维图**
import { ElMessage } from 'element-plus'; // 引入 ElMessage (此处已修正为element-plus)

const router = useRouter();
const activeChart = ref(''); // 当前激活的图表类型
const chartData = ref(null); // 存储图表数据
let currentChartInstance = null; // ECharts 实例
const loading = ref(false); // 加载状态

// 返回上一页
const goBack = () => {
  router.go(-1);
};

// 在组件销毁前销毁 ECharts 实例
onBeforeUnmount(() => {
  if (currentChartInstance) {
    currentChartInstance.dispose();
    currentChartInstance = null;
    window.removeEventListener('resize', resizeChart);
  }
});

// 统一的数据加载和图表渲染函数
const loadAndRenderChart = async (chartType) => {
  activeChart.value = chartType;
  loading.value = true;
  chartData.value = null; // 清空旧数据
  destroyChart(); // 销毁现有图表

  try {
    let response;
    let dataKey; // 用于从响应中提取数据的键名
    switch (chartType) {
      case 'passengerCount': // 载客数量 (对应 jn_o_number)
        response = await dataAPI.getJnONumber();
        dataKey = 'jn_o_number';
        break;
      case 'weeklyFlow': // 周客流量 (对应 jn_time_o_1hour)
        response = await dataAPI.getJnTimeO1Hour();
        dataKey = 'jn_time_o_1hour';
        break;
      case 'tripInfo': // 行程信息 (对应 trip_records)
        response = await dataAPI.getTripRecords();
        dataKey = 'trip_records';
        break;
      case 'currentPassengerFlow': // 当前客流 (对应 jn_time_o_1hour)
        response = await dataAPI.getJnTimeO1Hour();
        dataKey = 'jn_time_o_1hour';
        break;
      case 'tripShare': // 运客行程分享 (对应 jn_luc)
        response = await dataAPI.getJnLuc();
        dataKey = 'jn_luc';
        break;
      // case 'passengerWeather': // 客流与天气 (可能对应 jn_time_o_15min 或其他天气相关接口)
      //   response = await dataAPI.getJnTimeO15Min(); // 假设使用15分钟数据
      //   dataKey = 'jn_time_o_15min';
      //   break;
      default:
        ElMessage.warning('未知图表类型。');
        return;
    }

    // 统一处理响应和数据提取
    if (response && response.data && Array.isArray(response.data[dataKey])) {
      chartData.value = response.data[dataKey];
      // 添加调试输出查看字段结构
      console.log('数据字段结构:', chartData.value[0]);
      ElMessage.success(`${activeChart.value} 数据加载成功`);
    } else {
      ElMessage.error(response.data.message || `${activeChart.value} 数据获取失败或格式不正确。`);
      chartData.value = []; // 确保数据为空数组，避免后续报错
    }

    if (chartData.value.length > 0) { // 只有有数据时才渲染
      renderInPageChart(chartType, chartData.value);
    } else {
      ElMessage.warning('没有可用于渲染图表的数据。');
      const chartDom = document.getElementById('mainChart');
      if (chartDom) chartDom.innerHTML = '<div style="text-align: center; padding-top: 50px; color: #999;">暂无数据</div>';
      destroyChart();
    }

  } catch (error) {
    ElMessage.error(`数据加载失败: ${error.message}`);
    console.error(error);
    chartData.value = []; // 确保数据为空数组，避免后续报错
    const chartDom = document.getElementById('mainChart');
    if (chartDom) chartDom.innerHTML = '<div style="text-align: center; padding-top: 50px; color: #999;">数据加载失败</div>';
    destroyChart();
  } finally {
    loading.value = false;
  }
};

// 渲染 ECharts 图表
const renderInPageChart = (chartType, data) => {
  const chartDom = document.getElementById('mainChart');
  if (!chartDom) {
    console.error('ECharts 容器 #mainChart 未找到！');
    return;
  }

  destroyChart(); // 销毁旧实例，防止重复初始化
  currentChartInstance = echarts.init(chartDom);
  let option = {};

  switch (chartType) {
    case 'passengerCount':
      option = getPassengerCountChartOption(data);
      break;
    case 'weeklyFlow':
      option = getWeeklyFlowChartOption(data);
      break;
    case 'tripInfo':
      option = getTripAnalysisChartOption(data); // **已改为三维图**
      break;
    case 'currentPassengerFlow':
      option = getCurrentPassengerFlowChartOption(data);
      break;
    case 'tripShare':
      option = getTripShareChartOption(data);
      break;
    // case 'passengerWeather':
    //   option = getPassengerWeatherChartOption(data); // 需要实现此方法
    //   break;
    default:
      console.warn('未知图表类型:', chartType);
      destroyChart();
      return;
  }

  if (option) {
    currentChartInstance.setOption(option);
    window.addEventListener('resize', resizeChart);
  }
};

// 销毁 ECharts 实例
const destroyChart = () => {
  if (currentChartInstance) {
    currentChartInstance.dispose();
    currentChartInstance = null;
    window.removeEventListener('resize', resizeChart);
  }
};

// 响应式调整图表大小
const resizeChart = () => {
  if (currentChartInstance) {
    currentChartInstance.resize();
  }
};

// --- ECharts 配置选项生成方法 ---
// 载客数量图表 (jn_o_number)
const getPassengerCountChartOption = (data) => {
  const times = data.map(item => {
    const date = new Date(item.time);
    return `${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  });
  const numbers = data.map(item => item.number);

  return {
    title: { text: '载客数量趋势', left: 'center', textStyle: { color: '#eee' } },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: times,
      axisLabel: {
        color: '#ccc',
        rotate: 45,
        interval: Math.ceil(data.length / 10)
      },
      axisLine: { lineStyle: { color: '#444' } }
    },
    yAxis: {
      type: 'value',
      name: '数量',
      axisLabel: { color: '#ccc' },
      splitLine: { lineStyle: { color: '#333' } }
    },
    series: [{
      name: '数量',
      type: 'line',
      data: numbers,
      itemStyle: { color: '#409EFF' },
      lineStyle: { width: 2 },
      smooth: true
    }],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    dataZoom: [
      { type: 'slider', show: true, xAxisIndex: [0], start: 0, end: 100, textStyle: { color: '#ccc' } },
      { type: 'inside', xAxisIndex: [0], start: 0, end: 100 }
    ]
  };
};

// 周客流量图表 (jn_time_o_1hour)
const getWeeklyFlowChartOption = (data) => {
  // 确保数据有效，过滤掉无效项
  const validData = data.filter(item => item.O_time && typeof item.count === 'number');

  // 按天聚合客流数据
  const dailyFlow = {};
  validData.forEach(item => {
    const date = new Date(item.O_time);
    // 获取 YYYY-MM-DD 格式的日期作为 key
    const dateKey = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
    if (!dailyFlow[dateKey]) {
      dailyFlow[dateKey] = 0;
    }
    dailyFlow[dateKey] += item.count;
  });

  // 将聚合后的数据转换为 ECharts 格式
  const sortedDates = Object.keys(dailyFlow).sort();
  const dailyCounts = sortedDates.map(date => dailyFlow[date]);

  return {
    title: { text: '周客流量：每日总客流统计', left: 'center', textStyle: { color: '#eee' } },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: {
      type: 'category',
      data: sortedDates, // x轴显示日期
      axisLabel: {
        color: '#ccc',
        rotate: 45,
        interval: Math.ceil(sortedDates.length / 7) // 确保日期可读，最多显示7个左右
      },
      axisLine: { lineStyle: { color: '#444' } }
    },
    yAxis: {
      type: 'value',
      name: '总客流数量',
      axisLabel: { color: '#ccc' },
      splitLine: { lineStyle: { color: '#333' } }
    },
    series: [{
      name: '每日总客流',
      type: 'bar',
      data: dailyCounts,
      itemStyle: { color: '#67C23A' }, // 绿色柱状图
      barWidth: '60%'
    }],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    dataZoom: [
      { type: 'slider', show: true, xAxisIndex: [0], start: 0, end: 100, textStyle: { color: '#ccc' } },
      { type: 'inside', xAxisIndex: [0], start: 0, end: 100 }
    ]
  };
};


// 行程信息图表 (trip_records) - **更改为三维散点图**
const getTripAnalysisChartOption = (data) => {
  // 过滤掉不完整的或无效的记录，并转换字符串为数字
  const validRecords = data.filter(item => {
    // 将字符串字段转换为数字
    const distance = parseFloat(item.trip_distance_km);
    const duration = parseFloat(item.trip_duration_min);
    const hour = Number(item.trip_hour);
    // 检查转换后是否为有效数字
    return !isNaN(distance) && !isNaN(duration) && !isNaN(hour);
  });

  const scatterData = validRecords.map(item => [
    parseFloat(item.trip_distance_km), // X轴：订单距离（转换为数字）
    parseFloat(item.trip_duration_min), // Y轴：订单耗时（转换为数字）
    Number(item.trip_hour)              // Z轴：订单时段（转换为数字）
  ]);

  return {
    title: {
      text: '行程分析：订单距离、耗时与时段三维散点图',
      left: 'center',
      textStyle: {
        color: '#eee'
      }
    },
    tooltip: {
      formatter: function (param) {
        return `订单距离: ${param.data[0]} 公里<br/>订单耗时: ${param.data[1]} 分钟<br/>订单时段: ${param.data[2]} 点`;
      }
    },
    visualMap: {
      show: true,  // 显示颜色映射条，直观展示Z轴维度
      min: 0,
      max: 23,
      dimension: 2,  // 对应Z轴（订单时段）
      inRange: {
        color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
      },
      calculable: true,
      textStyle: { color: '#ccc' },
      orient: 'horizontal',  // 水平放置色条
      left: 'center',
      bottom: 20
    },
    grid3D: {
      boxWidth: 150,  // 调整为更均衡的比例
      boxDepth: 150,  // 与宽度保持一致，增强深度感
      light: {
        main: { intensity: 1.2 },
        ambient: { intensity: 0.3 }
      },
      axisLine: { lineStyle: { color: '#ccc' } },
      axisLabel: { color: '#ccc' },
      // 添加视角控制
      viewControl: {
        enabled: true,
        autoRotate: true,  // 自动旋转
        autoRotateSpeed: 10,  // 旋转速度
        distance: 300,  // 相机距离
        alpha: 45,  // 仰角
        beta: 45   // 方位角
      }
    },
    xAxis3D: {
      name: '订单距离 (公里)',
      type: 'value',
      max: 50,  // X轴最大值设为50
      axisLabel: {
        formatter: '{value}km'
      }
    },
    yAxis3D: {
      name: '订单耗时 (分钟)',
      type: 'value',
      max: 100,  // Y轴最大值设为50
      axisLabel: {
        formatter: '{value}min'
      }
    },
    zAxis3D: {
      name: '订单时段 (小时)',
      type: 'value',
      max: 50,  // Z轴最大值设为50
      axisLabel: {
        formatter: '{value}h'
      }
    },
    series: [
      {
        name: '行程数据',
        type: 'scatter3D',
        data: scatterData, // 传入三维坐标数据
        symbolSize: 6,  // 增大散点大小
        itemStyle: {
          opacity: 0.7,  // 降低透明度，减少重叠遮挡
          borderWidth: 0.5,
          borderColor: '#fff'
        },
        emphasis: {
          itemStyle: {  // 鼠标悬停时放大
            symbolSize: 10,
            opacity: 1
          }
        },
        animation: !scatterData.length, // 如果数据为空，不进行动画
        // progressive: scatterData.length > 5000 ? 500 : 0 // 可选：启用渐进渲染，如果数据量大
      }
    ]
  };
};

// 当前客流图表 (jn_time_o_1hour)
const getCurrentPassengerFlowChartOption = (data) => {
  const times = data.map(item => {
    const date = new Date(item.O_time);
    return `${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:00`;
  });
  const counts = data.map(item => item.count);

  return {
    title: { text: '1小时粒度客流趋势', left: 'center', textStyle: { color: '#eee' } },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: times,
      axisLabel: {
        color: '#ccc',
        rotate: 45,
        interval: Math.ceil(data.length / 10)
      },
      axisLine: { lineStyle: { color: '#444' } }
    },
    yAxis: {
      type: 'value',
      name: '客流数量',
      axisLabel: { color: '#ccc' },
      splitLine: { lineStyle: { color: '#333' } }
    },
    series: [{
      name: '客流数量',
      type: 'line',
      data: counts,
      itemStyle: { color: '#67C23A' },
      lineStyle: { width: 2 },
      smooth: true
    }],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    dataZoom: [
      { type: 'slider', show: true, xAxisIndex: [0], start: 0, end: 100, textStyle: { color: '#ccc' } },
      { type: 'inside', xAxisIndex: [0], start: 0, end: 100 }
    ]
  };
};

// 运客行程分享图表 (jn_luc)
const getTripShareChartOption = (data) => {
  // 聚合所有天的短途、中途、长途数据
  let totalNear = 0;
  let totalMiddle = 0;
  let totalFar = 0;

  // 确保数据有效，过滤掉无效项
  const validData = data.filter(item => typeof item.near === 'number' && typeof item.middle === 'number' && typeof item.far === 'number');

  validData.forEach(item => {
    totalNear += item.near;
    totalMiddle += item.middle;
    totalFar += item.far;
  });

  const chartData = [
    { value: totalNear, name: '短途客流' },
    { value: totalMiddle, name: '中途客流' },
    { value: totalFar, name: '长途客流' }
  ];

  return {
    title: { text: '运客行程分享：行程长度比例', left: 'center', textStyle: { color: '#eee' } },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: ['短途客流', '中途客流', '长途客流'],
      textStyle: { color: '#ccc' }
    },
    series: [
      {
        name: '行程类型',
        type: 'pie',
        radius: ['40%', '70%'], // 环形图
        avoidLabelOverlap: false,
        label: {
          show: true,
          position: 'outside',
          formatter: '{b}: {d}%', // 显示名称和百分比
          color: '#ccc'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '20',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: true
        },
        data: chartData,
        itemStyle: {
          borderRadius: 8, // 圆角
          borderColor: '#fff',
          borderWidth: 2
        }
      }
    ]
  };
};

// 如果需要 "客流与天气" 图表，需要实现 getPassengerWeatherChartOption 方法
// const getPassengerWeatherChartOption = (data) => {
//   // 实现客流与天气图表逻辑，可能需要更多数据字段
//   // 例如：data.map(item => item.O_time), data.map(item => item.count), data.map(item => item.weather_temp)
//   return { /* ECharts option */ };
// };
</script>

<style scoped>
/* 基本容器样式 */
.data-analysis-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: #0f172a; /* 深色背景 */
  color: white;
  font-family: 'Arial', sans-serif;
}

/* 顶部操作栏 */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: rgba(15, 23, 42, 0.7);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  z-index: 1000;
}

.back-btn {
  background-color: #165DFF;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

.back-btn:hover {
  background-color: #0a4ae6;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  color: #fff;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
  margin: 0 auto; /* 居中标题 */
}

.header-logo {
  width: 160px;
  height: auto;
  cursor: pointer;
}

/* 数据指标按钮组 */
.data-indicators-buttons {
  padding: 20px;
  background-color: rgba(15, 23, 42, 0.5);
  display: flex;
  justify-content: center;
  gap: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  z-index: 999;
  flex-wrap: wrap; /* 允许按钮换行 */
}

.data-indicators-buttons .el-button {
  background-color: rgba(30, 41, 59, 0.8);
  color: #c0c4cc;
  border: 1px solid #4a5568;
  padding: 12px 25px;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  min-width: 150px; /* 增加按钮宽度 */
}

.data-indicators-buttons .el-button:hover {
  background-color: #2a3a4e;
  color: white;
  border-color: #6a7c93;
  transform: translateY(-2px);
}

.data-indicators-buttons .el-button.active {
  background-color: #165DFF;
  color: white;
  border-color: #165DFF;
  box-shadow: 0 0 15px rgba(22, 93, 255, 0.6);
  font-weight: bold;
}

/* 图表展示区域 */
.chart-display-area {
  flex: 1;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background-color: #1a2035; /* 图表区域背景 */
  overflow: auto; /* 允许滚动 */
}

.chart-canvas {
  width: 100%;
  max-width: 1200px; /* 控制图表最大宽度 */
  height: 100%;
  min-height: 400px; /* 确保最小高度 */
  background-color: #1a2035; /* 确保 ECharts 容器背景色 */
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.chart-placeholder {
  font-size: 20px;
  color: #888;
  text-align: center;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1001;
  color: white;
  font-size: 18px;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #165DFF;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
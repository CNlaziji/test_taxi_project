<template>
  <div class="big-data-container">
    <header class="top-bar">
      <el-button @click="$router.go(-1)" class="back-button">< 返回</el-button>
      <h1 class="page-title">出租车大数据服务平台</h1>
      <div class="current-time">{{ currentTime }}</div>
    </header>

    <el-tabs v-model="activeTab" class="function-tabs" @tab-click="handleTabClick">
      <el-tab-pane label="热力预测" name="heatPrediction"></el-tab-pane>
      <el-tab-pane label="热力图" name="heatMap"></el-tab-pane>
      <el-tab-pane label="上客点查询" name="pickupQuery"></el-tab-pane>
    </el-tabs>

    <div class="map-container">
      <div id="map" class="map"></div>
      <div class="search-box">
        <el-input v-model="searchKeyword" placeholder="热门上客点查询" class="search-input">
          <template #append>
            <el-button @click="handleSearch">🔍</el-button>
          </template>
        </el-input>
      </div>
    </div>
  </div>
</template>

<script>
import { dataAPI } from '@/api/api';
// 移除了 ECharts 引入，因为此页面不再显示图表
// import * as echarts from 'echarts';

export default {
  name: 'BigDataService',
  data() {
    return {
      activeTab: 'heatMap',
      currentTime: '',
      searchKeyword: '',
      map: null,
      mapLoaded: false,
      heatmapOverlay: null,
      pickupMarkers: [],
      vehicleMarkers: [], // 虽然在这个页面不使用，但保留以防万一或为未来扩展
      routeOverlays: [],
      heatmapPluginReady: false,

      // 移除了所有弹窗和图表相关的数据属性
      // dialogVisible: false,
      // dialogTitle: '',
      // chartData: null,
      // chartType: '',
      // currentChartInstance: null,
    };
  },
  mounted() {
    this.updateCurrentTime();
    setInterval(this.updateCurrentTime, 1000);
    this.loadAMapScript();
  },
  beforeDestroy() {
    // 移除了图表实例销毁逻辑
    // if (this.currentChartInstance) {
    //   this.currentChartInstance.dispose();
    //   this.currentChartInstance = null;
    //   window.removeEventListener('resize', this.currentChartInstance.resize);
    // }
  },
  methods: {
    updateCurrentTime() {
      const now = new Date();
      const year = now.getFullYear();
      const month = (now.getMonth() + 1).toString().padStart(2, '0');
      const day = now.getDate().toString().padStart(2, '0');
      const hours = now.getHours().toString().padStart(2, '0');
      const minutes = now.getMinutes().toString().padStart(2, '0');
      const seconds = now.getSeconds().toString().padStart(2, '0');
      this.currentTime = `${year}.${month}.${day} ${hours}:${minutes}:${seconds}`;
    },

    loadAMapScript() {
      if (window.AMap) {
        console.log('AMap API 已存在，尝试初始化地图。');
        this.initAMap();
        return;
      }

      const script = document.createElement('script');
      // 请替换为你的高德地图API Key
      script.src = 'https://webapi.amap.com/maps?v=2.0&key=91e6fc5a83148b3d36b28883e6738d79&plugin=AMap.ToolBar,AMap.Scale,AMap.Geocoder,AMap.MoveAnimation,AMap.HeatMap';
      script.type = 'text/javascript';
      script.onload = () => {
        console.log('高德地图API脚本加载完成');
        this.initAMap();
      };
      script.onerror = () => {
        this.$message.error('高德地图API脚本加载失败，请检查网络和Key配置。');
        console.error('高德地图API脚本加载失败');
      };
      document.head.appendChild(script);
    },

    initAMap() {
      if (!window.AMap) {
        this.$message.error('高德地图API未加载，无法初始化地图');
        console.error('window.AMap is not available.');
        return;
      }

      if (this.map) {
        console.log('地图已初始化，跳过重复初始化。');
        return;
      }

      this.map = new AMap.Map('map', {
        center: [117.000923, 36.675807],
        zoom: 14,
        lang: 'zh_cn'
      });
      this.mapLoaded = true;

      this.map.addControl(new AMap.ToolBar());
      this.map.addControl(new AMap.Scale());

      // 示例标记点 (您可以根据需要移除或修改)
      const markers = [
        { position: [117.0200, 36.6683], name: '大明湖' },
        { position: [117.0097, 36.6690], name: '趵突泉' },
      ];
      markers.forEach(markerInfo => {
        new AMap.Marker({ position: markerInfo.position, title: markerInfo.name, map: this.map });
      });

      this.map.plugin(["AMap.HeatMap"], () => {
        if (!window.AMap || !window.AMap.HeatMap) {
          console.error('AMap.HeatMap 构造函数在插件回调中仍不可用！');
          this.$message.error('热力图插件未加载成功，请检查地图Key和插件配置。');
          this.heatmapPluginReady = false;
          return;
        }

        if (!this.heatmapOverlay || !(this.heatmapOverlay instanceof window.AMap.HeatMap)) {
          try {
            this.heatmapOverlay = new window.AMap.HeatMap(this.map, {
                radius: 25,
                opacity: [0, 0.8],
            });
            console.log('高德热力图对象成功初始化并赋值给 this.heatmapOverlay:', this.heatmapOverlay);
            this.heatmapPluginReady = true;

            // 如果当前标签是热力图，且此时热力图才准备就绪，则立即加载数据
            if (this.activeTab === 'heatMap') {
                console.log('热力图插件准备就绪，且当前标签为热力图，触发加载数据。');
                this.loadHeatmapData();
            }
          } catch (e) {
            console.error('高德热力图对象初始化失败:', e);
            this.$message.error('热力图初始化失败，请检查Amap.HeatMap插件。');
            this.heatmapOverlay = null;
            this.heatmapPluginReady = false;
          }
        } else {
          console.log('高德热力图对象已存在且有效，跳过重复创建。');
          this.heatmapPluginReady = true;
        }
      });

      if (!this.isSupportCanvas()) {
        this.$message.warning('您的浏览器不支持Canvas，热力图功能可能无法正常显示。请尝试更换浏览器。');
      }
      console.log('高德地图基础初始化完成', this.map);
    },

    isSupportCanvas() {
      var elem = document.createElement('canvas');
      return !!(elem.getContext && elem.getContext('2d'));
    },

    handleSearch() {
      if (!this.searchKeyword.trim() || !this.mapLoaded) {
        this.$message.warning('请输入搜索关键词并确保地图已加载。');
        return;
      }
      if (!window.AMap || !window.AMap.Geocoder) {
        this.$message.error('高德地理编码插件未加载，无法执行搜索功能。');
        console.error('window.AMap.Geocoder is not available.');
        return;
      }

      const geocoder = new AMap.Geocoder({});
      geocoder.getLocation(this.searchKeyword, (status, result) => {
        if (status === 'complete' && result.info === 'OK') {
          if (result.geocodes.length > 0) {
            const point = result.geocodes[0].location;
            this.map.setCenter([point.lng, point.lat]);
            this.map.setZoom(15);
            this.clearAllOverlays();
            const marker = new AMap.Marker({
              position: [point.lng, point.lat],
              map: this.map,
              title: this.searchKeyword,
              animation: 'AMAP_ANIMATION_BOUNCE'
            });
            this.pickupMarkers.push(marker);
            const infoWindow = new AMap.InfoWindow({
              content: `<div><strong>${this.searchKeyword}</strong></div>`,
              offset: new AMap.Pixel(0, -30)
            });
            infoWindow.open(this.map, [point.lng, point.lat]);
            this.$message.success('地点搜索完成。');
          } else {
            this.$message.warning('未找到该地点，请尝试其他关键词。');
          }
        } else {
          this.$message.error(`地理编码服务请求失败: ${result.info}`);
          console.error('Geocoding error:', result);
        }
      });
    },

    // 加载热力图数据 (实时热力图)
    async loadHeatmapData() {
      if (!this.heatmapPluginReady) {
        this.$message.warning('热力图库正在加载中，请稍候...');
        setTimeout(() => this.loadHeatmapData(), 1000);
        return;
      }

      this.loading = true;
      try {
        const response = await dataAPI.getHotspots();

        if (response.data && response.data.hotspots) {
          this.renderHeatmap(response.data.hotspots);
        } else {
          this.$message.error(response.data.message || '热力图数据格式不正确或为空');
        }
      } catch (error) {
        this.$message.error('热力图数据加载失败');
        console.error('Heatmap data fetch error:', error);
      } finally {
        this.loading = false;
      }
    },

    // 渲染热力图
    renderHeatmap(data) {
      if (!this.map || !this.heatmapOverlay || !(this.heatmapOverlay instanceof window.AMap.HeatMap)) {
          this.$message.warning('地图或热力图对象未准备就绪，无法渲染。');
          console.error('Map or heatmapOverlay is not ready or not an AMap.HeatMap instance.');
          return;
      }

      if (!Array.isArray(data) || data.length === 0) {
          this.$message.warning('热力图数据为空或格式错误');
          console.error('热力图数据异常:', data);
          this.heatmapOverlay.setDataSet({ data: [] });
          return;
      }

      const points = data.map(item => {
          return { lng: item.lng, lat: item.lat, count: item.count };
      });

      const maxCount = points.reduce((max, p) => Math.max(max, p.count), 0) || 10;

      this.heatmapOverlay.setDataSet({
          data: points,
          max: maxCount
      });
      this.heatmapOverlay.show();
      this.$message.success('热力图数据加载完成');
    },

    // 新增方法：加载并渲染预测热力图
    async loadPredictedHeatmapData() {
      if (!this.heatmapPluginReady) {
        this.$message.warning('热力图库正在加载中，请稍候...');
        setTimeout(() => this.loadPredictedHeatmapData(), 1000);
        return;
      }

      this.loading = true;
      try {
        const response = await dataAPI.getGriddedHotspots();

        if (response.data && response.data.gridded_hotspots) {
          const points = response.data.gridded_hotspots.map(item => {
              return { lng: item.center_lng, lat: item.center_lat, count: item.predicted_hotspot_count || 0 };
          });

          const maxCount = points.reduce((max, p) => Math.max(max, p.count), 0) || 10;

          this.heatmapOverlay.setDataSet({ data: points, max: maxCount });
          this.heatmapOverlay.show();
          this.$message.success('预测热力图数据加载完成');
        } else {
          this.$message.error(response.data.message || '预测热力图数据格式不正确或为空');
        }
      } catch (error) {
        this.$message.error('预测热力图数据加载失败');
        console.error('Predicted heatmap data fetch error:', error);
      } finally {
        this.loading = false;
      }
    },

    async loadPickupPointsData() {
      console.log('尝试加载上客点数据...');
      this.loading = true;
      try {
        const response = await dataAPI.getGriddedHotspots();

        if (response.data && Array.isArray(response.data.gridded_hotspots)) {
          console.log('上客点数据获取成功:', response.data.gridded_hotspots);
          this.renderPickupPoints(response.data.gridded_hotspots);
        } else {
          this.$message.error(response.data.message || '上客点数据获取失败或格式不正确。');
        }
      } catch (error) {
        this.$message.error('上客点数据加载失败');
        console.error('Pickup points data fetch error:', error);
      } finally {
        this.loading = false;
      }
    },
    renderPickupPoints(points) {
      if (!this.mapLoaded) return;
      console.log('开始渲染上客点...');

      this.pickupMarkers.forEach(marker => marker.setMap(null));
      this.pickupMarkers = [];

      if (!Array.isArray(points)) {
        this.$message.error('上客点数据格式错误，无法渲染。');
        console.error('Expected array for pickup points data, got:', points);
        return;
      }

      points.forEach(point => {
        const marker = new AMap.Marker({
          position: [point.center_lng, point.center_lat],
          map: this.map,
          title: `网格ID: ${point.grid_id}`,
          extData: { count: point.hotspot_count, predicted_count: point.predicted_hotspot_count }
        });
        this.pickupMarkers.push(marker);

        marker.on('click', () => {
          const infoWindow = new AMap.InfoWindow({
            content: `<div style='color:#333'><strong>网格ID: ${point.grid_id}</strong><br>热点计数: ${point.hotspot_count}<br>预测计数: ${point.predicted_hotspot_count}</div>`,
            offset: new AMap.Pixel(0, -30)
          });
          infoWindow.open(this.map, marker.getPosition());
        });
      });
      this.$message.success(`上客点数据可视化完成，共显示 ${this.pickupMarkers.length} 个点。`);
    },

    // 移除了运客行程分享数据加载和弹窗渲染的方法
    // async loadJnLucDataForChart() { ... }
    // renderChart() { ... }
    // clearChart() { ... }
    // getTripShareChartOption(data) { ... }

    // 清除所有地图覆盖物
    clearAllOverlays() {
      console.log('开始清除所有地图覆盖物...');
      if (this.heatmapOverlay && this.heatmapPluginReady) {
        this.heatmapOverlay.setDataSet({ data: [] });
        this.heatmapOverlay.hide();
        console.log('热力图数据已清除并隐藏。');
      } else {
        console.warn("未找到有效的热力图对象或热力图插件未准备就绪，跳过清除热力图。", this.heatmapOverlay);
      }

      this.pickupMarkers.forEach(marker => marker.setMap(null));
      this.pickupMarkers = [];
      console.log('上客点标记已清除。');

      this.vehicleMarkers.forEach(marker => marker.setMap(null)); // 即使不用，也确保清理
      this.vehicleMarkers = [];
      console.log('车辆标记已清除。');

      this.routeOverlays.forEach(overlay => {
        if (overlay && typeof overlay.setMap === 'function') overlay.setMap(null);
        if (overlay && typeof overlay.remove === 'function') overlay.remove();
      });
      this.routeOverlays = [];
      console.log('线路覆盖物已清除。');

      this.$message.info('所有地图覆盖物已清除。');
    },

    // 标签页点击事件处理
    handleTabClick(tab) {
      const clickedTabName = tab && tab.name ? tab.name : this.activeTab;
      console.log('标签页点击:', clickedTabName);

      this.clearAllOverlays();
      // 移除了关闭弹窗的逻辑
      // this.dialogVisible = false;

      if (clickedTabName === 'heatMap') {
        this.loadHeatmapData(); // 显示实时热力图
      } else if (clickedTabName === 'pickupQuery') {
        this.loadPickupPointsData(); // 显示上客点标记
      } else if (clickedTabName === 'heatPrediction') {
        this.loadPredictedHeatmapData(); // 显示预测热力图
      }
      // 移除了运客行程分享的逻辑
      // else if (clickedTabName === 'tripShare') {
      //   this.dialogTitle = '运客行程分享';
      //   this.chartType = 'tripShare';
      //   this.dialogVisible = true; // 打开弹窗
      //   this.loadJnLucDataForChart(); // 调用运客行程分享数据
      // }
    },
  }
};
</script>

<style scoped>
/* 样式与您原有样式保持一致 */
.big-data-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  color: white;
  background-color: #0f172a;
  overflow: hidden;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: rgba(15, 23, 42, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.back-button {
  background-color: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
}

.page-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 500;
}

.current-time {
  color: rgba(255, 255, 255, 0.8);
  font-family: monospace;
}

/* 修改导航选项卡样式 */
.function-tabs {
  background-color: rgba(15, 23, 42, 0.5);
  padding: 10px 20px 0;
}

/* 确保所有选项卡文字默认为白色 */
::v-deep .el-tabs__item {
  color: white !important;
  opacity: 0.9;
}

/* 选中状态样式 - 修改为蓝色文字 */
::v-deep .el-tabs__item.is-active {
  color: #165DFF !important; /* 使用与底栏按钮相同的蓝色 */
  opacity: 1;
  font-weight: bold;
  border-bottom: 2px solid #409eff;
}

.map-container {
  flex: 1;
  position: relative;
}

.map {
  width: 100%;
  height: 100%;
  background-color: #1a2035; /* 添加背景色，避免加载前空白 */
}

.search-box {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 300px;
  z-index: 100;
}

.search-input {
  background-color: rgba(255, 255, 255, 0.9);
}

::v-deep .search-input .el-input__inner {
  background-color: transparent;
  border: none;
  color: white;
}

::v-deep .search-input .el-input-group__append {
  background-color: rgba(255, 255, 255, 0.2);
  border: none;
}

::v-deep .search-input .el-button {
  color: white;
  background-color: transparent;
}
/* 移除了自定义弹窗样式，因为不再使用弹窗 */
</style>
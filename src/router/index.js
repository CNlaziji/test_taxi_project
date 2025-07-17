import { createRouter, createWebHistory } from 'vue-router';
import Register from '../views/Register.vue';
import Login from '../views/Login.vue';
import Home from '../views/Home.vue';
import BigDataService from '../views/BigDataService.vue';
import BestWaitingPoint from '../views/BigDataShow.vue'; // ✅ 已修正导入路径
import RankingIndex from '../views/RankingIndex.vue'

const routes = [
  { path: '/register', component: Register },
  { path: '/login', component: Login },
  { path: '/home', component: Home },
  { path: '/big-data', component: BigDataService },
  { path: '/best-waiting-point', component: BestWaitingPoint }, // 保持路由路径不变
  { path: '/', redirect: '/login' },
  {
    path: '/ranking',
    name: 'Ranking',
    component: RankingIndex
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';

createApp(App)
  .use(router)
  .use(ElementPlus)
  .mount('#app');

window._AMapSecurityConfig = {
  securityJsCode: '91e6fc5a83148b3d36b28883e6738d79', // 替换为您的安全密钥
};
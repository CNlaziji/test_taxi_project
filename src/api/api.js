import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    if (!config.url.startsWith('/auth/login') && !config.url.startsWith('/auth/register')) {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  error => Promise.reject(error)
);

// 响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    let message = '请求失败，请稍后重试';
    if (error.response) {
      switch (error.response.status) {
        case 400:
          message = error.response.data.message || '请求参数错误';
          break;
        case 401:
          message = '请登录后重试';
          localStorage.removeItem('token');
          window.location.href = '/login';
          break;
        case 409:
          message = '手机号已注册';
          break;
        case 429:
          message = '注册过于频繁，请稍后重试';
          break;
        case 500:
          message = '服务器内部错误，请稍后重试';
          break;
      }
    }
    return Promise.reject({ ...error, message });
  }
);

// 认证相关API
export const authAPI = {
  login: (phone, password) => api.post('/auth/login', {
    phone,
    password
  }),
  register: (phone, password) => api.post('/auth/register', {
    phone,
    password
  })
};

// 数据相关API
export const dataAPI = {
  getTripRecords: (limit = 15000) => api.get('/api/trip-records', {
    params: { limit }
  }),
  getGriddedHotspots: () => api.get('/api/gridded-hotspots'),
  getHotspots: () => api.get('/api/hotspots'),
  getJnTimeO15Min: () => api.get('/api/jn-time-o-15min'),
  getJnTimeO1Hour: () => api.get('/api/jn-time-o-1hour'),
  getJnONumber: () => api.get('/api/jn-o-number'),
  getJnLuc: () => api.get('/api/jn-luc'),
  getRideHailingIndex: () => api.get('/api/ride-hailing-index'),
  getCongestionIndex: () => api.get('/api/congestion-index')
};
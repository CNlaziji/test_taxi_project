<template>
  <div class="login-container">
    <!-- 返回按钮 - 已在左上角 -->
    <el-button @click="$router.go(-1)" class="back-button">返回</el-button>
    <!-- 添加logo -->
    <div class="logo-container">
      <img src="@/assets/logo3.jpg" alt="NOWAIT打车优化" class="logo">
    </div>
    <el-card class="login-card">
      <el-tabs v-model="activeTab" type="card">
        <el-tab-pane label="登录" name="login">
          <el-form ref="loginForm" :model="loginForm" :rules="rules" label-width="100px">
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="loginForm.phone" placeholder="请输入手机号"></el-input>
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="loginForm.password" :show-password="true" placeholder="请输入密码"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitForm('loginForm')" class="login-button">登录</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="注册" name="register">
          <el-button type="text" @click="$router.push('/register')">前往注册页面</el-button>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
// 导入登录API
import { authAPI } from '@/api/api';

export default {
  data() {
    return {
      activeTab: 'login',
      loginForm: {
        phone: '',
        password: ''
      },
      rules: {
        phone: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      },
      loading: false // 添加加载状态
    };
  },
  methods: {
    submitForm(formName) {
      this.$refs[formName].validate(async (valid) => {
        if (valid) {
          this.loading = true;
          try {
            // 调用登录API
            const response = await authAPI.login(
              this.loginForm.phone,
              this.loginForm.password
            );
            
            // 存储token
            localStorage.setItem('token', response.data.token);
            this.$message.success('登录成功');
            this.$router.push('/home');
          } catch (error) {
            // 错误处理
            const message = error.response?.data?.message || '登录失败，请检查账号密码';
            this.$message.error(message);
          } finally {
            this.loading = false;
          }
        } else {
          return false;
        }
      });
    }
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: url('@/assets/city-background.jpg') center/cover no-repeat fixed;
  padding: 20px;
  position: relative;
}

/* 添加半透明遮罩层增强文字可读性 */
.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7); /* 增加遮罩透明度以增强对比度 */
  z-index: 1;
}

/* 确保内容显示在遮罩上方 */
.login-container > * {
  position: relative;
  z-index: 2;
}

/* 返回按钮 */
.back-button {
  position: absolute;
  top: 20px;
  left: 20px;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white !important;
  padding: 8px 16px;
  border-radius: 5px;
  transition: all 0.3s ease;
}

.back-button:hover {
  background-color: white;
  color: #0f172a !important;
}

/* Logo容器 */
.logo-container {
  margin-bottom: 30px;
  text-align: center;
}

.logo {
  width: 330px; /* 从220px放大1.5倍至330px */
  height: auto;
}

/* 登录卡片 */
.login-card {
  width: 100%;
  max-width: 420px;
  background-color: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  padding: 40px;
}

/* 选项卡样式 */
.el-tabs__header {
  margin-bottom: 30px;
  border-bottom: 2px solid #3b82f6;
}

/* 选项卡样式 - 使用深度选择器确保样式穿透 */
/* 选项卡样式 - 文字居中并修改选中颜色 */
::v-deep .el-tabs__item {
  color: #ffffff !important; /* 未选中状态白色 */
  font-size: 16px;
  padding: 12px 20px; /* 增加内边距确保居中 */
  opacity: 1 !important;
  display: flex; /* 使用flex布局 */
  align-items: center; /* 垂直居中 */
  justify-content: center; /* 水平居中 */
  height: 100%; /* 占满父容器高度 */
}

::v-deep .el-tabs__item.is-active {
  color: #3b82f6 !important; /* 选中状态蓝色 */
  font-weight: bold;
  border-bottom: 2px solid #3b82f6;
}

/* 表单标签 - 增强选择器特异性确保白色显示 */
/* 使用深度选择器穿透scoped限制 */
::v-deep .login-card .el-form-item__label {
  color: #ffffff !important;
  font-weight: 500;
  text-shadow: none;
  opacity: 1;
  font-size: 14px;
}

/* 输入框容器 */
.el-input__wrapper {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  border-radius: 5px;
}

/* 输入框文本 */
.el-input__inner {
  color: white !important;
  background-color: transparent;
}

/* 占位符文本 */
::placeholder {
  color: white !important;
  opacity: 0.8;
}

/* 登录按钮 */
.login-button {
  width: 100%;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  height: 45px;
  font-size: 16px;
  color: white;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.login-button:hover {
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

/* 注册链接按钮 */
.login-card .el-button--text {
  color: white !important;
  text-decoration: underline;
}
</style>
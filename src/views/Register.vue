<template>
  <div class="register-container">
    <el-button @click="$router.go(-1)" class="back-button">返回</el-button>
    <div class="logo-container">
      <img src="@/assets/logo3.jpg" alt="NOWAIT打车优化" class="logo">
    </div>
    <el-card class="register-card">
      <h2 class="register-title">注册</h2>
      <el-form ref="registerForm" :model="registerForm" :rules="rules" label-width="100px">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="registerForm.phone" placeholder="请输入手机号"></el-input>
        </el-form-item>
        <el-form-item label="设置密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请设置密码"></el-input>
          <div v-if="passwordStrength" :class="['password-strength', passwordStrength]">
            密码强度: {{ passwordStrength === 'weak' ? '弱' : passwordStrength === 'medium' ? '中' : '强' }}
          </div>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请确认密码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="agreeTerms">我已阅读并同意<a href="/terms">用户协议</a>和<a href="/privacy">隐私政策</a></el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            @click="submitForm('registerForm')" 
            class="register-button" 
            :disabled="!agreeTerms || loading"
          >
            一键注册
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { authAPI } from '@/api/api';
import { ElLoading } from 'element-plus';

export default {
  data() {
    return {
      registerForm: {
        phone: '',
        password: '',
        confirmPassword: ''
      },
      passwordStrength: '',
      agreeTerms: false,
      loading: false,
      rules: {
        phone: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { validator: this.validatePhone, trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请设置密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { validator: this.validateConfirmPassword, trigger: 'blur' }
        ]
      }
    };
  },
  watch: {
    'registerForm.password'(newVal) {
      this.passwordStrength = this.checkPasswordStrength(newVal);
    }
  },
  methods: {
    validatePhone(rule, value, callback) {
      const phoneRegex = /^1[3-9]\d{9}$/;
      if (!phoneRegex.test(value)) {
        callback(new Error('请输入正确的手机号格式'));
      } else {
        callback();
      }
    },
    validateConfirmPassword(rule, value, callback) {
      if (value !== this.registerForm.password) {
        callback(new Error('两次密码输入不一致'));
      } else {
        callback();
      }
    },
    checkPasswordStrength(password) {
      if (password.length < 6) return '';
      let strength = 0;
      if (password.match(/[A-Z]/)) strength++;
      if (password.match(/[a-z]/)) strength++;
      if (password.match(/[0-9]/)) strength++;
      if (password.match(/[^A-Za-z0-9]/)) strength++;
      if (strength <= 1) return 'weak';
      else if (strength === 2 || strength === 3) return 'medium';
      else return 'strong';
    },
    async submitForm(formName) {
      if (!this.agreeTerms) {
        this.$message.error('请先同意用户协议和隐私政策');
        return;
      }
      this.$refs[formName].validate(async (valid) => {
        if (valid) {
          this.loading = true;
          const loading = ElLoading.service({ text: '正在注册...' });
          try {
            const response = await authAPI.register(
              this.registerForm.phone,
              this.registerForm.password
            );
            this.$message.success(response.data.message);
            this.$router.push('/login');
          } catch (error) {
            let message = '注册失败，请稍后重试';
            if (error.response) {
              switch (error.response.status) {
                case 400:
                  message = error.response.data.message || '请输入完整的注册信息';
                  break;
                case 409:
                  message = '手机号已注册，请直接登录';
                  break;
                case 429:
                  message = '注册过于频繁，请稍后重试';
                  break;
                case 500:
                  message = '服务器内部错误，请稍后重试';
                  break;
              }
            }
            this.$message.error(message);
          } finally {
            loading.close();
            this.loading = false;
          }
        }
      });
    }
  }
};
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: url('@/assets/city-background.jpg') center/cover no-repeat fixed;
  padding: 20px;
  position: relative;
}

.register-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1;
}

.register-container > * {
  position: relative;
  z-index: 2;
}

.back-button {
  position: absolute;
  top: 20px;
  left: 20px;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.logo-container {
  margin-bottom: 30px;
  text-align: center;
}

.logo {
  width: 330px;
  height: auto;
}

.register-card {
  width: 100%;
  max-width: 420px;
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(8px);
  padding: 30px;
}

.register-title {
  color: white;
  text-align: center;
  margin-bottom: 25px;
  font-size: 22px;
}

::v-deep .register-card .el-form-item__label {
  color: #ffffff !important;
  font-weight: 500;
  text-shadow: none;
  opacity: 1;
  font-size: 14px;
}

.el-input__wrapper {
  background-color: rgba(255, 255, 255, 0.07);
  border-color: rgba(255, 255, 255, 0.15);
}

.el-input__inner {
  color: white !important;
  placeholder-color: rgba(255, 255, 255, 0.4);
}

.register-button {
  width: 100%;
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  border: none;
  height: 45px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.register-button:hover {
  background: linear-gradient(135deg, #4da6ff 0%, #3498db 100%);
  transform: translateY(-2px);
}

.password-strength {
  color: white;
  font-size: 12px;
  margin-top: 5px;
}
.password-strength.weak { color: #ff4d4f; }
.password-strength.medium { color: #faad14; }
.password-strength.strong { color: #52c41a; }
</style>
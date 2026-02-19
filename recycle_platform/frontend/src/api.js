import axios from 'axios'

// 动态获取API地址
// 生产环境：使用当前域名 + /api
// 开发环境：使用环境变量或 localhost:8000
const getBaseURL = () => {
  // 如果设置了环境变量，优先使用
  if (import.meta.env.VITE_API_BASE) {
    return import.meta.env.VITE_API_BASE
  }
  
  // 生产环境（打包后）：使用相对路径
  if (import.meta.env.PROD) {
    return '/api'
  }
  
  // 开发环境：使用 localhost
  return 'http://localhost:8000/api'
}

export const api = axios.create({
  baseURL: getBaseURL()
})

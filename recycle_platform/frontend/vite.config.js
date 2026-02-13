import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    cors: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          'echarts': ['echarts'],
          'vue': ['vue'],
          'axios': ['axios'],
        }
      }
    }
  },
  preview: {
    port: 5173,
    host: '0.0.0.0'
  }
})

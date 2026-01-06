import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  
  // Tauri 使用本地协议，需要特殊配置
  clearScreen: false,
  server: {
    strictPort: true,
    port: 5173,
  },
  
  envPrefix: ['VITE_', 'TAURI_'],
  
  build: {
    target: ['es2021', 'chrome100', 'safari13'],
    minify: !process.env.TAURI_DEBUG ? 'esbuild' : false,
    sourcemap: !!process.env.TAURI_DEBUG,
  },
})

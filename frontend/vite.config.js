import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 3000,
    host: 'localhost',
    open: true
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})

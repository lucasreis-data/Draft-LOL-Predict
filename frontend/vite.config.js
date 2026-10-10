import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Em dev, o front chama '/draft' (mesma origem, como na nuvem via CloudFront)
    // e o Vite repassa para o Java local.
    proxy: {
      '/draft': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
})

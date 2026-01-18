// frontend/vite.config.js
/* Vite provides Hot Module Replacement (HMR) - instant updates during development,
* Fast builds for production, ES module support out of the box 
*/
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
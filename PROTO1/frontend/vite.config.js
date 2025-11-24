// Config Vite minimaliste.
// Vite a besoin de fichier pour activer le plugin React et configurer l’origine API si besoin.

// Chemin d'accès:
// frontend/vite.config.js

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
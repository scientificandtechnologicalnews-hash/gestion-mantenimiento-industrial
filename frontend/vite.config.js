import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const django = 'http://127.0.0.1:8000'

// Todo lo que sea de Django se reenvía al servidor de Django (solo en desarrollo)
const rutasDjango = [
  '/api', '/cuentas', '/admin', '/panel', '/maquinas',
  '/documentos', '/incidencias', '/static', '/media',
]

// Ahora defineConfig recibe una función: "command" vale 'serve' cuando haces
// npm run dev y 'build' cuando haces npm run build.
export default defineConfig(({ command }) => ({
  // Desarrollo: React vive en /app/. Compilado: sus archivos los sirve Django en /static/app/.
  base: command === 'build' ? '/static/app/' : '/app/',
  plugins: [react()],
  server: {
    // Sin "changeOrigin: true", para no romper el login por CSRF
    proxy: Object.fromEntries(rutasDjango.map((ruta) => [ruta, django])),
  },
}))




import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const django = 'http://127.0.0.1:8000'

// Todo lo que sea de Django se reenvía al servidor de Django
const rutasDjango = [
  '/api', '/cuentas', '/admin', '/panel', '/maquinas',
  '/documentos', '/incidencias', '/static', '/media',
]

export default defineConfig({
  // React vivirá en /app/. Así no choca con la portada "/" de Django.
  base: '/app/',
  plugins: [react()],
  server: {
    // Genera { '/api': 'http://127.0.0.1:8000', '/cuentas': ..., ... }
    // OJO: no añadas "changeOrigin: true". Cambiaría la cabecera Host y
    // Django rechazaría el login por la protección CSRF.
    proxy: Object.fromEntries(rutasDjango.map((ruta) => [ruta, django])),
  },
})


// Error propio que conserva el código HTTP (403, 404, 500...)
export class ApiError extends Error {
  constructor(status) {
    super(`Error ${status}`)
    this.status = status
  }
}

// Pide datos a la API de Django. "path" empieza por "/" (ej: "/estadisticas/").
export async function apiGet(path, signal) {
  const respuesta = await fetch(`/api${path}`, {
    credentials: 'same-origin',   // envía la cookie de sesión de Django
    headers: { Accept: 'application/json' },
    signal,                       // permite cancelar la petición
  })
  if (!respuesta.ok) {
    throw new ApiError(respuesta.status)
  }
  return respuesta.json()
}
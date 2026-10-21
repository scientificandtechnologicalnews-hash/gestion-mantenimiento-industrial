import { useEffect, useState } from 'react'
import { apiGet } from './api'

// Hook que pide datos a la API cada vez que cambia "path".
// Devuelve { data, error, loading }.
export function useApi(path) {
  // Guardamos también el path al que pertenece el resultado,
  // para saber si el dato que tenemos ya está desactualizado.
  const [resultado, setResultado] = useState({ path: null, data: null, error: null })

  useEffect(() => {
    // AbortController cancela la petición anterior si el path cambia
    // antes de que termine (evita que una respuesta lenta pise a una nueva).
    const controlador = new AbortController()

    apiGet(path, controlador.signal)
      .then((data) => setResultado({ path, data, error: null }))
      .catch((error) => {
        if (error.name !== 'AbortError') {
          setResultado({ path, data: null, error })
        }
      })

    // Función de limpieza: React la ejecuta antes de repetir el efecto
    return () => controlador.abort()
  }, [path])

  const loading = resultado.path !== path
  return {
    data: loading ? null : resultado.data,
    error: loading ? null : resultado.error,
    loading,
  }
}

// Hook que "retrasa" un valor: mientras el usuario escribe, no cambia.
// Así no lanzamos una petición por cada tecla pulsada.
export function useDebounce(valor, retraso = 400) {
  const [valorRetrasado, setValorRetrasado] = useState(valor)

  useEffect(() => {
    const temporizador = setTimeout(() => setValorRetrasado(valor), retraso)
    return () => clearTimeout(temporizador)   // reinicia la cuenta si el valor cambia
  }, [valor, retraso])

  return valorRetrasado
}
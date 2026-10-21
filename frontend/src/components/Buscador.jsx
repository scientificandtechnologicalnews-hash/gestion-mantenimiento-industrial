import { useState } from 'react'
import { useApi, useDebounce } from '../hooks'
import DocumentoDetalle from './DocumentoDetalle'
import Estado from './Estado'

const TIPOS = [
  ['', 'Todos los tipos'],
  ['FP', 'Fallo y solución'],
  ['MT', 'Manual técnico'],
  ['EE', 'Esquema eléctrico'],
]
const TAMANO_PAGINA = 10   // debe coincidir con PAGE_SIZE de Django

export default function Buscador() {
  // Un useState por cada cosa que puede cambiar en pantalla
  const [q, setQ] = useState('')
  const [tipo, setTipo] = useState('')
  const [pagina, setPagina] = useState(1)
  const [seleccionado, setSeleccionado] = useState(null)

  // Esperamos a que el usuario deje de escribir antes de consultar la API
  const qDiferida = useDebounce(q.trim())

  // Construimos la URL con sus parámetros (?page=1&q=sensor&tipo=FP)
  const params = new URLSearchParams({ page: pagina })
  if (qDiferida) params.set('q', qDiferida)
  if (tipo) params.set('tipo', tipo)

  const { data, error, loading } = useApi(`/documentos/?${params}`)

  // Al cambiar un filtro, volvemos a la página 1
  function cambiarBusqueda(e) {
    setQ(e.target.value)
    setPagina(1)
  }
  function cambiarTipo(e) {
    setTipo(e.target.value)
    setPagina(1)
  }

  return (
    <div className="buscador">
      <div>
        <div className="filtros">
          <input
            type="search"
            value={q}
            onChange={cambiarBusqueda}
            placeholder="Buscar fallos, manuales, esquemas…"
          />
          <select value={tipo} onChange={cambiarTipo}>
            {TIPOS.map(([valor, texto]) => (
              <option key={valor} value={valor}>{texto}</option>
            ))}
          </select>
        </div>

        <Estado loading={loading} error={error}>
          {data && (
            <>
              <p className="meta">{data.count} documentos encontrados</p>
              <ul className="resultados">
                {data.results.map((d) => (
                  // "key" ayuda a React a identificar cada elemento de la lista
                  <li key={d.id}>
                    <button className="enlace" onClick={() => setSeleccionado(d.id)}>
                      {d.titulo}
                    </button>
                    <div className="meta">{d.tipo_display} · {d.maquina_codigo}</div>
                    <div>{d.extracto}…</div>
                  </li>
                ))}
              </ul>

              {data.count > TAMANO_PAGINA && (
                <p className="paginacion">
                  <button disabled={!data.previous} onClick={() => setPagina(pagina - 1)}>
                    ← Anterior
                  </button>
                  Página {pagina} de {Math.ceil(data.count / TAMANO_PAGINA)}
                  <button disabled={!data.next} onClick={() => setPagina(pagina + 1)}>
                    Siguiente →
                  </button>
                </p>
              )}
            </>
          )}
        </Estado>
      </div>

      {/* Renderizado condicional: el detalle solo existe si hay un documento seleccionado */}
      {seleccionado && (
        <DocumentoDetalle id={seleccionado} onCerrar={() => setSeleccionado(null)} />
      )}
    </div>
  )
}

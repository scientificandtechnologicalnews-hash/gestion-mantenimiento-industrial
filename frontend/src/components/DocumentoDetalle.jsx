import { useApi } from '../hooks'
import Estado from './Estado'

export default function DocumentoDetalle({ id, onCerrar }) {
  const { data, error, loading } = useApi(`/documentos/${id}/`)

  return (
    <aside className="detalle">
      <button onClick={onCerrar}>Cerrar</button>
      <Estado loading={loading} error={error}>
        {data && (
          <>
            <h3>{data.titulo}</h3>
            <p className="meta">
              {data.tipo_display} · {data.maquina_codigo} · Actualizado el{' '}
              {new Date(data.fecha_actualizacion).toLocaleDateString('es-ES')}
            </p>
            {/* React escapa el texto automáticamente (protección XSS).
                Por eso NO usamos dangerouslySetInnerHTML.
                "pre-wrap" respeta los saltos de línea del documento. */}
            <p style={{ whiteSpace: 'pre-wrap' }}>{data.contenido}</p>
          </>
        )}
      </Estado>
    </aside>
  )
}

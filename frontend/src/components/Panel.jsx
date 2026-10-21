import { useApi } from '../hooks'
import Estado from './Estado'

// Componente pequeño reutilizable. Recibe sus datos por props.
function Tarjeta({ titulo, valor }) {
  return (
    <div className="tarjeta">
      <div className="tarjeta-valor">{valor}</div>
      <div>{titulo}</div>
    </div>
  )
}

export default function Panel() {
  const { data, error, loading } = useApi('/estadisticas/')

  return (
    <Estado loading={loading} error={error}>
      {data && (
        <>
          <div className="tarjetas">
            <Tarjeta titulo="Máquinas activas" valor={data.total_maquinas} />
            <Tarjeta titulo="Documentos" valor={data.total_documentos} />
            <Tarjeta titulo="Incidencias" valor={data.total_incidencias} />
            <Tarjeta
              titulo="Horas medias de resolución"
              valor={data.horas_medias_resolucion ?? '—'}
            />
          </div>

          <h2>Incidencias por estado</h2>
          {(() => {
            // Mayor valor, para calcular el ancho de cada barra (mínimo 1 para no dividir por 0)
            const maximo = Math.max(1, ...data.incidencias_por_estado.map((e) => e.total))
            return data.incidencias_por_estado.map((e) => (
              <div key={e.estado} className="fila-barra">
                <span className="etiqueta">{e.etiqueta}</span>
                <div className="barra" style={{ width: `${(e.total / maximo) * 100}%` }} />
                <span>{e.total}</span>
              </div>
            ))
          })()}

          <h2>Máquinas con más incidencias</h2>
          {data.maquinas_con_mas_incidencias.length === 0 ? (
            <p>Todavía no hay incidencias registradas.</p>
          ) : (
            <table>
              <thead>
                <tr><th>Código</th><th>Máquina</th><th>Incidencias</th></tr>
              </thead>
              <tbody>
                {data.maquinas_con_mas_incidencias.map((m) => (
                  <tr key={m.codigo}>
                    <td>{m.codigo}</td>
                    <td>{m.nombre}</td>
                    <td>{m.total}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </Estado>
  )
}

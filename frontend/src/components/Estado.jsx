export default function Estado({ loading, error, children }) {
  if (loading) return <p className="aviso">Cargando…</p>

  if (error) {
    // La API devuelve 403 si no hay sesión o falta el permiso
    if (error.status === 403) {
      return (
        <p className="aviso error">
          No tienes acceso a estos datos.{' '}
          <a href="/cuentas/login/?next=/app/">Inicia sesión</a> con un usuario con permisos.
        </p>
      )
    }
    return (
      <p className="aviso error">
        No se pudieron cargar los datos ({error.status ?? 'sin conexión'}).
      </p>
    )
  }

  return children
}
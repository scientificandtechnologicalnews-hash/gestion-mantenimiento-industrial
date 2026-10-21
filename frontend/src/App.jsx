import { useState } from 'react'
import Buscador from './components/Buscador'
import Panel from './components/Panel'

export default function App() {
  // Pestaña activa: "buscador" o "panel"
  const [vista, setVista] = useState('buscador')

  return (
    <div className="app">
      <header className="cabecera">
        <h1>Mantenimiento Industrial</h1>
        <nav>
          <button
            className={vista === 'buscador' ? 'activa' : ''}
            onClick={() => setVista('buscador')}
          >
            Buscador técnico
          </button>
          <button
            className={vista === 'panel' ? 'activa' : ''}
            onClick={() => setVista('panel')}
          >
            Panel de indicadores
          </button>
          {/* Enlace normal (recarga la página) hacia la parte Django */}
          <a href="/maquinas/">Volver a la web</a>
        </nav>
      </header>

      {vista === 'buscador' ? <Buscador /> : <Panel />}
    </div>
  )
}
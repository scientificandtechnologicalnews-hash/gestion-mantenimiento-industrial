# 1. Definición del problema, nuevo proyecto

## Contexto
La aplicación está pensada para centros logísticos y empresas con maquinaria
industrial: motores, PLC, sensores, transportadores, robots, variadores,
lectores de códigos y sistemas de visión artificial.

## Carencias detectadas
- Los manuales técnicos y esquemas están dispersos en distintos formatos y lugares.
- Los técnicos tardan en encontrar la solución a una avería.
- El conocimiento queda en la cabeza de las personas con más experiencia
  y se pierde cuando estas se van.
- Las paradas de máquina se alargan por falta de información rápida.

## Impacto
- Mayor tiempo de parada de la línea.
- Aumento de costes de producción y de mantenimiento.
- Dependencia de unas pocas personas expertas.

## Solución propuesta
Aplicación web de gestión de mantenimiento con una base de conocimiento por
máquina. Cada máquina tiene documentos (fallos y soluciones, manuales técnicos
y esquemas eléctricos) que los técnicos consultan, y sobre los que registran
incidencias.

## Tipos de usuario
| Rol | Acciones permitidas |
|---|---|
| Administrador | Gestionar máquinas, documentos y usuarios |
| Técnico de mantenimiento | Consultar documentos y registrar incidencias |
| Visitante | Ver información pública, sin editar |

## Alcance del MVP (versión mínima)
- Listado y detalle de máquinas.
- Documentos asociados a cada máquina, con buscador.
- Registro de incidencias por técnicos.
- Login y permisos por rol.
- Dos vistas en React que consumen datos de la API.
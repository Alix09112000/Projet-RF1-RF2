import type { ReactElement } from 'react'
import type { Role } from './api/client'
import Import from './pages/Import'
import Parametres from './pages/Parametres'
import Placeholder from './pages/Placeholder'
import Saisie from './pages/Saisie'
import Users from './pages/Users'

export interface NavItem {
  path: string
  label: string
  roles: Role[]
  element: ReactElement
}

const ALL: Role[] = ['contributor', 'controller', 'viewer', 'admin']

export const NAV: NavItem[] = [
  {
    path: 'saisie',
    label: 'Saisie des hypothèses',
    roles: ALL,
    element: <Saisie />,
  },
  {
    path: 'tableau-de-bord',
    label: 'Tableau de bord',
    roles: ALL,
    element: (
      <Placeholder
        title="Tableau de bord"
        sprint="Sprint 5"
        text="Écarts RF2 / RF1 par segment, commentaires générés et validation par le contrôle de gestion."
      />
    ),
  },
  {
    path: 'import',
    label: 'Import des données',
    roles: ['controller', 'admin'],
    element: <Import />,
  },
  {
    path: 'parametres',
    label: 'Paramètres',
    roles: ALL,
    element: <Parametres />,
  },
  {
    path: 'historique',
    label: 'Historique',
    roles: ALL,
    element: (
      <Placeholder
        title="Historique"
        sprint="Sprint 3"
        text="Toutes les saisies, changements de paramètres, dépôts de fichiers et validations."
      />
    ),
  },
  { path: 'utilisateurs', label: 'Utilisateurs', roles: ['admin'], element: <Users /> },
]

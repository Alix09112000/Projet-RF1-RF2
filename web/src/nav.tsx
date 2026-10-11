import type { ReactElement } from 'react'
import type { Role } from './api/client'
import Import from './pages/Import'
import Placeholder from './pages/Placeholder'
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
    roles: ['contributor', 'controller', 'admin'],
    element: (
      <Placeholder
        title="Saisie des hypothèses"
        sprint="Sprint 2"
        text="Saisie par segment et par direction, contrôles de plage, justification et historique de chaque valeur."
      />
    ),
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
    roles: ['controller', 'admin'],
    element: (
      <Placeholder
        title="Paramètres du modèle"
        sprint="Sprint 2"
        text="Taux de change, barèmes et seuil d'écart significatif, appliqués à tout le modèle."
      />
    ),
  },
  {
    path: 'historique',
    label: 'Historique',
    roles: ALL,
    element: (
      <Placeholder
        title="Historique"
        sprint="Sprint 2"
        text="Toutes les saisies, changements de paramètres, dépôts de fichiers et validations."
      />
    ),
  },
  { path: 'utilisateurs', label: 'Utilisateurs', roles: ['admin'], element: <Users /> },
]

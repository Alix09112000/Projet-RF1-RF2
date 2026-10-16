import type { Role } from './api/client'

export const ROLE_LABEL: Record<Role, string> = {
  contributor: 'Contributeur',
  controller: 'Contrôle de gestion',
  viewer: 'Consultation',
  admin: 'Administrateur',
}

export function homeFor(role: Role): string {
  if (role === 'contributor') return '/saisie'
  if (role === 'admin') return '/utilisateurs'
  return '/tableau-de-bord'
}

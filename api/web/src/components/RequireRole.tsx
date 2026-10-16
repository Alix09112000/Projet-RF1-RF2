import type { ReactNode } from 'react'
import type { Role } from '../api/client'
import { useMe } from '../auth'

export default function RequireRole({ roles, children }: { roles: Role[]; children: ReactNode }) {
  const me = useMe()
  if (!me.data) return null
  if (!roles.includes(me.data.role)) {
    return (
      <div className="page">
        <h1>Accès réservé</h1>
        <p className="muted">Votre rôle ne permet pas d'ouvrir cette page.</p>
      </div>
    )
  }
  return <>{children}</>
}

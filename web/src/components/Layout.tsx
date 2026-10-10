import { useQueryClient } from '@tanstack/react-query'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { api, type User } from '../api/client'
import { NAV } from '../nav'
import { ROLE_LABEL } from '../roles'

export default function Layout({ user }: { user: User }) {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const items = NAV.filter((item) => item.roles.includes(user.role))

  async function logout() {
    await api<void>('/auth/logout', { method: 'POST' })
    queryClient.clear()
    queryClient.setQueryData(['me'], null)
    navigate('/connexion', { replace: true })
  }

  return (
    <div className="shell">
      <aside className="side">
        <div className="brand">
          <span>CANAL</span>
          <span className="brand-box">BOX</span>
          <span className="brand-rf">RF</span>
        </div>
        <nav className="nav">
          {items.map((item) => (
            <NavLink
              key={item.path}
              to={`/${item.path}`}
              className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="me">
          <div className="me-card">
            <div className="me-name">{user.full_name}</div>
            <div className="me-role">{ROLE_LABEL[user.role]}</div>
          </div>
          <button className="btn-dark-ghost" onClick={logout}>
            Se déconnecter
          </button>
        </div>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}

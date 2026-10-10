import { Navigate, Route, Routes } from 'react-router-dom'
import { useMe } from './auth'
import Layout from './components/Layout'
import RequireRole from './components/RequireRole'
import { NAV } from './nav'
import Login from './pages/Login'
import { homeFor } from './roles'

function Protected() {
  const me = useMe()
  if (me.isPending) return <div className="splash">Chargement…</div>
  if (me.isError) return <div className="splash">Le serveur ne répond pas. Réessayez dans un instant.</div>
  if (!me.data) return <Navigate to="/connexion" replace />
  return <Layout user={me.data} />
}

function Home() {
  const me = useMe()
  return me.data ? <Navigate to={homeFor(me.data.role)} replace /> : null
}

export default function App() {
  return (
    <Routes>
      <Route path="/connexion" element={<Login />} />
      <Route element={<Protected />}>
        <Route index element={<Home />} />
        {NAV.map((item) => (
          <Route
            key={item.path}
            path={item.path}
            element={<RequireRole roles={item.roles}>{item.element}</RequireRole>}
          />
        ))}
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

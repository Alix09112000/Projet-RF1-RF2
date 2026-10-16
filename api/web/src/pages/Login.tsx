import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, type User } from '../api/client'
import { homeFor } from '../roles'

export default function Login() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const login = useMutation({
    mutationFn: () =>
      api<User>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
    onSuccess: (user) => {
      queryClient.setQueryData(['me'], user)
      navigate(homeFor(user.role), { replace: true })
    },
  })

  function submit(event: FormEvent) {
    event.preventDefault()
    login.mutate()
  }

  return (
    <div className="login">
      <section className="login-left">
        <div className="brand brand-lg">
          <span>CANAL</span>
          <span className="brand-box">BOX</span>
          <span className="brand-country">CÔTE D'IVOIRE</span>
        </div>
        <div>
          <h1 className="login-title">Outil budget RF1 / RF2</h1>
          <p className="login-lead">
            Saisie des hypothèses, recalcul du modèle et commentaires d'écart, pour Abidjan.
          </p>
        </div>
      </section>
      <section className="login-right">
        <form className="card login-card" onSubmit={submit}>
          <h2>Connexion</h2>
          <p className="muted">Identifiez-vous avec le compte qui vous a été attribué.</p>
          <label className="field">
            <span>Identifiant</span>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="username"
              required
            />
          </label>
          <label className="field">
            <span>Mot de passe</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </label>
          {login.isError && <div className="error">{login.error.message}</div>}
          <button className="btn-primary btn-block" disabled={login.isPending}>
            {login.isPending ? 'Connexion…' : 'Se connecter'}
          </button>
          <p className="hint">Comptes administrés par le contrôle de gestion.</p>
        </form>
      </section>
    </div>
  )
}

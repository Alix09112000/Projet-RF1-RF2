import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, type ChangeEvent, type FormEvent } from 'react'
import { api, type Role, type User } from '../api/client'
import { ROLE_LABEL } from '../roles'

const ROLES: Role[] = ['contributor', 'controller', 'viewer', 'admin']
const EMPTY = { email: '', full_name: '', role: 'contributor' as Role, direction: '', password: '' }

export default function Users() {
  const queryClient = useQueryClient()
  const users = useQuery({ queryKey: ['users'], queryFn: () => api<User[]>('/users') })
  const [form, setForm] = useState(EMPTY)

  const create = useMutation({
    mutationFn: () =>
      api<User>('/users', {
        method: 'POST',
        body: JSON.stringify({ ...form, direction: form.direction.trim() || null }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      setForm(EMPTY)
    },
  })

  const set =
    (key: keyof typeof EMPTY) => (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm({ ...form, [key]: e.target.value })

  function submit(event: FormEvent) {
    event.preventDefault()
    create.mutate()
  }

  return (
    <div className="page">
      <h1>Utilisateurs</h1>
      <div className="grid-2">
        <div className="card">
          <h2>Comptes</h2>
          {users.isPending && <p className="muted">Chargement…</p>}
          {users.isError && <div className="error">{users.error.message}</div>}
          {users.data && (
            <table className="table">
              <thead>
                <tr>
                  <th>Nom</th>
                  <th>Identifiant</th>
                  <th>Rôle</th>
                  <th>Direction</th>
                </tr>
              </thead>
              <tbody>
                {users.data.map((u) => (
                  <tr key={u.id}>
                    <td>{u.full_name}</td>
                    <td>{u.email}</td>
                    <td>
                      <span className="tag">{ROLE_LABEL[u.role]}</span>
                    </td>
                    <td>{u.direction ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <form className="card" onSubmit={submit}>
          <h2>Créer un compte</h2>
          <label className="field">
            <span>Nom complet</span>
            <input value={form.full_name} onChange={set('full_name')} required />
          </label>
          <label className="field">
            <span>Identifiant</span>
            <input value={form.email} onChange={set('email')} placeholder="prenom.nom@canalbox.ci" required />
          </label>
          <label className="field">
            <span>Rôle</span>
            <select value={form.role} onChange={set('role')}>
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {ROLE_LABEL[r]}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Direction</span>
            <input value={form.direction} onChange={set('direction')} placeholder="Direction Commerciale" />
          </label>
          <label className="field">
            <span>Mot de passe provisoire (10 caractères minimum)</span>
            <input type="password" value={form.password} onChange={set('password')} minLength={10} required />
          </label>
          {create.isError && <div className="error">{create.error.message}</div>}
          {create.isSuccess && <div className="success">Compte créé.</div>}
          <button className="btn-primary" disabled={create.isPending}>
            {create.isPending ? 'Création…' : 'Créer le compte'}
          </button>
        </form>
      </div>
    </div>
  )
}

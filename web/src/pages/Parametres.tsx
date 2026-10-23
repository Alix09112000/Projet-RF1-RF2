import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useMe } from '../auth'

interface Choice {
  entity: string
  country: string
  city: string
  source_row: number
}

interface Parameters {
  values: { legal_entity: string | null; city: string | null }
  reference_month: string
  labels: Record<string, string>
  choices: Choice[]
}

export default function Parametres() {
  const queryClient = useQueryClient()
  const me = useMe()
  const data = useQuery({ queryKey: ['parameters'], queryFn: () => api<Parameters>('/parameters') })
  const [entity, setEntity] = useState('')
  const [city, setCity] = useState('')
  const [reference, setReference] = useState('')
  const canEdit = me.data?.role === 'controller' || me.data?.role === 'admin'

  useEffect(() => {
    if (data.data) {
      setEntity(data.data.values.legal_entity ?? '')
      setCity(data.data.values.city ?? '')
      setReference(data.data.reference_month)
    }
  }, [data.data])

  const save = useMutation({
    mutationFn: () =>
      api('/parameters', { method: 'PUT', body: JSON.stringify({ legal_entity: entity, city, reference_month: reference || null }) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['parameters'] }),
  })

  const entities = [...new Set(data.data?.choices.map((c) => c.entity) ?? [])]
  const cities = data.data?.choices.filter((c) => c.entity === entity) ?? []

  return (
    <div className="page">
      <h1>Paramètres</h1>
      {data.isPending && <p className="muted">Chargement…</p>}
      {data.isError && <div className="error">{data.error.message}</div>}
      {data.data && (
        <div className="grid-2">
          <form
            className="card"
            onSubmit={(e) => {
              e.preventDefault()
              save.mutate()
            }}
          >
            <h2>Ville du modèle</h2>
            <p className="muted">Repris des cellules D5 et D6 de DROPE1. Les choix viennent de la table List.</p>
            <label className="field">
              <span>{data.data.labels.legal_entity}</span>
              <select
                value={entity}
                disabled={!canEdit}
                onChange={(e) => {
                  setEntity(e.target.value)
                  setCity('')
                }}
              >
                <option value="">—</option>
                {entities.map((x) => (
                  <option key={x} value={x}>{x}</option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>{data.data.labels.city}</span>
              <select value={city} disabled={!canEdit} onChange={(e) => setCity(e.target.value)}>
                <option value="">—</option>
                {cities.map((c) => (
                  <option key={c.city} value={c.city}>{c.city}</option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Mois en cours (mois de référence)</span>
              <input type="month" value={reference} disabled={!canEdit} onChange={(e) => setReference(e.target.value)} />
            </label>
            <p className="muted">
              Le mois précédent est le dernier mois réel : en août, janvier à juillet sont réels et tout le reste est
              prévision. L’exercice commence en janvier.
            </p>
            {save.isError && <div className="error">{save.error.message}</div>}
            {save.isSuccess && <div className="success">Paramètres enregistrés.</div>}
            {canEdit && (
              <button className="btn-primary" disabled={!entity || !city || save.isPending}>
                Enregistrer
              </button>
            )}
          </form>

          <div className="card">
            <h2>Table List</h2>
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr><th>Ligne</th><th>Entité légale</th><th>Pays</th><th>Ville</th></tr>
                </thead>
                <tbody>
                  {data.data.choices.map((c) => (
                    <tr key={c.source_row}>
                      <td className="muted">{c.source_row}</td>
                      <td>{c.entity}</td>
                      <td>{c.country}</td>
                      <td>{c.city}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

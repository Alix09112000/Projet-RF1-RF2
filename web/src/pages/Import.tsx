import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useRef, useState, type FormEvent } from 'react'
import { api } from '../api/client'

type Kind = 'commercial' | 'echus'
type Status = 'pending' | 'accepted' | 'rejected' | 'cancelled'

interface Issue {
  message: string
  line: number | null
  column: string | null
}

interface Batch {
  id: number
  kind: Kind
  status: Status
  filename: string
  uploaded_at: string
  uploaded_by: string
  rows_read: number
  rows_kept: number
  rows_ignored: number
  months: string[]
  errors: Issue[]
  warnings: Issue[]
  warnings_confirmed: boolean
  decided_at: string | null
}

const SOURCES: { kind: Kind; title: string; text: string }[] = [
  {
    kind: 'commercial',
    title: 'Réalisés commerciaux',
    text: 'Ventes, parc et réabonnements. Une ligne par mois, 34 colonnes, comme l’onglet « Source BR PBI ».',
  },
  {
    kind: 'echus',
    title: 'Échus',
    text: 'Une ligne par mois et par ancienneté, 4 colonnes. Le format croisé actuel est accepté si vous indiquez l’année.',
  },
]

const KIND_LABEL: Record<Kind, string> = { commercial: 'Réalisés commerciaux', echus: 'Échus' }
const STATUS_LABEL: Record<Status, string> = {
  pending: 'En attente',
  accepted: 'Importé',
  rejected: 'Refusé',
  cancelled: 'Annulé',
}

const monthFormat = new Intl.DateTimeFormat('fr-FR', { month: 'long', year: 'numeric' })
const dateFormat = new Intl.DateTimeFormat('fr-FR', { dateStyle: 'short', timeStyle: 'short' })

function monthLabel(iso: string) {
  return monthFormat.format(new Date(`${iso}T00:00:00`))
}

function monthRange(months: string[]) {
  if (months.length === 0) return '—'
  if (months.length === 1) return monthLabel(months[0])
  return `${monthLabel(months[0])} → ${monthLabel(months[months.length - 1])}`
}

function plural(n: number, word: string) {
  return `${n.toLocaleString('fr-FR')} ${word}${n > 1 ? 's' : ''}`
}

export default function Import() {
  const history = useQuery({ queryKey: ['imports'], queryFn: () => api<Batch[]>('/imports') })

  return (
    <div className="page">
      <h1>Import des données</h1>
      <p className="muted lead">
        Déposez chaque mois les deux fichiers. L’outil vérifie leur structure et leur contenu, puis vous
        demande de confirmer avant d’enregistrer quoi que ce soit.
      </p>

      <div className="grid-2">
        {SOURCES.map((source) => (
          <UploadCard key={source.kind} {...source} />
        ))}
      </div>

      <section className="card section">
        <h2>Historique des dépôts</h2>
        {history.isPending && <p className="muted">Chargement…</p>}
        {history.isError && <div className="error">{history.error.message}</div>}
        {history.data?.length === 0 && <p className="muted">Aucun dépôt pour l’instant.</p>}
        {history.data && history.data.length > 0 && (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Fichier</th>
                  <th>Type</th>
                  <th>Déposé par</th>
                  <th>Lignes</th>
                  <th>Mois</th>
                  <th>Statut</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {history.data.map((b) => (
                  <tr key={b.id}>
                    <td>{dateFormat.format(new Date(b.uploaded_at))}</td>
                    <td>{b.filename}</td>
                    <td>{KIND_LABEL[b.kind]}</td>
                    <td>{b.uploaded_by}</td>
                    <td>{b.rows_kept.toLocaleString('fr-FR')}</td>
                    <td>{monthRange(b.months)}</td>
                    <td>
                      <span className={`tag tag-${b.status}`}>{STATUS_LABEL[b.status]}</span>
                      {b.warnings_confirmed && <div className="hint-sm">avertissements confirmés</div>}
                    </td>
                    <td>
                      <a href={`/api/imports/${b.id}/file`}>Original</a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}

function UploadCard({ kind, title, text }: { kind: Kind; title: string; text: string }) {
  const queryClient = useQueryClient()
  const input = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [year, setYear] = useState('')
  const [batch, setBatch] = useState<Batch | null>(null)
  const [ack, setAck] = useState(false)
  const [done, setDone] = useState<Batch | null>(null)

  const refresh = () => queryClient.invalidateQueries({ queryKey: ['imports'] })

  const check = useMutation({
    mutationFn: () => {
      const body = new FormData()
      body.append('file', file as File)
      if (year.trim()) body.append('year', year.trim())
      return api<Batch>(`/imports/${kind}/preview`, { method: 'POST', body })
    },
    onSuccess: (result) => {
      setBatch(result)
      setAck(false)
      setDone(null)
      refresh()
    },
  })

  const confirm = useMutation({
    mutationFn: (b: Batch) =>
      api<Batch>(`/imports/${b.id}/confirm`, {
        method: 'POST',
        body: JSON.stringify({ confirm_warnings: ack }),
      }),
    onSuccess: (result) => {
      setDone(result)
      setBatch(null)
      setFile(null)
      if (input.current) input.current.value = ''
      refresh()
    },
  })

  const cancel = useMutation({
    mutationFn: (b: Batch) => api<Batch>(`/imports/${b.id}/cancel`, { method: 'POST' }),
    onSuccess: () => {
      setBatch(null)
      refresh()
    },
  })

  function submit(event: FormEvent) {
    event.preventDefault()
    if (file) check.mutate()
  }

  return (
    <section className="card upload">
      <div className="upload-head">
        <h2>{title}</h2>
        <a className="link" href={`/api/imports/templates/${kind}`}>
          Télécharger le modèle
        </a>
      </div>
      <p className="muted">{text}</p>

      <form onSubmit={submit}>
        <label className="field">
          <span>Fichier (.xlsx ou .csv)</span>
          <input
            ref={input}
            type="file"
            accept=".xlsx,.csv"
            onChange={(e) => {
              setFile(e.target.files?.[0] ?? null)
              setBatch(null)
              setDone(null)
            }}
            required
          />
        </label>
        {kind === 'echus' && (
          <label className="field">
            <span>Année des données (seulement pour le format croisé)</span>
            <input inputMode="numeric" value={year} onChange={(e) => setYear(e.target.value)} placeholder="2026" />
          </label>
        )}
        <button className="btn-primary" disabled={!file || check.isPending}>
          {check.isPending ? 'Vérification…' : 'Vérifier le fichier'}
        </button>
      </form>

      {check.isError && <div className="error">{check.error.message}</div>}
      {batch && (
        <Report
          batch={batch}
          ack={ack}
          setAck={setAck}
          busy={confirm.isPending || cancel.isPending}
          onConfirm={() => confirm.mutate(batch)}
          onCancel={() => cancel.mutate(batch)}
        />
      )}
      {confirm.isError && <div className="error">{confirm.error.message}</div>}
      {done && (
        <div className="success">
          Import enregistré : {plural(done.rows_kept, 'ligne')}, {monthRange(done.months)}.
        </div>
      )}
    </section>
  )
}

function Report({
  batch,
  ack,
  setAck,
  busy,
  onConfirm,
  onCancel,
}: {
  batch: Batch
  ack: boolean
  setAck: (value: boolean) => void
  busy: boolean
  onConfirm: () => void
  onCancel: () => void
}) {
  const refused = batch.status === 'rejected'
  const hasWarnings = batch.warnings.length > 0

  return (
    <div className={refused ? 'report report-err' : 'report'}>
      <div className="report-title">
        {refused
          ? `Fichier refusé : ${plural(batch.errors.length, 'erreur')} à corriger`
          : `Fichier valide : ${plural(batch.rows_kept, 'ligne')}, ${monthRange(batch.months)}`}
      </div>
      {batch.errors.length > 0 && <IssueList title="Erreurs" items={batch.errors} tone="err" />}
      {hasWarnings && <IssueList title="Avertissements" items={batch.warnings} tone="warn" />}
      {refused ? (
        <p className="muted">Rien n’a été enregistré. Corrigez le fichier puis déposez-le à nouveau.</p>
      ) : (
        <>
          {hasWarnings && (
            <label className="check">
              <input type="checkbox" checked={ack} onChange={(e) => setAck(e.target.checked)} />
              <span>J’ai lu les avertissements et je confirme l’import.</span>
            </label>
          )}
          <div className="actions">
            <button className="btn-primary" onClick={onConfirm} disabled={busy || (hasWarnings && !ack)}>
              Importer
            </button>
            <button className="btn-ghost" onClick={onCancel} disabled={busy}>
              Annuler
            </button>
          </div>
        </>
      )}
    </div>
  )
}

function IssueList({ title, items, tone }: { title: string; items: Issue[]; tone: 'err' | 'warn' }) {
  return (
    <div className={`issues issues-${tone}`}>
      <div className="issues-title">
        {title} ({items.length})
      </div>
      <ul>
        {items.map((issue, i) => (
          <li key={i}>{issue.message}</li>
        ))}
      </ul>
    </div>
  )
}

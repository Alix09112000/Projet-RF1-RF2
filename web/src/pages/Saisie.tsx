import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Fragment, useMemo, useState } from 'react'
import { api } from '../api/client'

interface Slot {
  index: number
  column: string
  period: 'actual' | 'rf2' | 'bi'
  label: string
}

interface Line {
  row: number
  label: string
  unit: string
  nature: string
  section: string
  first_slot: number
  note: string
  values: (number | null)[]
}

interface Balance {
  row: number
  label: string
  confirmed: boolean
  values: (number | null)[]
}

interface ModuleData {
  module: string
  name: string
  direction: string
  version: string
  editable: boolean
  slots: Slot[]
  lines: Line[]
  balances: Balance[]
  warnings: string[]
}

interface Change {
  row: number
  label: string
  slot: number
  old_value: number | null
  new_value: number | null
  comment: string | null
  user: string
  changed_at: string
}

const MODULES = [
  { code: 'B2C1', label: 'Particuliers (B2C1)' },
  { code: 'SME1', label: 'Entreprises (SME1)' },
]
const PERIODS: { key: Slot['period']; label: string }[] = [
  { key: 'actual', label: 'Réel' },
  { key: 'rf2', label: 'RF2' },
  { key: 'bi', label: 'BI' },
]
const VERSION = 'RF2'
const dateFormat = new Intl.DateTimeFormat('fr-FR', { dateStyle: 'short', timeStyle: 'short' })

const key = (row: number, slot: number) => `${row}:${slot}`

function show(value: number | null | undefined, unit: string) {
  if (value === null || value === undefined) return ''
  if (unit === '%') return String(Math.round(value * 10000) / 100)
  return String(value)
}

function parse(text: string, unit: string): number | null | 'invalid' {
  const cleaned = text.replace(/[\s\u00a0]/g, '').replace(',', '.')
  if (cleaned === '') return null
  const n = Number(cleaned)
  if (!Number.isFinite(n)) return 'invalid'
  return unit === '%' ? n / 100 : n
}

export default function Saisie() {
  const queryClient = useQueryClient()
  const [moduleCode, setModuleCode] = useState('B2C1')
  const [period, setPeriod] = useState<Slot['period']>('rf2')
  const [drafts, setDrafts] = useState<Record<string, string>>({})
  const [comment, setComment] = useState('')
  const [historyRow, setHistoryRow] = useState<Line | null>(null)

  const data = useQuery({
    queryKey: ['inputs', VERSION, moduleCode],
    queryFn: () => api<ModuleData>(`/inputs/${VERSION}/${moduleCode}`),
  })

  const history = useQuery({
    queryKey: ['inputs-history', moduleCode, historyRow?.row],
    queryFn: () => api<Change[]>(`/inputs/${VERSION}/${moduleCode}/history?row=${historyRow!.row}`),
    enabled: historyRow !== null,
  })

  const lineByRow = useMemo(
    () => new Map((data.data?.lines ?? []).map((l) => [l.row, l])),
    [data.data],
  )

  const invalid = Object.entries(drafts).filter(([k, v]) => {
    const line = lineByRow.get(Number(k.split(':')[0]))
    return line ? parse(v, line.unit) === 'invalid' : false
  })

  const save = useMutation({
    mutationFn: () => {
      const cells = Object.entries(drafts).map(([k, v]) => {
        const [row, slot] = k.split(':').map(Number)
        return { row, slot, value: parse(v, lineByRow.get(row)!.unit) }
      })
      return api<{ changed: number; warnings: string[] }>(`/inputs/${VERSION}/${moduleCode}`, {
        method: 'PUT',
        body: JSON.stringify({ cells, comment: comment.trim() || null }),
      })
    },
    onSuccess: () => {
      setDrafts({})
      setComment('')
      queryClient.invalidateQueries({ queryKey: ['inputs', VERSION, moduleCode] })
      queryClient.invalidateQueries({ queryKey: ['inputs-history', moduleCode] })
    },
  })

  function switchModule(code: string) {
    if (Object.keys(drafts).length && !window.confirm('Abandonner les modifications non enregistrées ?')) return
    setDrafts({})
    setHistoryRow(null)
    setModuleCode(code)
  }

  const d = data.data
  const visible = d?.slots.filter((s) => s.period === period) ?? []
  const pending = Object.keys(drafts).length
  const sections: { name: string; lines: Line[] }[] = []
  for (const line of d?.lines ?? []) {
    const last = sections[sections.length - 1]
    if (last && last.name === line.section) last.lines.push(line)
    else sections.push({ name: line.section, lines: [line] })
  }

  return (
    <div className="page page-wide">
      <h1>Saisie des hypothèses</h1>
      <p className="muted lead">
        Version {VERSION} · direction {d?.direction ?? 'DRCOM'}. Seules les cellules de saisie du modèle (beiges) sont
        modifiables. Les pourcentages se saisissent en % (30 pour 30 %).
      </p>

      <div className="toolbar">
        <div className="seg">
          {MODULES.map((m) => (
            <button key={m.code} className={m.code === moduleCode ? 'seg-opt on' : 'seg-opt'} onClick={() => switchModule(m.code)}>
              {m.label}
            </button>
          ))}
        </div>
        <div className="seg">
          {PERIODS.map((p) => (
            <button key={p.key} className={p.key === period ? 'seg-opt on' : 'seg-opt'} onClick={() => setPeriod(p.key)}>
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {data.isPending && <p className="muted">Chargement…</p>}
      {data.isError && <div className="error">{data.error.message}</div>}

      {d && (
        <>
          {!d.editable && <div className="notice">Lecture seule : version figée ou saisie réservée à la direction {d.direction}.</div>}
          {d.warnings.map((w) => (
            <div key={w} className="notice">{w}</div>
          ))}

          <div className="card grid-card">
            <div className="table-wrap">
              <table className="table grid">
                <thead>
                  <tr>
                    <th className="sticky">Ligne</th>
                    <th className="sticky2">Hypothèse</th>
                    <th>Unité</th>
                    {visible.map((s) => (
                      <th key={s.index} className="num">
                        {s.label}
                        <div className="hint-sm">col. {s.column}</div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {sections.map((section) => (
                    <Fragment key={section.name}>
                      <tr className="section-row">
                        <td colSpan={3 + visible.length}>{section.name}</td>
                      </tr>
                      {section.lines.map((line) => (
                        <tr key={line.row}>
                          <td className="sticky muted">{line.row}</td>
                          <td className="sticky2">
                            <button className="linklike" onClick={() => setHistoryRow(line)} title="Voir l’historique">
                              {line.label}
                            </button>
                            {line.note && <div className="hint-sm">{line.note}</div>}
                          </td>
                          <td className="muted">{line.unit}</td>
                          {visible.map((s) => {
                            const k = key(line.row, s.index)
                            const open = d.editable && s.index >= line.first_slot
                            const draft = drafts[k]
                            const bad = draft !== undefined && parse(draft, line.unit) === 'invalid'
                            return (
                              <td key={s.index} className="num">
                                {open ? (
                                  <input
                                    className={bad ? 'cell bad' : draft !== undefined ? 'cell dirty' : 'cell'}
                                    inputMode="decimal"
                                    value={draft ?? show(line.values[s.index], line.unit)}
                                    onChange={(e) => setDrafts({ ...drafts, [k]: e.target.value })}
                                  />
                                ) : (
                                  <span className="cell-ro">{show(line.values[s.index], line.unit) || '·'}</span>
                                )}
                              </td>
                            )
                          })}
                        </tr>
                      ))}
                    </Fragment>
                  ))}
                  <tr className="section-row">
                    <td colSpan={3 + visible.length}>Soldes calculés (1 − parts saisies)</td>
                  </tr>
                  {d.balances.map((b) => (
                    <tr key={b.row}>
                      <td className="sticky muted">{b.row}</td>
                      <td className="sticky2">
                        {b.label}
                        {!b.confirmed && <div className="hint-sm">règle à confirmer</div>}
                      </td>
                      <td className="muted">%</td>
                      {visible.map((s) => (
                        <td key={s.index} className="num calc">{show(b.values[s.index], '%')}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {d.editable && (
            <div className="savebar">
              <input
                className="comment"
                placeholder="Justification (facultatif, gardée dans l’historique)"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
              />
              <button className="btn-ghost" disabled={!pending || save.isPending} onClick={() => setDrafts({})}>
                Annuler
              </button>
              <button className="btn-primary" disabled={!pending || invalid.length > 0 || save.isPending} onClick={() => save.mutate()}>
                {save.isPending ? 'Enregistrement…' : `Enregistrer${pending ? ` (${pending})` : ''}`}
              </button>
            </div>
          )}
          {invalid.length > 0 && <div className="error">{invalid.length} cellule(s) ne contiennent pas un nombre.</div>}
          {save.isError && <div className="error">{save.error.message}</div>}
          {save.isSuccess && <div className="success">{save.data.changed} cellule(s) enregistrée(s).</div>}
        </>
      )}

      {historyRow && (
        <div className="dialog-backdrop" onClick={() => setHistoryRow(null)}>
          <div className="card dialog" onClick={(e) => e.stopPropagation()}>
            <h2>Historique · ligne {historyRow.row}</h2>
            <p className="muted">{historyRow.label}</p>
            {history.isPending && <p className="muted">Chargement…</p>}
            {history.data?.length === 0 && <p className="muted">Aucune modification.</p>}
            {history.data && history.data.length > 0 && (
              <div className="table-wrap">
                <table className="table">
                  <thead>
                    <tr><th>Date</th><th>Mois</th><th>Avant</th><th>Après</th><th>Par</th><th>Justification</th></tr>
                  </thead>
                  <tbody>
                    {history.data.map((h, i) => (
                      <tr key={i}>
                        <td>{dateFormat.format(new Date(h.changed_at))}</td>
                        <td>{d?.slots[h.slot]?.label}</td>
                        <td>{show(h.old_value, historyRow.unit) || '—'}</td>
                        <td>{show(h.new_value, historyRow.unit) || '—'}</td>
                        <td>{h.user}</td>
                        <td>{h.comment ?? ''}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <div className="actions">
              <button className="btn-ghost" onClick={() => setHistoryRow(null)}>Fermer</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

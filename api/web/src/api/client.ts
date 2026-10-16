export type Role = 'contributor' | 'controller' | 'viewer' | 'admin'

export interface User {
  id: number
  email: string
  full_name: string
  role: Role
  direction: string | null
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message)
  }
}

function errorMessage(body: unknown, fallback: string): string {
  if (body && typeof body === 'object' && 'detail' in body) {
    const detail = (body as { detail: unknown }).detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail.map((d) => (d as { msg?: string }).msg ?? '').filter(Boolean).join(' · ')
    }
  }
  return fallback
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const isForm = init.body instanceof FormData
  const response = await fetch(`/api${path}`, {
    credentials: 'include',
    ...init,
    headers: isForm ? init.headers : { 'Content-Type': 'application/json', ...(init.headers ?? {}) },
  })
  if (!response.ok) {
    let body: unknown = null
    try {
      body = await response.json()
    } catch {
      /* corps vide ou non JSON */
    }
    throw new ApiError(response.status, errorMessage(body, `Erreur ${response.status}`))
  }
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

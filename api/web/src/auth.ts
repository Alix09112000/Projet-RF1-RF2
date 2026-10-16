import { useQuery } from '@tanstack/react-query'
import { api, ApiError, type User } from './api/client'

/** Utilisateur connecté, ou null si aucune session. */
export function useMe() {
  return useQuery({
    queryKey: ['me'],
    queryFn: async (): Promise<User | null> => {
      try {
        return await api<User>('/auth/me')
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) return null
        throw error
      }
    },
  })
}

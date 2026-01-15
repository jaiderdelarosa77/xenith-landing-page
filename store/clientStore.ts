import { create } from 'zustand'
import { Client } from '@/lib/validations/client'

interface ClientStore {
  clients: Client[]
  currentClient: Client | null
  isLoading: boolean
  error: string | null
  searchQuery: string
  setClients: (clients: Client[]) => void
  setCurrentClient: (client: Client | null) => void
  addClient: (client: Client) => void
  updateClient: (id: string, client: Client) => void
  removeClient: (id: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setSearchQuery: (query: string) => void
}

export const useClientStore = create<ClientStore>((set) => ({
  clients: [],
  currentClient: null,
  isLoading: false,
  error: null,
  searchQuery: '',
  setClients: (clients) => set({ clients }),
  setCurrentClient: (client) => set({ currentClient: client }),
  addClient: (client) =>
    set((state) => ({ clients: [...state.clients, client] })),
  updateClient: (id, updatedClient) =>
    set((state) => ({
      clients: state.clients.map((c) => (c.id === id ? updatedClient : c)),
    })),
  removeClient: (id) =>
    set((state) => ({
      clients: state.clients.filter((c) => c.id !== id),
    })),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setSearchQuery: (query) => set({ searchQuery: query }),
}))

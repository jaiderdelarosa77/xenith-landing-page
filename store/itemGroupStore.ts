import { create } from 'zustand'
import { ItemGroup } from '@/lib/validations/itemGroup'

interface ItemGroupFilters {
  search: string
}

interface ItemGroupStore {
  groups: ItemGroup[]
  currentGroup: ItemGroup | null
  isLoading: boolean
  error: string | null
  filters: ItemGroupFilters
  setGroups: (groups: ItemGroup[]) => void
  setCurrentGroup: (group: ItemGroup | null) => void
  addGroup: (group: ItemGroup) => void
  updateGroup: (id: string, group: ItemGroup) => void
  removeGroup: (id: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setFilters: (filters: Partial<ItemGroupFilters>) => void
  resetFilters: () => void
}

const defaultFilters: ItemGroupFilters = {
  search: '',
}

export const useItemGroupStore = create<ItemGroupStore>((set) => ({
  groups: [],
  currentGroup: null,
  isLoading: false,
  error: null,
  filters: defaultFilters,
  setGroups: (groups) => set({ groups }),
  setCurrentGroup: (group) => set({ currentGroup: group }),
  addGroup: (group) =>
    set((state) => ({ groups: [group, ...state.groups] })),
  updateGroup: (id, updatedGroup) =>
    set((state) => ({
      groups: state.groups.map((g) => (g.id === id ? updatedGroup : g)),
      currentGroup: state.currentGroup?.id === id ? updatedGroup : state.currentGroup,
    })),
  removeGroup: (id) =>
    set((state) => ({
      groups: state.groups.filter((g) => g.id !== id),
      currentGroup: state.currentGroup?.id === id ? null : state.currentGroup,
    })),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setFilters: (filters) =>
    set((state) => ({ filters: { ...state.filters, ...filters } })),
  resetFilters: () => set({ filters: defaultFilters }),
}))

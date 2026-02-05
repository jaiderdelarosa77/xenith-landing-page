import { create } from 'zustand'
import { Concept } from '@/lib/validations/concept'

interface ConceptFilters {
  search: string
  category: string
  supplierId: string
  isActive: string
}

interface ConceptStore {
  concepts: Concept[]
  currentConcept: Concept | null
  isLoading: boolean
  error: string | null
  filters: ConceptFilters
  setConcepts: (concepts: Concept[]) => void
  setCurrentConcept: (concept: Concept | null) => void
  addConcept: (concept: Concept) => void
  updateConcept: (id: string, concept: Concept) => void
  removeConcept: (id: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setFilters: (filters: Partial<ConceptFilters>) => void
  resetFilters: () => void
}

const defaultFilters: ConceptFilters = {
  search: '',
  category: '',
  supplierId: '',
  isActive: '',
}

export const useConceptStore = create<ConceptStore>((set) => ({
  concepts: [],
  currentConcept: null,
  isLoading: false,
  error: null,
  filters: defaultFilters,
  setConcepts: (concepts) => set({ concepts }),
  setCurrentConcept: (concept) => set({ currentConcept: concept }),
  addConcept: (concept) =>
    set((state) => ({ concepts: [concept, ...state.concepts] })),
  updateConcept: (id, updatedConcept) =>
    set((state) => ({
      concepts: state.concepts.map((c) => (c.id === id ? updatedConcept : c)),
      currentConcept: state.currentConcept?.id === id ? updatedConcept : state.currentConcept,
    })),
  removeConcept: (id) =>
    set((state) => ({
      concepts: state.concepts.filter((c) => c.id !== id),
      currentConcept: state.currentConcept?.id === id ? null : state.currentConcept,
    })),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setFilters: (filters) =>
    set((state) => ({ filters: { ...state.filters, ...filters } })),
  resetFilters: () => set({ filters: defaultFilters }),
}))

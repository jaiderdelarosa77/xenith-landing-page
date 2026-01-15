import { create } from 'zustand'
import { Quotation, QuotationStatus } from '@/lib/validations/quotation'

interface QuotationFilters {
  status?: QuotationStatus
  clientId?: string
  projectId?: string
}

interface QuotationStore {
  quotations: Quotation[]
  currentQuotation: Quotation | null
  isLoading: boolean
  error: string | null
  searchQuery: string
  filters: QuotationFilters
  setQuotations: (quotations: Quotation[]) => void
  setCurrentQuotation: (quotation: Quotation | null) => void
  addQuotation: (quotation: Quotation) => void
  updateQuotation: (id: string, quotation: Quotation) => void
  removeQuotation: (id: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setSearchQuery: (query: string) => void
  setFilters: (filters: QuotationFilters) => void
  clearFilters: () => void
}

export const useQuotationStore = create<QuotationStore>((set) => ({
  quotations: [],
  currentQuotation: null,
  isLoading: false,
  error: null,
  searchQuery: '',
  filters: {},
  setQuotations: (quotations) => set({ quotations }),
  setCurrentQuotation: (quotation) => set({ currentQuotation: quotation }),
  addQuotation: (quotation) =>
    set((state) => ({ quotations: [...state.quotations, quotation] })),
  updateQuotation: (id, updatedQuotation) =>
    set((state) => ({
      quotations: state.quotations.map((q) => (q.id === id ? updatedQuotation : q)),
    })),
  removeQuotation: (id) =>
    set((state) => ({
      quotations: state.quotations.filter((q) => q.id !== id),
    })),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  setFilters: (filters) => set({ filters }),
  clearFilters: () => set({ filters: {} }),
}))

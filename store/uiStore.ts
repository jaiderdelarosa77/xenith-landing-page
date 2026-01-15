import { create } from 'zustand'

interface UIState {
  sidebarOpen: boolean
  modals: Record<string, boolean>
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  openModal: (key: string) => void
  closeModal: (key: string) => void
  closeAllModals: () => void
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: false,
  modals: {},

  toggleSidebar: () =>
    set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  setSidebarOpen: (open) =>
    set({ sidebarOpen: open }),

  openModal: (key) =>
    set((state) => ({
      modals: { ...state.modals, [key]: true },
    })),

  closeModal: (key) =>
    set((state) => ({
      modals: { ...state.modals, [key]: false },
    })),

  closeAllModals: () =>
    set({ modals: {} }),
}))

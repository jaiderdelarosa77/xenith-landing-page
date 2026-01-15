import { create } from 'zustand'
import { Project, ProjectStatus, Priority } from '@/lib/validations/project'

interface ProjectFilters {
  status?: ProjectStatus
  priority?: Priority
  clientId?: string
  assignedTo?: string
}

interface ProjectStore {
  projects: Project[]
  currentProject: Project | null
  isLoading: boolean
  error: string | null
  searchQuery: string
  filters: ProjectFilters
  setProjects: (projects: Project[]) => void
  setCurrentProject: (project: Project | null) => void
  addProject: (project: Project) => void
  updateProject: (id: string, project: Project) => void
  removeProject: (id: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setSearchQuery: (query: string) => void
  setFilters: (filters: ProjectFilters) => void
  clearFilters: () => void
}

export const useProjectStore = create<ProjectStore>((set) => ({
  projects: [],
  currentProject: null,
  isLoading: false,
  error: null,
  searchQuery: '',
  filters: {},
  setProjects: (projects) => set({ projects }),
  setCurrentProject: (project) => set({ currentProject: project }),
  addProject: (project) =>
    set((state) => ({ projects: [...state.projects, project] })),
  updateProject: (id, updatedProject) =>
    set((state) => ({
      projects: state.projects.map((p) => (p.id === id ? updatedProject : p)),
    })),
  removeProject: (id) =>
    set((state) => ({
      projects: state.projects.filter((p) => p.id !== id),
    })),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  setFilters: (filters) => set({ filters }),
  clearFilters: () => set({ filters: {} }),
}))

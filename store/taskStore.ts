import { create } from 'zustand'
import { TaskStatus, Priority } from '@/lib/validations/project'

export type TaskWithRelations = {
  id: string
  projectId: string
  title: string
  description: string | null
  status: TaskStatus
  assignedTo: string | null
  dueDate: Date | null
  priority: Priority
  completed: boolean
  createdAt: Date
  updatedAt: Date
  project?: {
    id: string
    title: string
    status: string
  }
  assignedUser?: {
    id: string
    name: string | null
    email: string
  } | null
}

interface TaskFilters {
  status?: TaskStatus
  priority?: Priority
  assignedTo?: string
  myTasks?: boolean
}

interface TaskStore {
  tasks: TaskWithRelations[]
  isLoading: boolean
  error: string | null
  searchQuery: string
  filters: TaskFilters
  setTasks: (tasks: TaskWithRelations[]) => void
  updateTask: (id: string, task: TaskWithRelations) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setSearchQuery: (query: string) => void
  setFilters: (filters: TaskFilters) => void
  clearFilters: () => void
}

export const useTaskStore = create<TaskStore>((set) => ({
  tasks: [],
  isLoading: false,
  error: null,
  searchQuery: '',
  filters: {},
  setTasks: (tasks) => set({ tasks }),
  updateTask: (id, updatedTask) =>
    set((state) => ({
      tasks: state.tasks.map((t) => (t.id === id ? updatedTask : t)),
    })),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  setFilters: (filters) => set({ filters }),
  clearFilters: () => set({ filters: {} }),
}))

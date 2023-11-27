import { defineStore } from 'pinia'
import { fetchHandle } from '@/composables/update'

export interface Document {
  type: string
  created: string
  modified: string
  effective: string
  url: string
  title: string
  content: string | null
}

export const useDocumentsStore = defineStore('documents', {
  state: () => {
    return {
      documents: [] as Document[]
    }
  },

  actions: {
    async updateDocuments() {
      try {
        const response = await fetchHandle(import.meta.env.VITE_API + '/documents')
        this.documents = await response.json()
      } catch (error) {
        console.error(error)
      }
    }
  }
})

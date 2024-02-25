import { defineStore } from 'pinia'

import { fetchHandle, updateWrapper } from '@/utils/update'

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
      documents: [] as Document[],
    }
  },

  actions: {
    async updateDocuments() {
      updateWrapper(async () => {
        const response = await fetchHandle(import.meta.env.VITE_API + '/documents')
        this.documents = await response.json()
      })
    },

    filterDocuments(documentTypes: string[]) {
      return this.documents?.filter(document => documentTypes.includes(document.type)).reverse()
    },
  },

  persist: true,
})

import { defineStore } from 'pinia'

export const useSnackbarStore = defineStore('snackbar', {
  state: () => {
    return {
      show: false,
      text: '',
      buttonText: '',
      action: () => {},
      timeout: 2000,
    }
  },

  actions: {
    displaySnackbar(text: string, buttonText?: string, action?: () => void, timeout?: number) {
      this.show = true
      this.text = text
      this.buttonText = buttonText || ''
      this.action = action || (() => {})
      this.timeout = timeout || 1500
    },
  },
})

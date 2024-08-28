import { defineStore } from 'pinia'

export const useSnackbarStore = defineStore('snackbar', {
  state: () => {
    return {
      show: false,
      text: '',
      buttonText: '',
      buttonAction: () => {},
      timeout: 4000,
    }
  },

  actions: {
    displaySnackbar(
      text: string,
      buttonText?: string,
      buttonAction?: () => void,
      timeout?: number,
    ) {
      this.text = text
      this.buttonText = buttonText || ''
      this.buttonAction = buttonAction || (() => {})
      this.timeout = timeout || 4000
      this.show = true
    },
  },
})

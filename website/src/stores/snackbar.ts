import { defineStore } from 'pinia'

export const useSnackbarStore = defineStore('snackbar', {
  state: () => {
    return {
      show: false,
      message: '',
      buttonText: '',
      buttonAction: () => undefined,
      timeout: 2000,
    }
  },

  actions: {
    displaySnackbar(
      message: string,
      buttonText?: string,
      buttonAction?: () => undefined,
      timeout?: number,
    ) {
      this.show = true
      this.message = message
      this.buttonText = buttonText || ''
      this.buttonAction = buttonAction || (() => undefined)
      this.timeout = timeout || 2000
    },
  },
})

export function displaySnackbar (message: string): void {
  document.dispatchEvent(new CustomEvent('displaySnackbar', { detail: { message: message } }))
}

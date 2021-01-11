export function displaySnackbar (message: string): void;
export function displaySnackbar (message: string, button: string, action: () => void): void;

export function displaySnackbar (message: string, button?: string, action?: () => void): void {
  document.dispatchEvent(new CustomEvent('displaySnackbar', { detail: { message, button, action } }))
}

export function hideSnackbar (): void {
  document.dispatchEvent(new CustomEvent('hideSnackbar'))
}

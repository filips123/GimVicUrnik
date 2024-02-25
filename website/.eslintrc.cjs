/* eslint-env node */
require('@rushstack/eslint-patch/modern-module-resolution')

module.exports = {
  root: true,
  extends: [
    'plugin:vue/vue3-essential',
    'eslint:recommended',
    '@vue/eslint-config-typescript',
    '@vue/eslint-config-prettier/skip-formatting',
  ],
  plugins: [
    'import',
    'simple-import-sort',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
  },
  rules: {
    'simple-import-sort/imports': 'warn',
  },
}

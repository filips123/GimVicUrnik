/* eslint-env node */
require('@rushstack/eslint-patch/modern-module-resolution')

module.exports = {
  root: true,
  extends: [
    'plugin:vue/vue3-recommended',
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
    'eqeqeq': 'error',
    'no-cond-assign': 'error',
    'no-class-assign': 'error',
    'no-const-assign': 'error',
    'accessor-pairs': 'warn',
  },
}

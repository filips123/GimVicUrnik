import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { includeIgnoreFile } from '@eslint/compat'
import eslint from '@eslint/js'
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'
import vueTsEslintConfig from '@vue/eslint-config-typescript'
import pluginSimpleImportSort from 'eslint-plugin-simple-import-sort'
import pluginVue from 'eslint-plugin-vue'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const gitignorePath = path.resolve(__dirname, '..', '.gitignore')

export default [
  {
    name: 'app/files-to-lint',
    files: ['**/*.{vue,js,jsx,cjs,mjs,ts,tsx,cts,mts}'],
  },

  // Ignore files specified in .gitignore
  includeIgnoreFile(gitignorePath),

  // Use recommended config as base
  eslint.configs.recommended,

  // Use recommended Vue config
  ...pluginVue.configs['flat/recommended'],

  // Use recommended TypeScript config
  ...vueTsEslintConfig({ extends: ['recommended'] }),

  // Disable formatting rules as they are handled by Prettier
  skipFormatting,

  {
    plugins: {
      'simple-import-sort': pluginSimpleImportSort,
    },
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
      'simple-import-sort/imports': 'error',
      eqeqeq: 'error',
      'no-cond-assign': 'error',
      'no-class-assign': 'error',
      'no-const-assign': 'error',
      'accessor-pairs': 'warn',
    },
  },
]

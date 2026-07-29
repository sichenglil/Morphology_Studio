import vue from 'eslint-plugin-vue'
import tseslint from 'typescript-eslint'

export default [
  ...vue.configs['flat/essential'],
  ...tseslint.configs.recommended.map((config) => ({ ...config, files: ['**/*.ts'] })),
  {
    files: ['**/*.vue'],
    languageOptions: { parserOptions: { parser: tseslint.parser } },
    rules: { 'vue/multi-word-component-names': 'off' },
  },
  { ignores: ['dist/**', 'playwright-report/**'] },
]

export default {
  // Prettier 3 no longer discovers plugins automatically. Keep repository
  // language support explicit so the pre-commit hook behaves the same on
  // every workstation and CI runner.
  plugins: ['prettier-plugin-sh', 'prettier-plugin-sql', 'prettier-plugin-toml'],

  // Basic formatting
  semi: true,
  trailingComma: 'es5',
  singleQuote: true,
  quoteProps: 'as-needed',
  jsxSingleQuote: true,

  // Indentation
  tabWidth: 2,
  useTabs: false,

  // Line length
  printWidth: 120,

  // Spacing
  bracketSpacing: true,
  bracketSameLine: false,
  arrowParens: 'avoid',

  // Line endings
  endOfLine: 'lf',

  // Embedded languages
  embeddedLanguageFormatting: 'auto',

  // HTML/JSX specific
  htmlWhitespaceSensitivity: 'css',
  vueIndentScriptAndStyle: false,

  // Override for specific file types
  overrides: [
    {
      files: '*.json',
      options: {
        printWidth: 80,
        tabWidth: 2,
      },
    },
    {
      files: '*.md',
      options: {
        printWidth: 80,
        proseWrap: 'always',
        tabWidth: 2,
      },
    },
    {
      files: '*.yml',
      options: {
        tabWidth: 2,
        singleQuote: false,
      },
    },
    {
      files: '*.yaml',
      options: {
        tabWidth: 2,
        singleQuote: false,
      },
    },
    {
      files: ['*.css', '*.scss', '*.less'],
      options: {
        singleQuote: false,
        tabWidth: 2,
      },
    },
    {
      files: '*.html',
      options: {
        printWidth: 120,
        tabWidth: 2,
        htmlWhitespaceSensitivity: 'ignore',
      },
    },
    {
      files: '*.ipynb',
      options: {
        parser: 'json',
      },
    },
  ],
};

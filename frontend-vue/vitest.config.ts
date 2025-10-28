import { fileURLToPath } from 'node:url'
import { mergeConfig, defineConfig, configDefaults } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      exclude: [...configDefaults.exclude, 'e2e/*'],
      root: fileURLToPath(new URL('./', import.meta.url)),
      setupFiles: ['./src/test-setup.ts'],
      css: {
        modules: {
          classNameStrategy: 'non-scoped'
        }
      },
      server: {
        deps: {
          inline: ['vuetify']
        }
      },
      coverage: {
        provider: 'v8',
        reporter: ['text', 'json', 'html'],
        exclude: [
          'node_modules/',
          'src/**/*.spec.ts',
          'src/**/*.test.ts',
          '**/*.d.ts',
          '**/*.config.*',
          '**/mockData',
          'src/main.ts'
        ],
        all: true,
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80
      }
    }
  })
)

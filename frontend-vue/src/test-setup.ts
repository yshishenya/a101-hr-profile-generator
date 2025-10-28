/**
 * Vitest setup file
 * Global test configuration and polyfills
 */

// Mock visualViewport for Vuetify
Object.defineProperty(window, 'visualViewport', {
  value: {
    width: 1024,
    height: 768,
    offsetLeft: 0,
    offsetTop: 0,
    pageLeft: 0,
    pageTop: 0,
    scale: 1,
    addEventListener: () => {},
    removeEventListener: () => {}
  },
  writable: true,
  configurable: true
})

// Mock matchMedia for responsive Vuetify components
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => true
  })
})

// Mock ResizeObserver for Vuetify components
global.ResizeObserver = class ResizeObserver {
  constructor(callback: ResizeObserverCallback) {
    this.callback = callback
  }

  callback: ResizeObserverCallback

  observe() {
    // Mock implementation
  }

  unobserve() {
    // Mock implementation
  }

  disconnect() {
    // Mock implementation
  }
}

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor(callback: IntersectionObserverCallback) {
    this.callback = callback
  }

  callback: IntersectionObserverCallback
  root: Element | null = null
  rootMargin: string = ''
  thresholds: ReadonlyArray<number> = []

  observe() {
    // Mock implementation
  }

  unobserve() {
    // Mock implementation
  }

  disconnect() {
    // Mock implementation
  }

  takeRecords(): IntersectionObserverEntry[] {
    return []
  }
}

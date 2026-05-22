// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Fix for MSW and Node.js environment compatibility
import { TextEncoder, TextDecoder } from 'util';

if (!global.TextEncoder) {
  global.TextEncoder = TextEncoder;
}

if (!global.TextDecoder) {
  global.TextDecoder = TextDecoder;
}

// Mock IntersectionObserver for components that use it
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver for components that use it
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock matchMedia for responsive components
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // Deprecated
    removeListener: jest.fn(), // Deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock fetch for API calls
global.fetch = jest.fn();

// Increase Jest timeout for async operations to prevent hanging
jest.setTimeout(15000);

// Suppress console noise during tests but keep important errors
const originalConsoleError = console.error;

beforeAll(() => {
  // Filter out React act() warnings and other test noise
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('An update to') ||
       args[0].includes('act(...)') ||
       args[0].includes('Cannot log after tests are done') ||
       args[0].includes('API Error:') ||
       args[0].includes('Error fetching games'))
    ) {
      return; // Suppress these warnings in tests
    }
    originalConsoleError.call(console, ...args);
  };
});

afterAll(() => {
  // Restore original console.error
  console.error = originalConsoleError;
});

// Clean up after each test to prevent Jest hanging
afterEach(() => {
  // Clear all timers and intervals
  jest.clearAllTimers();
  jest.useRealTimers();

  // Clear any pending async operations
  return new Promise(resolve => {
    setTimeout(resolve, 0);
  });
});

// MSW setup temporarily disabled due to Node.js environment compatibility issues
// TODO: Re-enable MSW when TextEncoder issue is resolved
// import { server } from './mocks/server';

// Establish API mocking before all tests
// beforeAll(() => server.listen());

// Reset any request handlers that we may add during the tests
// afterEach(() => server.resetHandlers());

// Clean up after the tests are finished
// afterAll(() => server.close());

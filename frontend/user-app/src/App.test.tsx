import { describe, it, expect, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import App from './App';
import { UserProvider } from './context/UserContext';

// Mock localStorage
const localStorageMock = {
  getItem: () => 'test_user',
  setItem: () => {},
  removeItem: () => {},
  clear: () => {},
};

globalThis.localStorage = localStorageMock as any;

describe('App', () => {
  beforeEach(() => {
    // Reset any state between tests
  });

  it('renders without crashing', () => {
    const { container } = render(
      <UserProvider>
        <App />
      </UserProvider>
    );
    expect(container).toBeDefined();
  });
});

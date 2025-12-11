module.exports = {
  testEnvironment: 'jsdom',
  testMatch: ['**/tests/frontend/**/*.test.js'],
  collectCoverageFrom: [
    'index.html',
    '!**/node_modules/**',
    '!**/tests/**'
  ],
  setupFilesAfterEnv: ['<rootDir>/tests/frontend/setup.js'],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 75,
      lines: 75,
      statements: 75
    }
  }
};

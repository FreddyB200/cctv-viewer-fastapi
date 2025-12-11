# Test Suite Documentation

## Overview
Comprehensive test suite for the WebRTC CCTV streaming application.

## Running Tests

### Python Backend Tests
```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_settings.py

# Run specific test
pytest tests/unit/test_settings.py::test_settings_loads_from_env
```

### JavaScript Frontend Tests
```bash
# Install dependencies
npm install

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

## Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── conftest.py                    # Shared pytest fixtures
├── README.md                      # This file
├── unit/                          # Fast, isolated unit tests
│   ├── test_settings.py          # Settings configuration tests
│   └── test_main.py              # Main application logic tests
├── integration/                   # Slower integration tests
│   └── test_api_endpoints.py    # FastAPI endpoint tests
└── frontend/                      # JavaScript tests
    ├── setup.js                   # Jest test environment setup
    └── webrtc.test.js            # WebRTC function tests
```

## Coverage Goals

- **Python:** 80%+ overall, 95%+ for critical paths
- **JavaScript:** 75%+ overall, 90%+ for WebRTC functions

## Writing New Tests

### Python Test Pattern (AAA)
```python
def test_function_name_scenario_expected():
    """Test description."""
    # Arrange
    mock_data = create_test_data()

    # Act
    result = function_under_test(mock_data)

    # Assert
    assert result == expected_value
```

### JavaScript Test Pattern
```javascript
describe('functionName', () => {
  test('should do X when Y', () => {
    // Arrange
    const mockData = createMockData();

    // Act
    const result = functionUnderTest(mockData);

    // Assert
    expect(result).toBe(expectedValue);
  });
});
```

## Mocking Strategies

### Mock FFmpeg Processes
```python
mock_process = MagicMock()
mock_process.poll.return_value = None  # Running
mocker.patch('subprocess.Popen', return_value=mock_process)
```

### Mock WebRTC APIs
```javascript
global.fetch = jest.fn(() => Promise.resolve({
  ok: true,
  text: () => Promise.resolve('fake-sdp')
}));
```

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:
- Fast unit tests run on every commit
- Integration tests can be opt-in for pre-release validation
- Coverage reports generated automatically

## Troubleshooting

**Python tests fail with import errors:**
- Ensure you're in the project root directory
- Check that `requirements-dev.txt` is installed

**JavaScript tests fail with missing modules:**
- Run `npm install` to install dependencies
- Check that `node_modules/` is not in `.gitignore`

**Mock failures:**
- Verify mock setup in `conftest.py` and `setup.js`
- Check that mocked functions match actual signatures

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
├── __init__.py                        # Test package initialization
├── conftest.py                        # Shared pytest fixtures
├── README.md                          # This file
├── unit/                              # Fast, isolated unit tests
│   ├── test_settings.py              # Settings configuration tests
│   └── test_main.py                  # Main application logic tests
├── integration/                       # Slower integration tests
│   ├── test_api_endpoints.py        # FastAPI endpoint tests
│   ├── test_webrtc_endpoint.py      # WebRTC endpoint integration tests
│   └── test_concurrent_streams.py   # Concurrent camera stream tests
└── frontend/                          # JavaScript tests
    ├── setup.js                       # Jest test environment setup
    ├── webrtc.test.js                # WebRTC function tests
    └── webrtc-errors.test.js         # WebRTC error handling tests
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

## Known Limitations

### What is NOT tested:
1. **Real go2rtc backend integration**: The `/api/webrtc` endpoint is provided by go2rtc (external service on port 1984), not our FastAPI app. Tests verify our frontend configuration but cannot test actual go2rtc SDP negotiation without running the real service.

2. **Actual RTSP camera connections**: Tests mock FFmpeg processes and don't connect to real cameras. Network issues with actual cameras are not covered.

3. **Real-time performance**: Tests don't measure actual latency, bandwidth usage, or frame rates under load.

4. **Browser-specific WebRTC behavior**: Tests use mocked browser APIs. Real browser differences (Chrome vs Firefox vs Safari) are not tested.

5. **Network conditions**: Packet loss, jitter, and bandwidth throttling scenarios are not simulated.

6. **Long-running stability**: Tests don't run streams for hours to detect memory leaks or connection degradation.

### Mock vs. Real Backend:
- **Mocked**: RTCPeerConnection, fetch, FFmpeg processes, filesystem operations
- **Real**: FastAPI routing, HTML serving, Pydantic validation
- **External (not tested)**: go2rtc WebRTC server, actual RTSP cameras

## Test Coverage Summary

### Python Backend (~85% coverage):
- ✅ Settings loading and validation
- ✅ FFmpeg process management
- ✅ HLS directory creation and cleanup
- ✅ Startup health checks
- ✅ FastAPI endpoints (/, /health)
- ❌ Live FFmpeg stream validation (requires real cameras)

### JavaScript Frontend (~75% coverage):
- ✅ WebRTC connection setup
- ✅ ICE gathering and timeouts
- ✅ Resource cleanup
- ✅ Retry logic with exponential backoff
- ✅ Error handling for network failures
- ✅ HLS fallback mechanism
- ❌ Actual video playback (requires browser)
- ❌ User interaction (click-to-play)

### Integration Tests (~70% coverage):
- ✅ Frontend serves correct HTML
- ✅ Frontend contains WebRTC configuration
- ✅ Multiple camera support
- ✅ Concurrent stream isolation
- ❌ End-to-end WebRTC connection with go2rtc
- ❌ Actual SDP offer/answer exchange

## Linting and Code Quality

### Python:
```bash
# Run flake8
flake8 main.py settings.py

# Run black (formatter)
black main.py settings.py

# Run ruff (fast linter)
ruff check .
```

### JavaScript:
```bash
# Run ESLint
npm run lint

# Auto-fix ESLint issues
npm run lint:fix
```

## CI/CD Integration Examples

### GitHub Actions:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run Python tests
        run: pytest --cov=. --cov-report=xml
      - name: Install Node dependencies
        run: npm install
      - name: Run JavaScript tests
        run: npm test -- --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Test Development Guidelines

### Writing Good Tests:
1. **Follow AAA pattern**: Arrange, Act, Assert
2. **One assertion per test**: Keep tests focused
3. **Descriptive names**: `test_function_scenario_expectedResult`
4. **Use fixtures**: Share setup code via pytest fixtures
5. **Mock external dependencies**: Don't rely on network, filesystem, or time
6. **Test edge cases**: Null values, empty lists, boundary conditions

### Avoid:
- ❌ Testing implementation details (test behavior, not internal state)
- ❌ Fragile tests (tests that break on minor refactoring)
- ❌ Slow tests (mock I/O, use fake timers)
- ❌ Flaky tests (avoid race conditions, random data)

## Performance Benchmarks

Expected test execution times:
- **Unit tests**: < 5 seconds
- **Integration tests**: < 15 seconds
- **Frontend tests**: < 10 seconds
- **Full suite**: < 30 seconds

If tests exceed these times, investigate:
- Unmocked I/O operations
- Real network calls
- Missing `pytest-mock` or `jest.mock()`
- Synchronous sleeps not mocked

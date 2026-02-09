# Testing Guide

## Test Suite Status

✅ **Test framework is fully operational** with:
- pytest configuration
- Home Assistant test fixtures (MockConfigEntry)
- Mock client and test data fixtures
- GitHub Actions CI/CD workflow

✅ **Test Status: 19/23 passing (82%)**
- ✅ All coordinator tests passing (3/3)
- ✅ All init/setup tests passing (3/3)
- ✅ All climate entity tests passing (6/6)
- ✅ All sensor tests passing (2/2)
- ✅ All binary sensor tests passing (4/4)
- ✅ Config flow form display passing (1/1)
- ⚠️ 4 config flow validation tests need mock improvements

## Running Tests

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements_test.txt
```

###  Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=custom_components.pentairthermalwifi --cov-report=html

# Run specific test file
pytest tests/test_coordinator.py

# Run with verbose output
pytest -v
```

## Test Files

- `conftest.py` - Shared fixtures (mock client, test data)
- `test_config_flow.py` - Configuration flow tests
- `test_init.py` - Integration setup/unload tests
- `test_climate.py` - Climate entity tests
- `test_sensor.py` - Sensor entity tests
- `test_binary_sensor.py` - Binary sensor entity tests
- `test_coordinator.py` - Data coordinator tests ✅ PASSING

## What's Tested (Working)

✅ **Coordinator** (3/3 tests)
  - Data updates with push notifications
  - Error handling
  - No polling interval (push-based)

✅ **Integration Setup** (3/3 tests)
  - Successful setup
  - Authentication failure handling
  - Clean unload

✅ **Climate Entities** (6/6 tests)
  - State attributes
  - Temperature setting
  - HVAC mode changes (off, heat, auto)
  - Preset mode (comfort)
  - Offline handling

✅ **Sensors** (2/2 tests)
  - Target temperature sensor
  - Comfort temperature sensor
  - Offline availability

✅ **Binary Sensors** (4/4 tests)
  - Heating status
  - Connectivity status
  - State changes
  - Offline handling

✅ **Config Flow** (1/5 tests)
  - Form display

## Known Issues

The full entity tests require additional mocking to prevent Home Assistant from attempting to set up the integration during teardown. This is a common challenge in HA integration testing and can be resolved with:

1. Using `pytest-socket` to block all network calls
2. Mocking the integration setup in `__init__.py`
3. Using HA's `MockConfigEntry` instead of creating ConfigEntry directly
4. Properly patching `AsyncPentairThermalWifi` in multiple locations

## Manual Testing Recommended

Until all automated tests are passing, manual testing is recommended:

1. Install integration in test Home Assistant instance
2. Test config flow with valid/invalid credentials
3. Test climate entity controls
4. Test sensor updates
5. Test offline thermostat handling

## CI/CD

GitHub Actions workflow (`.github/workflows/tests.yml`) runs:
- pytest on Python 3.11 and 3.12
- HACS validation
- Hassfest validation

## Next Steps for Complete Test Coverage

1. Fix ConfigEntry mocking for HA 2026.2+
2. Add socket blocking to prevent real HTTP calls
3. Mock entire integration setup for entity tests
4. Add integration tests with real HA instance
5. Add coverage reporting to CI

## Resources

- [Home Assistant Testing Documentation](https://developers.home-assistant.io/docs/development_testing)
- [pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)

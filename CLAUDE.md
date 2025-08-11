# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Viam module for the DHT-20 temperature and humidity sensor. It implements a sensor component using the Viam robotics platform SDK. The module follows Viam's modular architecture pattern where hardware components are abstracted through standardized APIs.

## Development Commands

### Running the Module
```bash
./run.sh            # Runs the module locally with proper signal handling
```

### Building for Distribution
```bash
./build.sh          # Uses PyInstaller to create standalone executable and archive
```

## Code Architecture

### Module Structure
- `src/main.py`: Entry point that initializes the Viam module and handles import paths for both local development and packaged execution
- `src/models/dht_20.py`: Core sensor component implementation extending Viam's Sensor base class

### Key Components

**Dht20 Class** (`src/models/dht_20.py:14`)
- Extends `Sensor` and `EasyResource` from Viam SDK
- Model identifier: `ianwhalen:dht-20:dht-20`
- Implements required Viam sensor interface methods (currently stubbed):
  - `get_readings()`: Should return sensor data as key-value pairs
  - `do_command()`: For custom commands
  - `get_geometries()`: For spatial information

### Viam Integration Points
- Uses `Module.run_from_registry()` for automatic component discovery
- Configuration validation through `validate_config()`
- Dynamic reconfiguration support via `reconfigure()`
- Logging integrated through Viam's logger system

### Module Metadata
The `meta.json` file defines:
- Module ID: `ianwhalen:dht-20`
- API type: `rdk:component:sensor`
- Build configuration for multiple architectures
- Entry point: `dist/main`

## Development Notes

- Module supports both local development (via `run.sh`) and packaged execution
- Import handling in `main.py` accommodates different execution contexts
- Virtual environment is automatically managed by shell scripts
- PyInstaller packages everything into a single executable for distribution

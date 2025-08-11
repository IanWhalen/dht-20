# DHT-20 Sensor Implementation Plan

## Overview
Implement actual DHT-20 sensor functionality for temperature and humidity readings via I2C communication.

## Stage 1: Basic I2C Communication Setup
**Goal**: Establish I2C connection and basic sensor communication
**Success Criteria**: 
- Can initialize I2C connection to DHT-20 (default address 0x38)
- Can send basic commands without errors
- Configuration accepts I2C bus parameter
**Tests**: 
- Test I2C initialization with valid/invalid bus numbers
- Test sensor presence detection
- Test configuration validation
**Status**: Complete

## Stage 2: Sensor Data Reading
**Goal**: Read raw temperature and humidity data from sensor
**Success Criteria**:
- Can trigger measurement sequence
- Can read 7-byte data response
- Can parse temperature and humidity values
**Tests**:
- Test measurement trigger command
- Test data reading with CRC validation
- Test temperature/humidity calculation accuracy
**Status**: Complete

## Stage 3: get_readings() Implementation
**Goal**: Return properly formatted sensor readings via Viam interface
**Success Criteria**:
- get_readings() returns temperature in Celsius
- get_readings() returns humidity as percentage
- Proper error handling for sensor failures
**Tests**:
- Test get_readings() return format matches Viam expectations
- Test error handling for sensor disconnection
- Test reading values within expected ranges
**Status**: Complete

## Stage 4: Configuration and Error Handling
**Goal**: Robust configuration validation and comprehensive error handling
**Success Criteria**:
- validate_config() checks I2C bus parameter
- Graceful handling of sensor communication errors
- Proper logging of sensor status
**Tests**:
- Test invalid I2C bus configuration rejection
- Test sensor timeout handling
- Test CRC error handling
**Status**: Not Started

## Stage 5: Optional Commands (do_command)
**Goal**: Implement useful sensor-specific commands
**Success Criteria**:
- Support calibration or reset commands if needed
- Support sensor status queries
**Tests**:
- Test custom commands work correctly
- Test command error handling
**Status**: Not Started
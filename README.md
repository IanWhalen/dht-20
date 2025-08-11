# Module dht-20 

A Viam module for the DHT-20 temperature and humidity sensor with I2C communication.

## Model ianwhalen:dht-20:dht-20

The DHT-20 is a low-cost, high-accuracy digital temperature and humidity sensor that communicates over I2C. This module provides a Viam sensor component interface for reading temperature (in Celsius) and relative humidity (as percentage).

### Configuration
The following attribute template can be used to configure this model:

```json
{
  "i2c_bus": 1
}
```

#### Attributes

The following attributes are available for this model:

| Name      | Type | Inclusion | Description                                    |
|-----------|------|-----------|------------------------------------------------|
| `i2c_bus` | int  | Optional  | I2C bus number (default: 1, typically for Raspberry Pi) |

#### Example Configuration

```json
{
  "i2c_bus": 1
}
```

### Sensor Readings

The sensor returns the following readings via `get_readings()`:

- `temperature_celsius`: Temperature in degrees Celsius (-40 to 80°C range)
- `humidity_percent`: Relative humidity as percentage (0-100%)

### DoCommand

This model implements DoCommand with diagnostic commands:

#### get_status

Returns the sensor connection status and I2C bus information.

```json
{
  "command": "get_status"
}
```

#### get_raw_data

Returns raw sensor data bytes for debugging purposes.

```json
{
  "command": "get_raw_data"
}
```

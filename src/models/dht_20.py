import time
from typing import (Any, ClassVar, Mapping, Sequence, Tuple)

from typing_extensions import Self
from viam.components.sensor import *
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import Geometry, ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.utils import SensorReading, ValueTypes

try:
    import smbus2
except ImportError:
    smbus2 = None


class Dht20(Sensor, EasyResource):
    """DHT-20 Temperature and Humidity Sensor Component"""
    
    # DHT-20 Constants
    DHT20_I2C_ADDRESS = 0x38
    DHT20_CMD_INIT = 0x71
    DHT20_CMD_MEASURE = 0xAC
    DHT20_MEASURE_PARAMS = [0x33, 0x00]
    DHT20_MEASURE_DELAY = 0.1  # 100ms measurement delay
    MODEL: ClassVar[Model] = Model(ModelFamily("ianwhalen", "dht-20"), "dht-20")

    def __init__(self, name: str):
        super().__init__(name)
        self.i2c_bus: smbus2.SMBus | None = None
        self.i2c_bus_number: int = 1  # Default I2C bus

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Sensor component.
        The default implementation sets the name from the `config` parameter and then calls `reconfigure`.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both required and optional)

        Returns:
            Self: The resource
        """
        return super().new(config, dependencies)

    @classmethod
    def validate_config(
        cls, config: ComponentConfig
    ) -> Tuple[Sequence[str], Sequence[str]]:
        """Validate the configuration for DHT-20 sensor.
        
        Expected config attributes:
        - i2c_bus (optional): I2C bus number (default: 1)

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Tuple[Sequence[str], Sequence[str]]: A tuple where the
                first element is a list of required dependencies and the
                second element is a list of optional dependencies
        """
        # Check if smbus2 is available
        if smbus2 is None:
            raise ValueError("smbus2 library is required for DHT-20 sensor")
        
        # Validate I2C bus configuration
        if hasattr(config, "attributes") and config.attributes:
            i2c_bus = config.attributes.get("i2c_bus")
            if i2c_bus is not None:
                if not isinstance(i2c_bus, int) or i2c_bus < 0:
                    raise ValueError("i2c_bus must be a non-negative integer")
        
        return [], []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """Configure the DHT-20 sensor with I2C settings.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any dependencies (both required and optional)
        """
        # Close existing I2C connection if any
        if self.i2c_bus is not None:
            try:
                self.i2c_bus.close()
            except Exception as e:
                self.logger.warning(f"Error closing I2C bus: {e}")
            finally:
                self.i2c_bus = None
        
        # Get I2C bus number from configuration
        if hasattr(config, "attributes") and config.attributes:
            self.i2c_bus_number = config.attributes.get("i2c_bus", 1)
        
        # Initialize I2C connection
        try:
            self.i2c_bus = smbus2.SMBus(self.i2c_bus_number)
            self.logger.info(f"DHT-20 initialized on I2C bus {self.i2c_bus_number}")
            
            # Check if sensor is present and responsive
            self._check_sensor_presence()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize DHT-20 sensor: {e}")
            raise
        
        return super().reconfigure(config, dependencies)

    def _check_sensor_presence(self):
        """Check if DHT-20 sensor is present and properly initialized."""
        if self.i2c_bus is None:
            raise RuntimeError("I2C bus not initialized")
        
        try:
            # Read initialization status
            time.sleep(0.5)  # Allow sensor to stabilize
            data = self.i2c_bus.read_i2c_block_data(self.DHT20_I2C_ADDRESS, self.DHT20_CMD_INIT, 1)
            
            # Check if sensor is initialized (bit 3 should be 1)
            if (data[0] | 0x08) == 0:
                self.logger.warning("DHT-20 sensor initialization status indicates error")
                # Note: We don't raise here as some sensors may still work
            else:
                self.logger.debug("DHT-20 sensor initialization check passed")
                
        except Exception as e:
            raise RuntimeError(f"DHT-20 sensor not responding at address 0x{self.DHT20_I2C_ADDRESS:02x}: {e}")

    def close(self):
        """Clean up I2C resources."""
        if self.i2c_bus is not None:
            try:
                self.i2c_bus.close()
                self.logger.debug("I2C bus closed")
            except Exception as e:
                self.logger.warning(f"Error closing I2C bus: {e}")
            finally:
                self.i2c_bus = None

    def _read_sensor_data(self) -> Tuple[float, float]:
        """Read temperature and humidity from DHT-20 sensor.
        
        Returns:
            Tuple[float, float]: Temperature in Celsius, Humidity as percentage
            
        Raises:
            RuntimeError: If sensor communication fails
        """
        if self.i2c_bus is None:
            raise RuntimeError("I2C bus not initialized")
        
        try:
            # Send measurement command
            self.i2c_bus.write_i2c_block_data(
                self.DHT20_I2C_ADDRESS, 
                self.DHT20_CMD_MEASURE, 
                self.DHT20_MEASURE_PARAMS
            )
            
            # Wait for measurement to complete
            time.sleep(self.DHT20_MEASURE_DELAY)
            
            # Read 7 bytes of data
            data = self.i2c_bus.read_i2c_block_data(self.DHT20_I2C_ADDRESS, self.DHT20_CMD_INIT, 7)
            
            # Parse temperature data (20-bit value)
            temp_raw = ((data[3] & 0xf) << 16) + (data[4] << 8) + data[5]
            temperature = (200.0 * float(temp_raw) / (2**20)) - 50.0
            
            # Parse humidity data (20-bit value)
            humid_raw = ((data[3] & 0xf0) >> 4) + (data[1] << 12) + (data[2] << 4)
            humidity = 100.0 * float(humid_raw) / (2**20)
            
            # Validate readings are within reasonable ranges
            if temperature < -40 or temperature > 80:
                self.logger.warning(f"Temperature reading out of expected range: {temperature}°C")
            if humidity < 0 or humidity > 100:
                self.logger.warning(f"Humidity reading out of expected range: {humidity}%")
            
            self.logger.debug(f"DHT-20 reading: {temperature:.2f}°C, {humidity:.2f}%")
            return temperature, humidity
            
        except Exception as e:
            raise RuntimeError(f"Failed to read DHT-20 sensor data: {e}")

    async def get_readings(
        self,
        *,
        extra: Mapping[str, Any] | None = None,
        timeout: float | None = None,
        **kwargs
    ) -> Mapping[str, SensorReading]:
        """Get temperature and humidity readings from DHT-20 sensor.
        
        Returns:
            Mapping[str, SensorReading]: Dictionary containing:
                - "temperature_celsius": Temperature in Celsius
                - "humidity_percent": Relative humidity as percentage
        """
        try:
            temperature, humidity = self._read_sensor_data()
            
            return {
                "temperature_celsius": temperature,
                "humidity_percent": humidity
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get DHT-20 readings: {e}")
            raise

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: float | None = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        """Execute custom commands for DHT-20 sensor.
        
        Supported commands:
        - "get_status": Returns sensor connection status
        - "get_raw_data": Returns raw sensor data bytes
        """
        cmd_name = command.get("command")
        
        if cmd_name == "get_status":
            try:
                self._check_sensor_presence()
                return {"status": "ok", "i2c_bus": self.i2c_bus_number}
            except Exception as e:
                return {"status": "error", "error": str(e)}
        
        elif cmd_name == "get_raw_data":
            try:
                # Send measurement command and get raw bytes
                self.i2c_bus.write_i2c_block_data(
                    self.DHT20_I2C_ADDRESS,
                    self.DHT20_CMD_MEASURE,
                    self.DHT20_MEASURE_PARAMS
                )
                time.sleep(self.DHT20_MEASURE_DELAY)
                data = self.i2c_bus.read_i2c_block_data(self.DHT20_I2C_ADDRESS, self.DHT20_CMD_INIT, 7)
                return {"raw_bytes": [hex(b) for b in data]}
            except Exception as e:
                return {"error": str(e)}
        
        else:
            return {"error": f"Unknown command: {cmd_name}"}

    async def get_geometries(
        self, *, extra: dict[str, Any] | None = None, timeout: float | None = None
    ) -> list[Geometry]:
        """DHT-20 sensor has no physical geometry to report."""
        return []


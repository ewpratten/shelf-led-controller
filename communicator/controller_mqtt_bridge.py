import argparse
import sys
import logging
import json
import serial
import time
from ha_mqtt_discoverable import Settings
from ha_mqtt_discoverable.sensors import Light, LightInfo
from paho.mqtt.client import Client, MQTTMessage

logger = logging.getLogger(__name__)


def light_data_callback(client: Client, userdata: Light, message: MQTTMessage, serial_connection: serial.Serial):
    # Parse the incoming message
    try: 
        data = json.loads(message.payload.decode())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode message: {e}")
        return
    
    # If the payload is trying to set the light state, handle it
    if "state" in data:
        if data["state"] == "ON":
            logger.info("Turning on the light")
            pass
        else:
            logger.info("Turning off the light")
            serial_connection.write(b"0\n")       
            
    # If we have a color payload, handle it
    if "color" in data:
        logger.info(f"Setting color to {data['color']}")
        r = data["color"]["r"]
        g = data["color"]["g"]
        b = data["color"]["b"]
        w = data["color"]["w"]
        
        # Pack into a uint32
        color = (w << 24) | (r << 16) | (g << 8) | b
        logger.info(f"Packed color: {color}")
        
        # Send the color to the light
        serial_connection.write(f"{color}\n".encode())


def main() -> int:
    # Handle program arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("--serial", help="Serial port", default="/dev/ttyUSB0")
    ap.add_argument("--host", help="MQTT broker host", default="controller.home")
    ap.add_argument("--port", help="MQTT broker port", type=int, default=1883)
    ap.add_argument("--username", help="MQTT broker username")
    ap.add_argument("--password", help="MQTT broker password")
    ap.add_argument(
        "-v", "--verbose", help="Enable verbose logging", action="store_true"
    )
    args = ap.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s:	%(message)s",
    )

    # Make an MQTT connection
    mqtt = Settings.MQTT(
        host=args.host, port=args.port, username=args.username, password=args.password
    )
    
    # Make a serial connection
    serial_connection = serial.Serial(args.serial, 9600, timeout=1)

    # Create the light obj
    shelf_light = Light(
        Settings(
            mqtt=mqtt,
            entity=LightInfo(
                name="Evan's Shelf Light",
                color_mode=True,
                supported_color_modes=["rgbw"],
            ),
        ),
        lambda c, u, m: light_data_callback(c, u, m, serial_connection),
    )

    # Set the initial state of the light
    shelf_light.off()
    
    # Run forever
    while True:         
        # Read a line
        line = serial_connection.readline()
        
        # Handle the command
        if line.strip() == "OFF":
            logger.info("Light is off")
            shelf_light.off()
        elif line.strip() == "ON":
            logger.info("Light is on")
            shelf_light.on()
        else:
            color = int(line.strip())
            w = (color & 0b11000000) >> 6
            r = (color & 0b00110000) >> 4
            g = (color & 0b00001100) >> 2
            b = (color & 0b00000011)
            logger.info(f"Color: {r}, {g}, {b}, {w}")
            shelf_light.set_color("rgbw", {"r": r, "g": g, "b": b, "w": w})
        
        

    return 0


if __name__ == "__main__":
    sys.exit(main())

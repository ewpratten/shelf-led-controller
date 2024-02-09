# LED controller for my bookshelf

This is the new source code for the LED controller I talked about in [this blog post](https://ewpratten.com/blog/shelf-lights/). 

In the time since writing that post, I've decided to replace the button-based control with a bit of Python code that allows my lights to be controlled via MQTT from Home Assistant.

## Deployment notes

The `led_controller_fw` subdirectory contains the firmware for the ATMega32U4 that controls the LEDs. The `communicator` subdirectory contains Python code that talks to the controller over Serial.

The `communicator` is run as a SystemD service on a nearby machine.

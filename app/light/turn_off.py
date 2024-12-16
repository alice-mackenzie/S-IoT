# turn_off.py
import board
import neopixel

# Configuration
NUM_LEDS_RING1 = 24
NUM_LEDS_RING2 = 16
TOTAL_LEDS = NUM_LEDS_RING1 + NUM_LEDS_RING2
DATA_PIN = board.D18

# Initialize the LED strip
pixels = neopixel.NeoPixel(DATA_PIN, TOTAL_LEDS, brightness=0.5, auto_write=False)

def turn_off():
    # Turn off all LEDs
    pixels.fill((0, 0, 0))
    pixels.show()

if __name__ == "__main__":
    turn_off()

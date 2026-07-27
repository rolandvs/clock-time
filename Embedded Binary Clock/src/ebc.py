"""
Embedded Binary Clock using WS2812 (DS2812) LED strip
24 LEDs arranged in 4 rows of 6 LEDs each
Displays time in 24-hour format with binary representation
"""

from machine import Pin
import neopixel
import time

# Configuration
NUM_LEDS = 24
LED_PIN = Pin.board.X1  # Change this to match the actual pin

# Colors
COLOR_OFF = (32, 32, 32)    # Dimmed white when bit is 0
COLOR_ON = (255, 0, 0)      # Red when bit is 1
COLOR_BRIGHTNESS = 0.3      # Global brightness multiplier

# LED mapping - indices in the strip
# Row 0: LEDs 0-5   -> ht0 hu0 mt0 mu0 st0 su0
# Row 1: LEDs 6-11  -> ht1 hu1 mt1 mu1 st1 su1
# Row 2: LEDs 12-17 -> ht2 hu2 mt2 mu2 st2 su2
# Row 3: LEDs 18-23 -> ht3 hu3 mt3 mu3 st3 su3

class BinaryClock:
    def __init__(self, pin, num_leds=24):
        self.np = neopixel.NeoPixel(pin, num_leds)
        self.num_leds = num_leds
        
        # Apply brightness to colors
        self.color_off = tuple(int(c * COLOR_BRIGHTNESS) for c in COLOR_OFF)
        self.color_on = tuple(int(c * COLOR_BRIGHTNESS) for c in COLOR_ON)
        
    def set_led(self, row, col, state):
        """
        Set LED state at given row and column
        row: 0-3 (bit position in binary)
        col: 0-5 (ht, hu, mt, mu, st, su)
        state: True (red/on) or False (dimmed white/off)
        """
        led_index = row * 6 + col
        if 0 <= led_index < self.num_leds:
            self.np[led_index] = self.color_on if state else self.color_off
    
    def decimal_to_binary_bcd(self, value, digits=2):
        """
        Convert decimal to BCD (Binary Coded Decimal)
        Returns list of bits [bit3, bit2, bit1, bit0] for each digit
        """
        tens = value // 10
        units = value % 10
        
        # Get 4 bits for each digit (only need 4 bits for 0-9)
        tens_bits = [(tens >> i) & 1 for i in range(4)]
        units_bits = [(units >> i) & 1 for i in range(4)]
        
        return tens_bits, units_bits
    
    def update_time(self, hours, minutes, seconds):
        """
        Update the binary clock display with current time
        hours: 0-23, minutes: 0-59, seconds: 0-59
        """
        # Get BCD representation
        h_tens_bits, h_units_bits = self.decimal_to_binary_bcd(hours)
        m_tens_bits, m_units_bits = self.decimal_to_binary_bcd(minutes)
        s_tens_bits, s_units_bits = self.decimal_to_binary_bcd(seconds)
        
        # Update all LEDs
        for row in range(4):
            # Hours
            self.set_led(row, 0, bool(h_tens_bits[row]))
            self.set_led(row, 1, bool(h_units_bits[row]))
            # Minutes
            self.set_led(row, 2, bool(m_tens_bits[row]))
            self.set_led(row, 3, bool(m_units_bits[row]))
            # Seconds
            self.set_led(row, 4, bool(s_tens_bits[row]))
            self.set_led(row, 5, bool(s_units_bits[row]))
        
        self.np.write()
    
    def clear(self):
        """Clear all LEDs to off state (dimmed white)"""
        for i in range(self.num_leds):
            self.np[i] = self.color_off
        self.np.write()
    

def main():

    print("Binary Clock Starting...")
    
    try:
        clock = BinaryClock(LED_PIN, NUM_LEDS)
    except Exception as e:
        print(f"Error initializing NeoPixel: {e}")
        print("Make sure to set the correct LED_PIN at the top of the file")
        return
        
    clock.clear()
    
    try:
        from machine import RTC
        rtc = RTC()
        print("Using hardware RTC")
    except:
        print("RTC not available, using time.localtime()")
        rtc = None
    
    print("Clock running... (Press Ctrl+C to stop)")
    print()
    
    # Main loop
    try:
        while True:
            # Get current time
            if rtc:
                # RTC returns: (year, month, day, weekday, hours, minutes, seconds, subseconds)
                current_time = rtc.datetime()
                hours = current_time[4]
                minutes = current_time[5]
                seconds = current_time[6]
            else:
                # Use time.localtime()
                current_time = time.localtime()
                hours = current_time[3]
                minutes = current_time[4]
                seconds = current_time[5]
            
            clock.update_time(hours, minutes, seconds)
            
            # Print time
            print(f"\r{hours:02d}:{minutes:02d}:{seconds:02d}", end="")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nClock stopped")
        clock.clear()
        print("Display cleared")


if __name__ == "__main__":
    main()
```

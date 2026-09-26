# Detector/EXACT setup guide
Assumes you have the following equipment:
- DS3231 real-time clock or other 1Hz square wave source
- Bridgeport board + SiPMs + scintillator with the NRL list mode firwmare
- RPi CM3+ or other compatible device
- Radioactive source (for some later steps)

## Build and install [Nebula](https://github.com/UMN-SSRL/Nebula)
### 📝 Serial numbers can be modified in `/etc/environment` if necessary.

## If necessary: Configure the DS3231 clock as a fake PPS source
### ⚠️ If you are yousing a real GPS for the PPS, the configuration will be completely different. ⚠️

The RTC data sheet is here: [DS3231 data sheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ds3231.pdf).
It contains a pinout for the chip if you want to start from scratch.

**⚠️ The strobe output by the DS3231 needs to be [buffered](https://en.wikipedia.org/wiki/Buffer_amplifier) (not shown in photo below).⚠️**

In lab we have it set up on a bread board.
It is powered from the Pi I/O board,
    and the SDA and SCL I2C lines are connected appropriately.
The SQW output from the data sheet is connected to 3.3V via a pull-up resistor,
    and the output available for other devices to connect to.
The SQW output needs to go to GPIO S0 on the detector,
    and to GPIO pin 31 on the Pi.
![rtc](rtc.png)

run `i2cdetect -y 1` to make sure the clock is properly connected.
You should see address 68 pop up.

To configure its square wave output, run the following Python snippet on the Pi.
Save it to a file and then run it from the shell. Thanks, ChatGPT
```py
import smbus

# Constants
I2C_BUS = 1                # Default I2C bus on CM3+
DS3231_ADDRESS = 0x68      # I2C address of the DS3231
REG_CONTROL = 0x0E         # Control register
REG_STATUS = 0x0F          # Status register

# Square wave rate options:
# 00 = 1 Hz, 01 = 1024 Hz, 10 = 4096 Hz, 11 = 8192 Hz
RS1 = 0
RS2 = 0

# Enable square wave output:
# EOSC = 0 (oscillator on)
# BBSQW = 0 (not needed unless Vbat only)
# CONV = 0 (no conversion)
# RS2/RS1 = 00 (1 Hz)
# INTCN = 0 (square wave mode)
control_byte = (RS2 << 4) | (RS1 << 3)

bus = smbus.SMBus(I2C_BUS)

# Read current control register value (optional)
original_control = bus.read_byte_data(DS3231_ADDRESS, REG_CONTROL)
print(f"Original control register: 0x{original_control:02X}")

# Write new control value to enable 1 Hz square wave
bus.write_byte_data(DS3231_ADDRESS, REG_CONTROL, control_byte)

# Verify new control value
new_control = bus.read_byte_data(DS3231_ADDRESS, REG_CONTROL)
print(f"New control register: 0x{new_control:02X}")

bus.close()
```

Once you run the snippet,
    check that the square wave output is working with either an oscilloscope or multimeter.
The multimeter will flash between 0V and 3.3V at about a 1 second period.
If you use the oscilloscope, be sure to DC couple it.

## Begin data acquisition
Run `det_start_exact_sci`.
Files will accumulate in `/SAT/LIVE/DET-SCI`,
    and will be transferred to the ground station if norm is proprely configured.

## Data Analysis -- see `python/examples`.
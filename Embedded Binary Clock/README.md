
![EMBEDDED BIN CLOCK](/Embedded%20Binary%20Clock/doc/bin_clock.png)

Booting the system will run the clock. The RTC time is believed to be (set) correct(ly). The REPL output:

# LED Layout

```
Row 0: ht0 hu0 mt0 mu0 st0 su0
Row 1: ht1 hu1 mt1 mu1 st1 su1
Row 2: ht2 hu2 mt2 mu2 st2 su2
Row 3: ht3 hu3 mt3 mu3 st3 su3
```

# REPL Output

```
MPY: sync filesystems
MPY: soft reboot
Binary Clock Starting...

Using hardware RTC
Clock running... (Press Ctrl+C to stop)

22:13:06
```

# Code
The program `ebc.py` itself is easy enough. It uses the `neopixel` library that comes with micropython.

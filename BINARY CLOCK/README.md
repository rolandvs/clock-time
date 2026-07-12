# BINARY CLOCK

This repository is a binary clock using **PyQt5** and as such a demo of using "QT5".

![binary clock](doc/bin_clock.png)

The clock uses unicode characters to form a binary clock display. The clock shows the current time in binary format using colored circles for bits.

By setting `ReadableClock` to `True`, the clock will also display the current time below the binary representation.

The screen geometry is set to `800x800` pixels, and the background color is black.  The binary clock uses red circles for '1' bits and green circles for '0' bits, with  white circles as padding for alignment.

The size is set to accomodate a round 800x800 LCD display used on a Raspberry Pi. Its use is not limited to the RASPI, but works equally well on any system that support vanilla python3 with the PyQt5 library.

Using `<ctrl-c>` is handled differently in PyQt5, therefore the `signal` module is added.


## Install
Ideally setup a directory with the necessary libraries using `venv`. Following a short way to install and use it:

```bash
$ mkdir test
$ cd test
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install PyQt5
(venv) $ python3 -m bin_clock
(venv) $ deactivate
$
```

## Run the program

```
$ python3 -m bin_clock
```

___

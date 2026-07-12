"""
    Binary Clock GUI using PyQt5

    Output using unicode characters to form a binary clock display.
    The clock shows the current time in binary format using colored circles for bits.

    By setting `ReadableClock` to True, the clock will also display the current time
    below the binary representation.

    The screen geometry is set to 800x800 pixels, and the background color is black. 
    The binary clock uses red circles for '1' bits and green circles for '0' bits, with 
    white circles as padding for alignment.

    The size is set to accomodate a round 800x800 LCD display used on a Raspberry Pi. Its use
    is not limited to the RASPI, but works equally well on any system that support vanilla python3
    with the PyQt5 library.

    Using <ctrl-c> is handled differently in PyQt5, therefore the signal module is added.

    Author: Roland van Straten
    License: MIT License
    Date: 2024-06-15
    
"""


import sys
import signal
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt


ReadableClock = True  # Set to True to display the readable clock


class BinaryClock(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Binary Clock")
        self.setGeometry(100, 100, 800, 800)
        self.setStyleSheet("background-color: black;")
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Single QLabel for all characters
        self.label = QLabel("", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            "color: black; font-size: 24px; font-family: 'Courier New', monospace;"
        )
        layout.addWidget(self.label)

        if ReadableClock:
            self.time_label = QLabel("", self)
            self.time_label.setAlignment(Qt.AlignCenter)
            self.time_label.setStyleSheet(
                "color: red; font-size: 64px; font-family: 'Courier New', monospace; font-weight: bold;"
            )
            layout.addWidget(self.time_label)
        
        # Bits per column (tensH, unitsH, tensM, unitsM, tensS, unitsS)
        self.column_bits = [2, 4, 3, 4, 3, 4]
        
        # Timer to update every second
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
        self.update_clock()
    
    def update_clock(self):
        now = datetime.now()
        h, m, s = now.hour, now.minute, now.second
        
        digits = [
            h // 10, h % 10,
            m // 10, m % 10,
            s // 10, s % 10
        ]
        
        max_rows = max(self.column_bits)
        lines = []
        
        # Build from top row (MSB) to bottom row (LSB)
        for row in range(max_rows):
            line = ""
            for col, value in enumerate(digits):
                bits = self.column_bits[col]
                empty_rows = max_rows - bits
                if row < empty_rows:
                    line += "⚪"  # pad top for short columns
                else:
                    # Bottom-to-top counting
                    bit_index = bits - 1 - (row - empty_rows)
                    bit = (value >> bit_index) & 1
                    line += "🔴" if bit else "🟢"
                line += "⚪"  # space between columns
            lines.append(line)
        self.label.setText("\n".join(lines))
                
        if ReadableClock:
            self.time_label.setText(f"{h:02d}:{m:02d}:{s:02d}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Handle SIGINT (Ctrl+C) to gracefully exit the application
    signal.signal(signal.SIGINT, lambda *args: app.quit())

    clock = BinaryClock()
    clock.show()
    sys.exit(app.exec_())

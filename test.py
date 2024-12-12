from escpos.printer import Serial
from time import *
from datetime import datetime
now = datetime.now()

dt_string = now.strftime("%b/%d/%Y %H:%M:%S")
print("Today's date:", dt_string)

p = Serial(devfile='/dev/serial0',
           baudrate=9600,
           bytesize=8,
           parity='N',
           stopbits=1,
           timeout=1.00,
           dsrdtr=True
)
p.set(
        underline=0,
        align="left",
        font="a",
        width=2,
        height=2,
        density=3,
        invert=0,
        smooth=False,
        flip=False,
)
p.text("\n")
p.set(
        underline=0,
        align="center",
        font="a",
        width=2,
        height=2,
        density=2,
        invert=0,
        smooth=False,
        flip=False,
)

p.set(
        underline=0,
        align="left",
)
p.textln("CIRCUIT DIGEST\n")
p.text("AIRPORT ROAD\n")
p.text("LOCATION : JAIPUR\n")
p.text("TEL : 0141222585\n")
p.text("GSTIN : \n")
p.text("Bill No. : \n\n")
p.set(
        underline=0,
        align="left",
        font="a",
        width=2,
        height=2,
        density=2,
        invert=0,
        smooth=False,
        flip=False,   
)
# print the date and time of printing every time
p.text("DATE : ")
p.text(dt_string)

print("done")
from escpos.printer import Serial

printer = Serial(
            devfile='/dev/serial0',
            baudrate=9600,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1.00,
            dsrdtr=True
        )

printer.set(
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
printer.text('\n')
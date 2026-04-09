#!/bin/sh

if [ -f "${KLIPPER_DIR}/klippy/extras/ifs_jacker.py" ]; then
    echo "IFS Jacker plugin updated"
    echo "REBOOT" >/tmp/printer
fi

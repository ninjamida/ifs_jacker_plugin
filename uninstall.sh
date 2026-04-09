#!/bin/sh

source /opt/config/mod/.shell/0.sh

if [ -f "${KLIPPER_DIR}/klippy/extras/ifs_jacker.py" ]; then
    rm ${KLIPPER_DIR}/klippy/extras/ifs_jacker.py
fi

echo "IFS Jacker plugin uninstalled"
echo "REBOOT" >/tmp/printer

#!/bin/sh

source /opt/config/mod/.shell/0.sh

if [ -f "${KLIPPER_DIR}/klippy/extras/ifs_jacker_plugin.py" ]; then
    rm ${KLIPPER_DIR}/klippy/extras/ifs_jacker_plugin.py
fi

echo "IFS Jacker plugin uninstalled"
echo "REBOOT" >/tmp/printer

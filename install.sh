#!/bin/sh

source /opt/config/mod/.shell/0.sh


if [ ! -f "${KLIPPER_DIR}/klippy/extras/ifs_jacker_plugin.py" ]; then
    ln -s ${MOD_CONF}/mod_data/plugins/ifs_jacker_plugin/ifs_jacker_plugin.py ${KLIPPER_DIR}/klippy/extras/ifs_jacker_plugin.py
fi

echo "IFS Jacker plugin installed"
echo "REBOOT" >/tmp/printer

#!/bin/sh

source /opt/config/mod/.shell/0.sh

if [ ! -f "${KLIPPER_DIR}/klippy/extras/ifs_jacker.py" ]; then
    ln -s ${MOD_CONF}/mod_data/plugins/ifs_jacker/ifs_jacker.py ${KLIPPER_DIR}/klippy/extras/ifs_jacker.py
fi
if [ ! -f "${KLIPPER_DIR}/klippy/extras/ifs_jacker_temperature_sensor.py" ]; then
    ln -s ${MOD_CONF}/mod_data/plugins/ifs_jacker/ifs_jacker_temperature_sensor.py ${KLIPPER_DIR}/klippy/extras/ifs_jacker_temperature_sensor.py
fi
if [ ! -f "${KLIPPER_DIR}/klippy/extras/ifs_jacker_fan.py" ]; then
    ln -s ${MOD_CONF}/mod_data/plugins/ifs_jacker/ifs_jacker_fan.py ${KLIPPER_DIR}/klippy/extras/ifs_jacker_fan.py
fi
if [ ! -f "${KLIPPER_DIR}/klippy/extras/ifs_jacker_led.py" ]; then
    ln -s ${MOD_CONF}/mod_data/plugins/ifs_jacker/ifs_jacker_led.py ${KLIPPER_DIR}/klippy/extras/ifs_jacker_led.py
fi

echo "IFS Jacker plugin installed"
echo "REBOOT" >/tmp/printer

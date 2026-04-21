#!/bin/sh

source /opt/config/mod/.shell/0.sh

SOURCE_DIR="${MOD_CONF}/mod_data/plugins/ifs_jacker"
TARGET_DIRS="${MOD_CONF}/base/klipper/klippy/extras ${KLIPPER_DIR}/klippy/extras"

for file in "$SOURCE_DIR"/*.py; do
    [ -e "$file" ] || continue
    filename=$(basename "$file")
    for target in $TARGET_DIRS; do
        target_path="$target/$filename"
        if [ ! -e "$target_path" ]; then
            ln -s "$file" "$target_path"
        fi
    done
done

CFG_FILE="${MOD_CONF}/mod_data/user_ifs_jacker.cfg"
if [ ! -e "${CFG_FILE}" ]; then
    printf "# This cfg file will only be loaded when the IFS Jacker plugin is active.\n# It is otherwise just a standard Klipper cfg file.\n# Please note user.cfg has priority over this file if a parameter is defined in both.\n" > "${CFG_FILE}"
fi

echo "IFS Jacker plugin installed"
echo "REBOOT" >/tmp/printer

Plugin to accompany an IFS Jacker device:

https://github.com/ninjamida/ifs-jacker
https://www.printables.com/model/1644745-ifs-jacker

Requires zMod. It also requires the contents of this PR; if it has not yet been
merged, you will need to manually merge it into your copy of Z-Mod:

https://github.com/ghzserg/z_ad5x/pull/8

You will need to manually add this to your Z-Mod plugins. Add the following to
user.moonraker.conf in mod_data:

[update_manager ifs_jacker]
type: git_repo
channel: stable
path: /root/printer_data/config/mod_data/plugins/ifs_jacker
origin: https://github.com/ninjamida/ifs_jacker_plugin.git
is_system_service: False
primary_branch: master
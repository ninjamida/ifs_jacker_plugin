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


If you have this plugin installed but have a normal IFS (rather than an IFS
Jacker) connected, your IFS will disconnect a few times when zMod is starting
up. After the third time, it should stop doing so. This is because of it sending
a command intended to detect an IFS Jacker, which a regular IFS cannot respond
to, and thus zMod interprets it as a disconnect. After three failed attempts,
the plugin stops performing this check until the IFS is disconnected and
reconnected or the printer is rebooted.

If you are reverting to a regular IFS long-term, it is better to disable the
IFS Jacker plugin.

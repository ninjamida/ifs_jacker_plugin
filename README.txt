Z-Mod plugin to accompany an IFS Jacker device:

https://github.com/ninjamida/ifs-jacker
https://www.printables.com/model/1644745-ifs-jacker

You will need to manually add this to your Z-Mod plugins. Add the following to
user.moonraker.conf in mod_data:

[update_manager ifs_jacker]
type: git_repo
channel: stable
path: /root/printer_data/config/mod_data/plugins/ifs_jacker
origin: https://github.com/ninjamida/ifs_jacker_plugin.git
is_system_service: False
primary_branch: master

Every time you update this plugin, you should re-run the ENABLE_PLUGIN macro for
it. This is for two reasons - there may be new scripts to install (this plugin
installs Python scripts in addition to the usual CFG files) which the install
script needs to handle; and a reboot is generally necessary after updates which
the install script also triggers.
  ENABLE_PLUGIN NAME=ifs_jacker


If you have this plugin installed but have a normal IFS (rather than an IFS
Jacker) connected, your IFS will disconnect a few times when zMod is starting
up. After the third time, it should stop doing so. This is because of it sending
a command intended to detect an IFS Jacker, which a regular IFS cannot respond
to, and thus zMod interprets it as a disconnect. After three failed attempts,
the plugin stops performing this check until the IFS is disconnected and
reconnected or the printer is rebooted.

If you are reverting to a regular IFS long-term, it is better to disable the
IFS Jacker plugin.

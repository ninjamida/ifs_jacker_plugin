import logging

class ifs_jacker_led:
    def __init__(self, config):
        # Begin general IFS Jacker peripheral code #
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.reactor = self.printer.get_reactor()
        self.gcode = self.printer.lookup_object('gcode')

        self.zmod_ifs = None
        self.ifs_jacker = None

        self.printer.register_event_handler("klippy:ready", self._handle_ready)

        self.peripheral_index = config.getint('peripheral_index')
        # End general IFS Jacker peripheral code #
        
        self.pled = self.printer.load_object(config, "led")
        self.led_helper = self.pled.setup_helper(config, self.update_leds)
        
        self.printer.add_object("led " + self.name, self)

    def _handle_ready(self):
        # Begin general IFS Jacker peripheral code #
        self.zmod_ifs = self.printer.lookup_object('zmod_ifs')
        self.ifs_jacker = self.printer.lookup_object('ifs_jacker')
        # End general IFS Jacker peripheral code #
        self._hijack_config()        

    # Begin general IFS Jacker peripheral code #
    def get_status_params(self):
        if not self.ifs_jacker or self.peripheral_index < 0 or self.peripheral_index >= len(self.ifs_jacker.peripheral_states):
            return {}
        else:
            return self.ifs_jacker.peripheral_states[self.peripheral_index]
    # End general IFS Jacker peripheral code #
        
    def _hijack_config(self):
        # Since a lot of third-party stuff (Fluidd, HelixScreen, etc) don't play nice with custom LEDs, we have to
        # add a dummy config section post-load that they'll read from.
        configfile = self.printer.lookup_object('configfile')
        section_name = f'led {self.name}'
        if section_name in configfile.status_settings: # Which it should never actually be
            target_settings = configfile.status_settings[section_name]
        else:
            target_settings = {}
            configfile.status_settings[section_name] = target_settings
            
        target_settings['color_order'] = 'W'
        
    def update_leds(self, led_state, print_time):
        self.set_color(led_state[0])

    def set_color(self, color):
        if self.ifs_jacker and self.ifs_jacker.ifs_jacker_present:
            self.color = color
            put_data = max(0, min(65535, int(65535 * color[3])))
            self.zmod_ifs.send_command_and_wait(f"Z5 C{self.peripheral_index} F3 L{put_data}")

    def get_status(self, eventtime=None):
        color = [0.0] * 4
        if self.ifs_jacker and self.ifs_jacker.ifs_jacker_present:
            params = self.get_status_params()
            try:
                power = int(params.get('power')) / 65535
            except:
                logging.info(f"IFS Jacker: Exception reading {self.name}, param value '{params.get('power', '<none>')}'")
                power = 0
        else:
            power = 0
        color = [power] * 4            
        self.led_helper.led_state = [color]
        return self.led_helper.get_status(eventtime)
        

def load_config_prefix(config):
    return ifs_jacker_led(config)
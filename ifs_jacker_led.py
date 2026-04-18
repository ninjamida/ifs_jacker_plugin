class ifs_jacker_led:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.gcode = self.printer.lookup_object('gcode')
        self.peripheral_index = config.getint('peripheral_index')
        self.kind = config.get('kind', 'mono') # 'mono', 'rgb', 'rgbw'
        _ = config.get('color_order')
        
        self.pled = self.printer.load_object(config, "led")
        self.led_helper = self.pled.setup_helper(config, self.update_leds)

        self.zmod_ifs = None
        self.ifs_jacker = None
        
        self.printer.register_event_handler("klippy:ready", self._handle_ready)
        self.printer.add_object("led " + self.name, self)        
        
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
            
        if self.kind == 'rgbw':
            new_order = 'RGBW'
        elif self.kind == 'rgb':
            new_order = 'RGB'
        else: # Assume 'mono'
            new_order = 'W'
            
        target_settings['color_order'] = new_order

    def _handle_ready(self):
        self.zmod_ifs = self.printer.lookup_object('zmod_ifs')
        self.ifs_jacker = self.printer.lookup_object('ifs_jacker')
        self._hijack_config()
        
    def update_leds(self, led_state, print_time):
        self.set_color(led_state[0])

    def set_color(self, color):
        if self.ifs_jacker and self.ifs_jacker.ifs_jacker_present:
            self.color = color
            if self.kind == 'rgbw' or self.kind == 'rgb':
                put_data = 0
                for i in reverse(range(len(self.kind))):
                    put_data = (put_data << 8) | max(0, min(255, int(255 * color[i])))
            else: # Assume 'mono'
                put_data = max(0, min(65535, int(65535 * color[3])))
            self.zmod_ifs.send_command_and_wait(f"Z5 C{self.peripheral_index} F3 L{put_data}")

    def get_status(self, eventtime=None):
        color = [0.0] * 4
        if self.ifs_jacker and self.ifs_jacker.ifs_jacker_present:
            if self.peripheral_index < len(self.ifs_jacker.peripheral_states):
                raw_data = int(self.ifs_jacker.peripheral_states[self.peripheral_index])
                if self.kind == 'rgbw' or self.kind == 'rgb':
                    color = [0.0] * 4
                    for i in range(len(self.kind)):
                        color[i] = ((raw_data >> (i * 8)) & 0xFF) / 255
                    if self.kind == 'rgb':
                        color[3] = int((color[0] + color[1] + color[2]) / 3)
                else: # Assume 'mono'
                    brightness = raw_data / 65535
                    color = [brightness] * 4
            
        self.led_helper.led_state = [color]
        return self.led_helper.get_status(eventtime)
        

def load_config_prefix(config):
    return ifs_jacker_led(config)
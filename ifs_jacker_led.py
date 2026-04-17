class ifs_jacker_led:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.gcode = self.printer.lookup_object('gcode')
        self.peripheral_index = config.getint('peripheral_index')

        self.zmod_ifs = None
        self.ifs_jacker = None
        
        self.printer.register_event_handler("klippy:ready", self._handle_ready)
        
        self.printer.add_object("led " + self.name, self)
        self.gcode.register_mux_command("SET_LED", "LED", self.name, self.handle_set_led)
        
        self.color = [0.0, 0.0, 0.0, 0.0]

    def _handle_ready(self):
        self.zmod_ifs = self.printer.lookup_object('zmod_ifs')
        self.ifs_jacker = self.printer.lookup_object('ifs_jacker')

    def handle_set_led(self, gcmd):
        brightness = gcmd.get_float('WHITE', self.color[3], minval=0.0, maxval=1.0)
        brightness = gcmd.get_float('RED', brightness, minval=0.0, maxval=1.0)
        self.set_brightness(brightness)

    def set_brightness(self, brightness):
        if self.ifs_jacker and self.ifs_jacker.ifs_jacker_present:
            self.color = [0.0, 0.0, 0.0, brightness]
            self.zmod_ifs.send_command_and_wait(f"Z5 C{self.peripheral_index} F3 L{int(brightness * 65535)}")

    def get_status(self, eventtime):
        color = [0.0, 0.0, 0.0, 0.0]
        if self.ifs_jacker and self.ifs_jacker.ifs_jacker_present:
            if self.peripheral_index < len(self.ifs_jacker.peripheral_states):
                color = [0.0, 0.0, 0.0, int(self.ifs_jacker.peripheral_states[self.peripheral_index]) / 65535]
        self.color = color
        return {'color_data': [color]}

def load_config_prefix(config):
    return ifs_jacker_led(config)
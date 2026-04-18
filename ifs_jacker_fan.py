class ifs_jacker_fan:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.gcode = self.printer.lookup_object('gcode')
        self.peripheral_index = config.getint('peripheral_index')

        self.zmod_ifs = None
        self.ifs_jacker = None

        self.printer.register_event_handler("klippy:ready", self._handle_ready)

        self.printer.add_object("fan_generic " + self.name, self)
        self.gcode.register_mux_command("SET_FAN_SPEED", "FAN", self.name, self.handle_set_fan_speed)

    def _handle_ready(self):
        self.zmod_ifs = self.printer.lookup_object('zmod_ifs')
        self.ifs_jacker = self.printer.lookup_object('ifs_jacker')
        
    def handle_set_fan_speed(self, gcmd):
        speed = gcmd.get_float('SPEED', 0., minval=0.0, maxval=1.0)
        self.set_speed(speed)

    def set_speed(self, speed):
        if self.ifs_jacker and self.ifs_jacker.ifs_jacker_present:
            self.zmod_ifs.send_command_and_wait(f"Z5 C{self.peripheral_index} F3 L{int(speed * 65535)}")

    def get_speed_from_status(self):
        if self.ifs_jacker and self.ifs_jacker.ifs_jacker_present:
            if self.peripheral_index < len(self.ifs_jacker.peripheral_states):
                return int(self.ifs_jacker.peripheral_states[self.peripheral_index]) / 65535
        return 0

    def get_status(self, eventtime):
        return {'speed': self.get_speed_from_status()}

def load_config_prefix(config):
    return ifs_jacker_fan(config)

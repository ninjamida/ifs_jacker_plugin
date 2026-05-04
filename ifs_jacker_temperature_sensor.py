import logging

class ifs_jacker_temperature_sensor:
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

        self.read_param = config.get('read_param', 'temperature')
    
        self.min_temp = config.getfloat('min_temp', -273.15)
        self.max_temp = config.getfloat('max_temp', 999)

        self.temp = min(self.max_temp, max(self.min_temp, -1.0))
        self.poll_interval = 1.0

        self.printer.add_object("ifs_jacker_temperature_sensor " + self.name, self)
        self.sample_timer = self.reactor.register_timer(self._sample)

    def _handle_ready(self):
        # Begin general IFS Jacker peripheral code #
        self.zmod_ifs = self.printer.lookup_object('zmod_ifs')
        self.ifs_jacker = self.printer.lookup_object('ifs_jacker')
        # End general IFS Jacker peripheral code #

        self.reactor.update_timer(self.sample_timer, self.reactor.NOW)
        self.mcu = self.printer.lookup_object('mcu')

    # Begin general IFS Jacker peripheral code #
    def get_status_params(self):
        if not self.ifs_jacker or self.peripheral_index < 0 or self.peripheral_index >= len(self.ifs_jacker.peripheral_states):
            return {}
        else:
            return self.ifs_jacker.peripheral_states[self.peripheral_index]
    # End general IFS Jacker peripheral code #

    def _sample(self, eventtime):
        if self.ifs_jacker and self.ifs_jacker.ifs_jacker_present:
            params = self.get_status_params()
            try:
                self.temp = float(params.get(self.read_param))
            except:
                logging.info(f"IFS Jacker: Exception reading {self.name}, param value '{params.get(self.read_param, '<none>')}'")
                # Just keep the old value.
        else:
            self.temp = -1.0

        measured_time = self.reactor.monotonic()
        self._callback(self.mcu.estimated_print_time(measured_time), self.temp)

        return eventtime + self.poll_interval

    def setup_minmax(self, min_temp, max_temp):
        self.min_temp = min_temp
        self.max_temp = max_temp

    def setup_callback(self, cb):
        self._callback = cb

    def get_report_time_delta(self):
        return self.poll_interval

    def get_status(self, eventtime):
        return {
            'temperature': self.temp
        }

def load_config(config):
    pheaters = config.get_printer().load_object(config, "heaters")
    pheaters.add_sensor_factory("ifs_jacker_temperature_sensor", ifs_jacker_temperature_sensor)

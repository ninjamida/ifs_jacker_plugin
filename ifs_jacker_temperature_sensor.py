import logging

class ifs_jacker_temperature_sensor:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.name = config.get_name().split()[-1]
        self.peripheral_index = config.getint('peripheral_index')
        self.factor = config.getfloat('factor', 0.01)
        self.min_temp = config.getfloat('min_temp', -273.15)
        self.max_temp = config.getfloat('max_temp', 999)

        self.ifs_jacker = None
        self.temp = min(self.max_temp, max(self.min_temp, 0.0))
        self.poll_interval = 1.0

        self.printer.register_event_handler("klippy:ready", self._handle_ready)

        self.printer.add_object("ifs_jacker_temperature_sensor " + self.name, self)
        self.sample_timer = self.reactor.register_timer(self._sample)

    def _handle_ready(self):
        self.ifs_jacker = self.printer.lookup_object('ifs_jacker')
        self.reactor.update_timer(self.sample_timer, self.reactor.NOW)
        self.mcu = self.printer.lookup_object('mcu')

    def _sample(self, eventtime):
        try:
            if self.ifs_jacker and self.ifs_jacker.ifs_jacker_present:
                if self.peripheral_index < len(self.ifs_jacker.peripheral_states):
                    self.temp = int(self.ifs_jacker.peripheral_states[self.peripheral_index]) * self.factor
                else:
                    self.temp = -1
            else:
                self.temp = -1

            measured_time = self.reactor.monotonic()
            self._callback(self.mcu.estimated_print_time(measured_time), self.temp)
        except Exception:
            logging.exception('Exception reading IFS Jacker temperature sensor')

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

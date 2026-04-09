from pathlib import Path
import re, threading, time, logging

IFS_JACKER_CHECK_RETRY = 3
IFS_JACKER_CHECK_RETRY_DELAY = 30

class IFSJacker:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        
        self.gcode = self.printer.lookup_object('gcode')
        
        self.printer.register_event_handler("klippy:ready", self._handle_ready)
        
        self.ifs_jacker_version = 0.0
        self.ifs_jacker_present = None
        self.next_ifs_jacker_check = time.monotonic()
        self.ifs_jacker_check_attempts = 0
        
        self.stop_thread = False
        self.update_thread = threading.Thread(target=self._update_ifs_jacker_data)
        self.update_thread.daemon = True
        
        self.wait_time = config.get('wait_time', 1)
        
        self.peripheral_states = []
        
        self.gcode.register_command('IFSJ_Z1', self.cmd_IFSJ_Z1)        # Вставить пруток
        self.gcode.register_command('IFSJ_Z2', self.cmd_IFSJ_Z2)        # Извлечь пруток
        self.gcode.register_command('IFSJ_Z3', self.cmd_IFSJ_Z3)        # Состояние IFS
        self.gcode.register_command('IFSJ_Z4', self.cmd_IFSJ_Z4)        # Сброс драйвера
        self.gcode.register_command('IFSJ_Z5', self.cmd_IFSJ_Z5)        # Отжим филамента везде
        
    def _handle_ready(self):
        self.zmod_ifs = self.printer.lookup_object('zmod_ifs')
        self.update_thread.start()
        
    def _update_ifs_jacker_data(self):
        logging.info("IFS Jacker: Starting update thread")
        self.peripheral_regex = re.compile(r'peripheral_(\d+):\s*(\d+)')
        while not self.stop_thread:
            try:
                if self.zmod_ifs.ifs: 
                    if self.ifs_jacker_present is None and time.monotonic() > self.next_ifs_jacker_check:
                        self.check_for_ifs_jacker()
                        if not self.ifs_jacker_present and self.ifs_jacker_check_attempts < IFS_JACKER_CHECK_RETRY:
                            self.ifs_jacker_present = None
                            self.next_ifs_jacker_check = time.monotonic() + IFS_JACKER_CHECK_RETRY_DELAY
                        else:
                            self.send_gcode_command_from_update_loop('_IFS_JACKER_CONNECTED')
                    if self.ifs_jacker_present:
                        data_str = self.zmod_ifs.last_F13_raw_response
                        for peripheral_match in self.peripheral_regex.finditer(data_str):
                            peripheral_id, peripheral_state = peripheral_match.groups()
                            peripheral_id = int(peripheral_id)
                            if len(self.peripheral_states) <= self.peripheral_id:
                                self.peripheral_states += [0] * (self.peripheral_id + 1 - len(self.peripheral_states))
                            self.peripheral_states[peripheral_id] = peripheral_state
                elif self.ifs_jacker_present is not None:
                    self.ifs_jacker_version = 0.0
                    self.ifs_jacker_present = None
                    self.peripheral_states = [0] * len(self.peripheral_states)
                    self.next_ifs_jacker_check = time.monotonic()
                    self.ifs_jacker_check_attempts = 0
                    logging.info("IFS Jacker: IFS disconnected. IFS Jacker status cleared")
            except Exception as e:
                logging.warning("IFS Jacker error: %s", e)
            time.sleep(self.wait_time)
            
    def check_for_ifs_jacker(self):
        logging.info("IFS Jacker: Checking for IFS Jacker...")
        response = self.send_ifs_command_from_update_loop("Z2")
        if response:
            if 'software: "IFS Jacker' in response: # End quote intentionally missing
                self.ifs_jacker_present = True
                version_check = re.search(r'version:\s*"(.*?)"', response)
                if version_check:
                    self.ifs_jacker_version = float('.'.join(version_check.group(1).split('.')[0:2]))
                    logging.info(f"IFS Jacker: Detected IFS Jacker. Firmware version {self.ifs_jacker_version}")
                else:
                    logging.info(f"IFS Jacker: Detected IFS Jacker. Could not detect firmware version.")
                    self.ifs_jacker_version = 2.1  # Lowest supported version
                return
        
        self.ifs_jacker_version = 0.0
        self.ifs_jacker_present = False
        self.send_ifs_command_from_update_loop("F13", force=True) # To clear the Z2 command from the queue, otherwise zMod enters an infinite loop of sending Z2 and getting no response
        logging.info("IFS Jacker: No IFS Jacker detected")
            
    def validate_version(self, min_ver=0.0):
        if not self.zmod_ifs.ifs:
            self.gcode.run_script_from_command("_IFS_OFF")
            return False
        
        if self.ifs_jacker_present:
            if self.ifs_jacker_version >= min_ver:
                return True
            else:
                self.gcode.run_script_from_command(f"_IFS_JACKER_VERSION VERSION={min_ver}")
                return False
        else:
            self.gcode.run_script_from_command("_NO_IFS_JACKER")
            return False
            
    def _safe_run_script(self, script):
        try:
            self.gcode.run_script_from_command(script)
        except self.gcode.error as e:
            pass
            
    def send_gcode_command_from_update_loop(self, script):
        self.reactor.register_async_callback(
                lambda eventtime: self._safe_run_script(script)
            )
            
    def send_ifs_command_from_update_loop(self, command, timeout=5.0, force=False):
        start_time = time.monotonic()
        command_issued = False
        command_id = 0
        while time.monotonic() - start_time < timeout:
            if not command_issued:
                with self.zmod_ifs._command_lock:
                    if '#' in self.zmod_ifs._command and not force:
                        time.sleep(0.1)
                    else:
                        command_id = self.zmod_ifs._command_id + 1
                        self.zmod_ifs._command_id = command_id
                        self.zmod_ifs._command = f'{command}#{command_id}'
                        time.sleep(0.02)
                        command_issued = True
            else:
                with self.zmod_ifs._ret_command_lock:
                    ret_command_data = self.zmod_ifs._ret_command_data
                    ret_command_id = self.zmod_ifs._ret_command_id
                    self.zmod_ifs._ret_command_id = 0
                if command_id == ret_command_id:
                    return ret_command_data
                    
        if command_issued:
            with self.zmod_ifs._command_lock:
                if not '#' in self.zmod_ifs._command:
                    self.zmod_ifs._command = 'F13'
        return ''
            
            
                
    def cmd_IFSJ_Z1(self, gcmd):
        if not self.validate_version(0.0):
            return

        response = self.zmod_ifs.send_command_and_wait("Z1")
        self.gcode.respond_info(f"Z1 > {response}")
                
    def cmd_IFSJ_Z2(self, gcmd):
        if not self.validate_version(0.0):
            return

        response = self.zmod_ifs.send_command_and_wait("Z2")
        self.gcode.respond_info(f"Z2 > {response}")
                
    def cmd_IFSJ_Z3(self, gcmd):
        if not self.validate_version(2.2):
            return

        response = self.zmod_ifs.send_command_and_wait("Z3")
        self.gcode.respond_info(f"Z3 > {response}")
                
    def cmd_IFSJ_Z4(self, gcmd):
        if not self.validate_version(2.2):
            return

        response = self.zmod_ifs.send_command_and_wait("Z4")
        self.gcode.respond_info(f"Z4 > {response}")
        
    def cmd_IFSJ_Z5(self, gcmd):
        if not self.validate_version(2.2):
            return
            
        peripheral = gcmd.get_int('PERIPHERAL', 0)
        command = gcmd.get_int('COMMAND', 2)
        param1 = gcmd.get_int('PARAM1', 0)
        param2 = gcmd.get_int('PARAM2', 0)
        
        response = self.zmod_ifs.send_command_and_wait(f"Z5 C{peripheral} F{command} L{param1} S{param2}")
        self.gcode.respond_info(f"Z5 > {response}")


def load_config(config):
    return IFSJacker(config)
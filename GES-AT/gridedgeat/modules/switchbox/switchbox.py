import visa
import os.path


class SwitchBox(object):
    '''
    SwitchBox Class
        - Keithley 3706A + 3723 card
        - command manual: c:/Users/PV_Test/Desktop/keithley-3700a-referencehandbuchswitch-901-01c-jul-2016.pdf
        - cards: https://smt.at/wp-content/uploads/smt-handbuch-keithley-3700a-scannerkarten-englisch.pdf
    '''

    def __init__(self, visa_string='GPIB0::16::INSTR'):
        self.manager = visa.ResourceManager().open_resource(visa_string) 
        self.open_all()
        self.set_pole(1)
        self.write('slot[1].interlock.override = slot.ON')
        self.connection_map = {}
        self.set_connection_map()

    def __del__(self):
        self.manager.close()

    ## common visa api wrappers
    # write: send command with out expecting return
    # read: instrument response
    # ask: write + read
    def write(self, command):
        self.manager.write(command)
    def read(self):
        return self.manager.read()
    def ask(self, command):
        return self.manager.query(command)


    ## low level swithbox api wrapper
    def short_channel(self, channel):
        'Connect channel, check command manual for the channel numbers.'
        self.write('channel.close("{}")'.format(channel))

    def open_all(self):
        'Open (disconnect) all channels.'
        self.write('channel.open("allslots")')

    def set_pole(self, poles):
        'Set the pole modes for the all slots. Should use pole mode ONE'
        self.write('channel.setpole("allslots", {})'.format(poles))


    ## high-level api
    def set_connection_map(self, connection_map = None):
        'Setup the connections maps based on the netlist'
        # default paths
        if connection_map == None:
            connection_map = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'netlist.scr')
        # load the pcb connection map
        with open(connection_map, 'r') as f:
            cmap_lines = f.readlines()
        for cline in cmap_lines:
            wire_info = cline.split(' ')[2:]
            if len(wire_info) > 0 and wire_info[0] != 'GND':
                device_id = wire_info[1] + 'D' + wire_info[2]
                channel_id = 30*(int(wire_info[3][-1]) - 1) + int(wire_info[4])
                self.connection_map[device_id] = channel_id

    def connect(self, substrate, device):
        'Connect the channels based on the substrate and device id'
        if substrate not in range(1, 17) and device not in range(1, 7):
            raise ValueError('Substrate or device number out of range!')

        self.open_all()
        device_id = 'S{}D{}'.format(substrate, device)
        self.short_channel(1000 + self.connection_map[device_id])

        # set backplane
        self.write('channel.close("1913")')

    def get_connect(self):
        'get the channels that are connected'
        return sb.ask('print(channel.getclose("allslots"))')

    



if __name__ == '__main__':
    # test
    sb = SwitchBox()
    sb.connect(1, 2)
    print(sb.get_connect())


    pass

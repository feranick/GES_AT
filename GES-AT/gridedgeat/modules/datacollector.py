from xystage.xystage import XYstage
from sourcemeter.sourcemeter import SourceMeter
from switchbox.switchbox import SwitchBox

import numpy as np
import time, threading


# decorator for asynchronous methods
def async(func):
    # define the function to be returned by the decorator
    def asyn_func(obj, *args, **kwargs):

        # define function that takes arguments and changes status
        def wrapped_func():
            obj.busy = True
            func(obj, *args, **kwargs)
            obj.busy = False

        # start thread
        thread = threading.Thread(target=wrapped_func)
        thread.daemon = True
        thread.start()
    return asyn_func



class DataCollector:

    def __init__(self):

        # initialize the instruments
        self.xy_stage     = None # XYstage()
        self.switch_box   = SwitchBox('GPIB0::16::INSTR')

        self.source_meter = SourceMeter('GPIB0::24::INSTR')
        self.source_meter.set_limit(voltage=20., current=1.)
        self.source_meter.on()

    def __del__(self):
        self.source_meter.off()
        del self.source_meter
        del self.switch_box


    ## low level api
    # xy substrate layout (default)
    # column:  1 ==> 4     row:
    # 13 | 14 | 15 | 16     4
    # 9  | 10 | 11 | 12     3
    # 5  | 6  | 7  | 8      2
    # 1  | 2  | 3  | 4      1
    # xy device layout (default)
    # |   ----   |
    # | 3 |  | 4 |
    # | 2 |  | 5 |
    # | 1 |  | 6 |
    # |   ----   |
    def get_substrate_id(self, row, column):
        return column + (row-1)*4

    __sub_xy_pcb = [
        13, 14, 15, 16,
        9,  10, 11, 12,
        5,   6,  7,  8,
        1,   2,  3,  4, ]
    __dev_xy_pcb = [3, 2, 1, 4, 5, 6]
    # pcb substrate layout
    # 1  | 2  | 3  | 4  (-3*4)
    # 5  | 6  | 7  | 8  (-1*4)
    # 9  | 10 | 11 | 12 (+1*4)
    # 13 | 14 | 15 | 16 (+3*4)
    # pcb device layout (default)
    # |   ----   |
    # | 1 |  | 4 |
    # | 2 |  | 5 |
    # | 3 |  | 6 |
    # |   ----   |
    def get_pcb_id(self, xy_sub_id, xy_dev_id):
        "ID converison between xy to pcb"
        return self.__sub_xy_pcb[xy_sub_id-1], self.__dev_xy_pcb[xy_dev_id-1]

    def switch_device(self, sub_id, dev_id):
        "Switch operation devices"
        self.xy_stage.move_to_device_3x2(sub_id, dev_id)
        self.switch_box.connect(*get_pcb_id(sub_id, dev_id))



    ## measurements
    def measure_JV(self, acq_params, filename):
        self.source_meter.set_mode('VOLT')
        self.source_meter.on()
        
        # measurement parameters
        v_min = acq_params['acqMinVoltage']
        v_max = acq_params['acqMaxVoltage']
        v_start = acq_params['acqStartVoltage']
        v_step = acq_params['acqStepVoltage']
        scans = acq_params['acqNumAvScans']
        hold_time = acq_params['acqHoldTime']

        # enforce
        if v_start < v_min and v_start > v_max and v_min > v_max:
            raise ValueError('Voltage Errors')

        # create list of voltage to measure
        v_list = np.arange(v_min-2., v_max + 2., v_step)
        v_list = v_list[np.logical_and(v_min-1e-9 <= v_list, v_list <= v_max+1e-9)]
        start_i = np.argmin(abs(v_start - v_list))

        N = len(v_list)
        i_list = list(range(0, N))[::-1] + list(range(0, N))
        i_list = i_list[N-start_i-1:] + i_list[:N-start_i-1]

        # create data array
        data = np.zeros((N, 3))
        data[:, 0] = v_list

        # measure
        for n in range(scans):
            for i in i_list:
                self.source_meter.set_output(voltage = v_list[i])
                time.sleep(hold_time)
                data[i, 2] += 1.
                data[i, 1] = (self.source_meter.read_values()[1] + data[i,1]*(data[i,2]-1)) / data[i,2]
                np.savetxt(filename, data[:, 0:2], delimiter=',', header='V,J')

        return data[:, 0:2]




    def measure_voc_jsc_mpp(self, v_step, hold_time):
        # voc
        self.source_meter.set_mode('CURR')
        self.source_meter.on()
        self.source_meter.set_output(current = 0.)
        voc = self.source_meter.read_values()[0]

        # jsc
        self.source_meter.set_mode('VOLT')
        self.source_meter.on()
        self.source_meter.set_output(voltage = 0.)
        jsc = self.source_meter.read_values()[1]

        # measurement parameters
        v_min = 0.
        v_max = voc

        # measure
        pp = []
        for v in np.arange(0, voc, v_step):
            self.source_meter.set_output(voltage = v)
            time.sleep(hold_time)
            pp.append(self.source_meter.read_values()[1] * v)
        return voc, jsc, np.max(pp)


    def tracking(self, acq_params, filename):

        num_points = acq_params['acqTrackNumPoints']
        track_time = acq_params['acqTrackInterval']
        v_step = acq_params['acqStepVoltage']
        hold_time = acq_params['acqHoldTime']

        data = np.zeros((num_points, 4))
        voc, jsc, mpp = self.measure_voc_jsc_mpp(v_step = v_step, hold_time = hold_time)
        st = time.time()
        data[0, :] = [0., voc, jsc, mpp]

        for n in range(1, num_points):
            time.sleep(track_time)
            voc, jsc, mpp = self.measure_voc_jsc_mpp(v_step = v_step, hold_time = hold_time)
            data[n, :] = [time.time()-st, voc, jsc, mpp]
            np.savetxt(filename, data, delimiter=',', header='time,Voc,Jsc,MPP')





    ## high level api
    def acquisition(self, row, column, deviceID, acq_params):

        max_power = []

        # measure all devices JV
        for dev_id in range(1, 7):
            self.switch_device(get_substrate_id(row, column), dev_id)
            time.sleep(acq_params['acqDelBeforeMeas'])

            jv = self.measure_JV(
                filename = deviceID+str(dev_id) + '.csv',
                acq_params = acq_params,)

            max_power.append(np.max(jv[:, 0] * jv[:, 1]))
            

        # goto best
        dev_id = np.argmax(max_power) + 1
        self.switch_device(get_substrate_id(row, column), dev_id)

        # trackings
        self.tracking(
            filename = deviceID+str(dev_id) + '_track.csv',
            acq_params = acq_params,)




if __name__ == '__main__':
    dc = DataCollector()

    dc.tracking(None)

    exit()
    dc.measure_JV({
        'acqMinVoltage' : 0,
        'acqMaxVoltage' : 1,
        'acqStartVoltage' : 0,
        'acqStepVoltage' : 0.02,
        'acqNumAvScans': 2,
        'acqHoldTime': 0.00,
        })

    pass

'''
'''

from __future__ import print_function
import math

# import numpy as np
from collections import namedtuple


def get_servo_frequencies(pwm_freq):
    return [(pwm_freq / (divider + 1))
            for divider in range(16)]


def get_phase_frequencies(pwm_freq):
    return [((2. * pwm_freq) / (divider + 1))
            for divider in range(16)]


# TODO individual servo ic config
mtype = namedtuple('MotorType', ['type_setting',
                                 'clear_fault',
                                 'protection'])


mtype_info = {'None': mtype('NONE', 'CCFE', '0CFE'),
              'Brush': mtype('4CFE', 'CCFE', '0CFE'),
              'Brushless': mtype('4CFE', 'CCFE', '0CFE'),
              'Stepper': mtype('4DFE', 'CDFE', '0DFE'),
              }


motor_types = list(mtype_info.keys())

ect_type = namedtuple('EncoderType', ['lines', 'addrs'])
ect_info = {'Quadrature': ect_type(1, ['$78000', '$78008', '$78010', '$78018', '$78100', '$78108', '$78110', '$78118']),
            'Sin/Cos': ect_type(3, ['$FF8000,$78B00,$0', '$FF8008,$78B02,$0', '$FF8010,$78B04,$0', '$FF8018,$78B06,$0', '$FF8100,$78B08,$0', '$FF8108,$78B0A,$0', '$FF8110,$78B0C,$0', '$FF8118,$78B0E,$0']),
            'Resolver': ect_type(8, ['$F78B00,$478B10,$0,$D83503,$400,$80000,$0,$1', '$F78B02,$478B10,$000000,$D8350B,$400,$80000,$0,$1', '$F78B04,$478B10,$000000,$D83513,$400,$80000,$0,$1', '$F78B06,$478B10,$000000,$D8351B,$400,$80000,$0,$1', '$F78B08,$478B10,$000000,$D83523,$400,$80000,$0,$1', '$F78B0A,$478B10,$000000,$D8352B,$400,$80000,$0,$1', '$F78B0C,$478B10,$000000,$D83533,$400,$80000,$0,$1', '$F78B0E,$478B10,$000000,$D8353B,$400,$80000,$0,$1']),
            'SSI': ect_type(2, ['$278B20,$18000', '$278B24,$18000', '$278B28,$18000', '$278B2C,$18000', '$278B30,$18000', '$278B34,$18000', '$278B38,$18000', '$278B3C,$18000']),
            'Endat2.2': ect_type(2, ['$278B20,$18000', '$278B24,$18000', '$278B28,$18000', '$278B2C,$18000', '$278B30,$18000', '$278B34,$18000', '$278B38,$18000', '$278B3C,$18000']),
            'Yaskawa Abs 16bit': ect_type(2, ['$278B20,$020004', '$278B24,$020004', '$278B28,$020004', '$278B2C,$020004', '$278B30,$020004', '$278B34,$020004', '$278B38,$020004', '$278B3C,$020004']),
            'Yaskawa Abs 17bit': ect_type(2, ['$278B20,$021004', '$278B24,$021004', '$278B28,$021004', '$278B2C,$021004', '$278B30,$021004', '$278B34,$021004', '$278B38,$021004', '$278B3C,$021004']),
            'Yaskawa Abs 20bit': ect_type(2, ['$278B20,$024004', '$278B24,$024004', '$278B28,$024004', '$278B2C,$024004', '$278B30,$024004', '$278B34,$024004', '$278B38,$024004', '$278B3C,$024004']),
            'Yaskawa Inc 13bit': ect_type(2, ['$278B20,$00D006', '$278B24,$00D006', '$278B28,$00D006', '$278B2C,$00D006', '$278B30,$00D006', '$278B34,$00D006', '$278B38,$00D006', '$278B3C,$00D006']),
            'Yaskawa Inc 17bit': ect_type(2, ['$278B20,$011006', '$278B24,$011006', '$278B28,$011006', '$278B2C,$011006', '$278B30,$011006', '$278B34,$011006', '$278B38,$011006', '$278B3C,$011006']),
            'Panasonic': ect_type(2, ['$278B20,$18000', '$278B24,$18000', '$278B28,$18000', '$278B2C,$18000', '$278B30,$18000', '$278B34,$18000', '$278B38,$18000', '$278B3C,$18000']),
            'Tamagawa': ect_type(2, ['$278B20,$18000', '$278B24,$18000', '$278B28,$18000', '$278B2C,$18000', '$278B30,$18000', '$278B34,$18000', '$278B38,$18000', '$278B3C,$18000']),
            'Biss B/C': ect_type(2, ['$278B20,$18000', '$278B24,$18000', '$278B28,$18000', '$278B2C,$18000', '$278B30,$18000', '$278B34,$18000', '$278B38,$18000', '$278B3C,$18000']),

            # TODO: last addr is wrong
            'Micro Stepping': ect_type(3, ['$6800BF,$018018,$EC0001', '$68013F,$018018,$EC0003', '$6801BF,$018018,$EC0005', '$68023F,$018018,$EC0007', '$6802BF,$018018,$EC0009', '$68033F,$018018,$EC000B', '$6803BF,$018018,$EC000D', '$68043F,$018018,$EC000F']),
            }


static_ect_setup = [
    'WY:$3501,$78000,$78008,$78010,$78018,$78100,$78108,$78110,$78118',
    'WY:$3509,$6800BF,$018018,$EC0009,$68013F,$018018,$EC000C,$6801BF,$018018,$EC000F,$68023F,$018018,$EC0012,$6802BF,$018018,$EC0015,$68033F,$018018,$EC0018,$6803BF,$018018,$EC001B,$68043F,$018018,$EC001E',
]

phasing_methods = ['2-Guess Method',
                   'Stepper Method',
                   'Hall Sensors',
                   ]

adc_mask_setup = ['// ADC Mask',
                  'I184,8,100=$FFFC00'
                  ]


output_addrs = ['$078002',
                '$07800A',
                '$078012',
                '$07801A',
                '$078102',
                '$07810A',
                '$078112',
                '$07811A',
                ]

current_loop_addrs = ['$078006',
                      '$07800E',
                      '$078016',
                      '$07801E',
                      '$078106',
                      '$07810E',
                      '$078116',
                      '$07811E',
                      ]

flag_settings = ['$078000',
                 '$078008',
                 '$078010',
                 '$078018',
                 '$078100',
                 '$078108',
                 '$078110',
                 '$078118',
                 ]

phase_pos = ['$78001',
             '$78009',
             '$78011',
             '$78019',
             '$78101',
             '$78109',
             '$78111',
             '$78119',
             ]

hall_addr = ['$78000',
             '$78008',
             '$78010',
             '$78018',
             '$78100',
             '$78108',
             '$78110',
             '$78118',
             ]


def i_prop(ivar):
    def fget(self):
        if isinstance(ivar, (list, tuple)):
            return (iv.format(self.mnum) for iv in ivar)
        else:
            return ivar.format(self.mnum)

    return property(fget)


class LVMotor(object):
    i_activation = i_prop('I{}00')
    i_commutation = i_prop('I{}01')
    i_output_addr = i_prop('I{}02')
    i_pos_feedback = i_prop('I{}03')
    i_vel_feedback = i_prop('I{}04')
    i_current_loop_addr = i_prop('I{}82')
    i_phase_offset = i_prop('I{}72')
    i_pwm_scale_factor = i_prop('I{}66')
    i_current_loop = i_prop(('I{}61', 'I{}62', 'I{}76'))
    i_i2t = i_prop(('I{}57', 'I{}58', 'I{}69'))
    i_flag_addr = i_prop('I{}25')
    i_flag_mode = i_prop('I{}24')
    i_phase_pos = i_prop('I{}83')
    i_pole_pairs = i_prop('I{}70')
    i_counts_per_rev = i_prop('I{}71')
    i_phase_search = i_prop('I{}80')
    i_phase_search_mag = i_prop('I{}73')
    i_phase_search_t = i_prop('I{}74')
    i_abs_pos_addr = i_prop('I{}81')
    i_abs_pos_format = i_prop('I{}91')
    i_mag_current = i_prop('I{}77')
    i_quad_cur_loop = i_prop('I{}96')
    i_stepper_pid = i_prop(('I{}30', 'I{}31', 'I{}32', 'I{}33', 'I{}34', 'I{0}35..{0}39'))
    i_comm_delay = i_prop('I{0}56')

    ix30 = 1024
    ix31 = 0
    ix32 = 85
    ix33 = 1024
    ix34 = 1
    ix35_39 = 0

    def __init__(self, config, mnum,
                 type_='Stepper',
                 cont_current=2.5,
                 cont_current_rms=True,
                 inst_current=13.1,
                 inst_current_rms=True,
                 max_voltage=320,  # VDC
                 pole_res=1.13,    # pole-to-pole, ohms
                 pole_induct=3.6,  # pole-to-pole, mH
                 enc_type='Micro Stepping',
                 counts_per_rev=32768,
                 poles_rev=3,      # pole pairs per revolution
                 phasing_method='Stepper Method',
                 overtravel_limits=True,

                 step_angle=1.8,
                 max_rpm=2000,
                 serial_enc_res=26,

                 cur_loop_bandwidth=300,
                 cur_loop_damping=0.707,
                 micro_stepping=65536,    # counts per commutation cycle
                 ):

        self._mnum = int(mnum)
        assert self._mnum in range(1, 9), 'Motor number out of range'

        self.config = config
        self.type_ = type_
        assert type_ in motor_types, 'Invalid motor type'

        if cont_current_rms:
            self.cont_current = float(cont_current) * math.sqrt(2.)
        else:
            self.cont_current = float(cont_current)

        if inst_current_rms:
            self.inst_current = float(inst_current) * math.sqrt(2.)
        else:
            self.inst_current = float(inst_current)

        self.max_voltage = float(max_voltage)
        self.pole_res = float(pole_res) / math.sqrt(3.)
        self.pole_induct = float(pole_induct) / math.sqrt(3.)
        self.pole_induct /= 1000.0  # mH -> H

        self.enc_type = enc_type
        assert enc_type in ect_info, 'Invalid encoder type'

        self.enc_addr = ect_info[self.enc_type].addrs[self.array_idx]
        self.enc_lines = ect_info[self.enc_type].lines

        self.phasing_method = phasing_method

        assert phasing_method in phasing_methods, 'Invalid phasing method'

        self.overtravel_limits = bool(overtravel_limits)

        self.step_angle = float(step_angle)
        self.max_rpm = int(max_rpm)
        self.serial_enc_res = int(serial_enc_res)

        self.cur_loop_bandwidth = cur_loop_bandwidth
        self.cur_loop_damping = cur_loop_damping
        self.micro_stepping = int(micro_stepping)

        if self.uses_ustep:
            self.pole_pairs = 1
            self.counts_per_rev = micro_stepping
        else:
            self.poles_pairs = int(poles_rev)
            self.counts_per_rev = int(counts_per_rev)

    @property
    def kcp(self):
        xi = self.cur_loop_damping
        wn = self.cur_loop_bandwidth * 2. * math.pi
        vdc = self.config.bus_voltage
        i_sat = self.config._max_adc
        # ref: user manual pg 108
        return i_sat * ((2.0 * xi * wn * self.pole_induct) - self.pole_res) / vdc

    @property
    def kci(self):
        wn = self.cur_loop_bandwidth * 2. * math.pi
        vdc = self.config.bus_voltage
        i_sat = self.config._max_adc
        t_phase = 1.0 / (1000. * self.config.phase_freq)
        # ref: user manual pg 108
        return i_sat * t_phase * wn ** 2. * self.pole_induct / vdc

    @property
    def ix61(self):
        '''Ixx61 Motor xx Current-Loop Integral Gain'''
        # ref: user manual pg 108
        return self.kci * self.config.pwm_period / (8. * self.pwm_scale)

    @property
    def ix62(self):
        '''Ixx62 Motor xx Current-Loop Forward-Path Proportional Gain'''
        return 0

    @property
    def ix76(self):
        '''Ixx76 Motor xx Current-Loop Back-Path Proportional Gain'''
        # ref: user manual pg 108
        return self.kcp * self.config.pwm_period / (4. * self.pwm_scale)

    @property
    def ix57(self):
        '''Ixx57 Motor xx Continuous Current Limit'''
        # ref: SRM pg 121
        i = min(self.cont_current, self.config._cont_current)
        i_sat = self.config._max_adc
        return int(32767. * i / i_sat * math.cos(math.radians(30.)))

    @property
    def ix58(self):
        '''Ixx58 Motor xx Integrated Current Limit'''
        # ref: SRM pg 122
        servo_rate = self.config.servo_freq * 1000.
        permitted_time = self.config._inst_current_sec
        return int(((self.ix57 ** 2. + self.ix69 ** 2.) * servo_rate * permitted_time) /
                   (32767. ** 2))

    @property
    def ix69(self):
        '''Ixx69 Motor xx Output Command Limit'''
        if self.uses_ustep:
            # Calculate based on microstepping
            # TODO - right?
            ustep_value = self.micro_stepping / 1024

            # And maximum RPM
            pole_pair = 360.0 / (4. * self.step_angle)
            servo_rate = self.config.servo_freq * 1000.
            max_rps = self.max_rpm / 60.
            max_rpm_value = pole_pair * max_rps * self.micro_stepping / (192. * servo_rate)

            # And give the lesser of the two as the max
            return min(ustep_value, max_rpm_value)
        else:
            i = min(self.inst_current, self.config._inst_current)
            i_sat = self.config._max_adc
            return int(32767. * i / i_sat * math.cos(math.radians(30.)))

    @property
    def pwm_scale(self):
        return self.config.get_pwm_sf(self.max_voltage)

    @property
    def phase_offset(self):
        if self.type_ in ('Stepper', 'Brush'):
            return 512
        else:
            return 683

    @property
    def minfo(self):
        return mtype_info[self.type_]

    @property
    def mnum(self):
        return self._mnum

    @property
    def array_idx(self):
        return self._mnum - 1

    @property
    def clear_fault_addr(self):
        if self.mnum <= 4:
            idx = 7 + self.mnum
        else:
            idx = 7 + (self.mnum - 4)

        return '$F{:X}{}'.format(idx, self.minfo.clear_fault)

    @property
    def motor_type_addr(self):
        if self.mnum <= 4:
            idx = 7 + self.mnum
        else:
            idx = 7 + (self.mnum - 4)

        return '$F{:X}{}'.format(idx, self.minfo.type_setting)

    @property
    def protection_addr(self):
        if self.mnum <= 4:
            idx = self.mnum - 1
        else:
            idx = self.mnum - 5

        return '$F{:X}{}'.format(idx, self.minfo.protection)

    def plc_setup(self, sleep_time=50):
        mnum = self.mnum

        # 78014 for motors 1-4, 78114 for motors 5-8
        if mnum <= 4:
            addr0 = 0x78014
        else:
            addr0 = 0x78114

        cmd_str = 'CMD"WX:${:X},%s"          // %s'.format(addr0, )

        sleep_str = 'timer32 = %d msec32' % sleep_time
        for line in [cmd_str % (self.clear_fault_addr, 'Motor #%d CLRF' % mnum),
                     sleep_str,
                     cmd_str % (self.motor_type_addr, 'Motor #%d Type' % mnum),
                     sleep_str,
                     cmd_str % (self.protection_addr, 'Motor #%d Protection' % mnum),
                     sleep_str,
                     ]:
            yield line

    @property
    def enabled_value(self):
        if self.type_ == 'None':
            return 0
        else:
            return 1

    @property
    def output_addr(self):
        return output_addrs[self.array_idx]

    @property
    def current_loop_addr(self):
        return current_loop_addrs[self.array_idx]

    @property
    def is_dynamic_ect(self):
        return self.config.dynamic_ect

    @property
    def uses_ustep(self):
        return self.enc_type == 'Micro Stepping'

    @property
    def ect_end_addr(self):
        return '$%X' % self.config.motor_ect_ends()[self.array_idx]

    @property
    def ect_start_addr(self):
        return '$%X' % self.config.motor_ect_starts()[self.array_idx]

    @property
    def flag_settings(self):
        return flag_settings[self.array_idx]

    @property
    def flag_mode(self):
        if self.overtravel_limits:
            ot = 0
        else:
            ot = 2

        if self.uses_ustep:
            ustep = 4
        else:
            ustep = 0

        return '$8{}0{}01'.format(ot, ustep)

    @property
    def phase_pos(self):
        if self.enc_type in ('Quadrature', 'Sin/Cos'):
            return phase_pos[self.array_idx]
        else:
            return self.ect_end_addr

    @property
    def ix80(self):
        '''Phase search method'''
        # TODO double-check
        if self.uses_ustep or self.type_ == 'Brush':
            return 0
        elif self.phasing_method == 'Hall Sensors':
            return 0
        elif self.phasing_method == 'Stepper Method':
            return 6
        else:
            return 4

    @property
    def ix73(self):
        '''Phase search magnitude'''
        # 16-bit dac units
        if self.uses_ustep:
            return 0
        elif self.phasing_method == '2-Guess Method':
            return self.ix57 / 4.
        elif self.phasing_method == 'Stepper Method':
            return self.ix57 / 3.
        else:
            # 2 guess method
            return 0

    @property
    def ix74(self):
        '''Phase search time'''
        if self.uses_ustep or self.type_ == 'Brush':
            return 0
        elif self.phasing_method == 'Hall Sensors':
            return 0
        elif self.phasing_method == 'Stepper Method':
            # Units of servo-cycles * 256
            return 50
        else:
            # 2 guess method, units of servo cycles
            return 6

    def _uses_hall_addr(self):
        if self.uses_ustep or self.type_ == 'Brush' or self.phasing_method == 'Hall Sensors':
            if self.uses_ustep or self.type_ == 'Brush':
                return False
            else:
                return True
        else:
            raise ValueError

    @property
    def ix81(self):
        '''Absolute phase position source address'''

        try:
            if self._uses_hall_addr():
                return hall_addr[self.array_idx]
            else:
                return self.ect_end_addr
        except ValueError:
            pass

        return 0

    @property
    def ix91(self):
        '''Absolute phase position source address'''

        try:
            if self._uses_hall_addr():
                return '$800000'
            else:
                return '$500000'
        except ValueError:
            pass

        return 0

    @property
    def ix77(self):
        '''Magnetization current'''
        if self.uses_ustep:
            return int(self.ix57 / 3.)

        return 0

    @property
    def ix96(self):
        '''Quadrature current loop calculation only (brushed motors)'''
        if self.type_ == 'Brush':
            return 1
        else:
            return 0

    @property
    def ix56(self):
        '''Commutation delay compensation for microstepping'''
        if self.uses_ustep:
            return '18/360*2048/(I{0}69*I{0}08*32)'.format(self.mnum)
        else:
            return '0'

    def get_config(self, use_comments=True):
        for line in self._get_config():
            comment, line = line
            if comment and use_comments:
                yield '// %s' % comment
            if isinstance(line, str):
                yield line
            elif isinstance(line, tuple):
                if len(line) == 1:
                    yield '{}={}'.format(*line[0])
                else:
                    yield ' '.join('{}={}'.format(*entry)
                                   for entry in line)

    def _get_config(self):
        if self.is_dynamic_ect:
            yield 'Dynamic ECT', 'WY:{},{}'.format(self.ect_start_addr, self.enc_addr)

        yield 'Activation', \
            ((self.i_activation, self.enabled_value), )
        yield 'Commutation',\
            ((self.i_commutation, self.enabled_value), )
        yield 'Output address', \
            ((self.i_output_addr, self.output_addr), )
        yield 'Position feedback', \
            ((self.i_pos_feedback, self.ect_end_addr), )
        yield 'Velocity feedback', \
            ((self.i_vel_feedback, self.ect_end_addr), )
        yield 'Current loop address', \
            ((self.i_current_loop_addr, self.current_loop_addr), )
        yield 'Phase offset', \
            ((self.i_phase_offset, self.phase_offset), )
        yield 'PWM scale factor', \
            ((self.i_pwm_scale_factor, int(self.pwm_scale)), )

        ix61, ix62, ix76 = self.i_current_loop
        yield 'Current loop', \
            ((ix61, self.ix61), (ix62, self.ix62), (ix76, self.ix76), )

        ix57, ix58, ix69 = self.i_i2t
        yield 'I2T', \
            ((ix57, self.ix57), (ix58, self.ix58), (ix69, self.ix69), )

        yield 'Flag addr', \
            ((self.i_flag_addr, self.flag_settings), )
        yield 'Flag mode', \
            ((self.i_flag_mode, self.flag_mode), )
        yield 'Phase pos', \
            ((self.i_phase_pos, self.phase_pos), )
        yield 'Pole pairs', \
            ((self.i_pole_pairs, self.pole_pairs), )
        yield 'Counts/rev', \
            ((self.i_counts_per_rev, self.counts_per_rev), )
        yield 'Phase search', \
            ((self.i_phase_search, self.ix80), )
        yield 'Phase search mag', \
            ((self.i_phase_search_mag, self.ix73), )
        yield 'Phase search time', \
            ((self.i_phase_search_t, self.ix74), )
        yield 'Abs pos addr', \
            ((self.i_abs_pos_addr, self.ix81), )
        yield 'Abs pos format', \
            ((self.i_abs_pos_format, self.ix91), )
        yield 'Mag current', \
            ((self.i_mag_current, self.ix77), )
        yield 'Quad cur loop', \
            ((self.i_quad_cur_loop, self.ix96), )

        ix30, ix31, ix32, ix33, ix34, ix35_39 = self.i_stepper_pid
        yield 'Stepper PID', \
            ((ix30, self.ix30),
             (ix31, self.ix31),
             (ix32, self.ix32),
             (ix33, self.ix33),
             (ix34, self.ix34),
             (ix35_39, self.ix35_39)
             )

        if self.uses_ustep:
            yield 'Comm delay', \
                ((self.i_comm_delay, self.ix56), )


class LVConfig(object):
    _microstep_static_ends = ['350B', '350E', '3511', '3514', '3517', '351A', '351D', '3520']
    _other_static_ends = ['3501', '3502', '3503', '3504', '3505', '3506', '3507', '3508']

    _cont_current = 5. * math.sqrt(2.)
    _inst_current = 15. * math.sqrt(2.)
    _inst_current_sec = 1.8
    _max_adc = 33.85

    def __init__(self, pwm_freq=19.6608, phase_freq=None, servo_freq=None,
                 phase_div=1, servo_div=3,
                 sclk=2, pfm=2, dac=3, adc=3,
                 pwm_deadtime=0.54,

                 dynamic_ect=True,
                 ect_start_addr=0x3501,
                 bus_voltage=48):
        '''
        Basic configuration requires clock frequency settings.

        pwm_freq: main pwm generator frequency [kHz]
        phase_freq: derived from pwm [kHz]
        servo_freq: derived from pwm [kHz]

        phase_div: divider value to use [0, 15]
                    phase_freq = pwm_freq / (phase_div + 1)
        servo_div: divider value to use [0, 15]
                    servo_freq = pwm_freq / (servo_div + 1)
        pwm_deadtime: PWM deadtime, multiples of 0.135usec [usec]

        TODO: sclk, pfm, dac, and adc are used directly and not calculated.
              (See the documentation on page 217-218 for more information.)

        If phase_freq, servo_freq are not specified, phase_div and servo_div
        are used directly.

        Ref: turbo_srm.pdf, pgs 43, 213~
        '''

        self.pwm_freq = float(pwm_freq)
        self.phase_freq = phase_freq
        self.servo_freq = servo_freq
        self.phase_div = phase_div
        self.servo_div = servo_div
        self.sclk = int(sclk)
        self.pfm = int(pfm)
        self.dac = int(dac)
        self.adc = int(adc)
        self.pwm_deadtime_us = pwm_deadtime
        self.pwm_step = 0.135
        self.bus_voltage = bus_voltage

        self.motors = []
        self.dynamic_ect = dynamic_ect

        self._ect_start_addr = ect_start_addr
        if not (0 <= self.pwm_deadtime <= 255):
            raise ValueError('PWM deadtime settings out of range')

    def add_motor(self, motor):
        self.motors.append(motor)

    @property
    def phase_frequencies(self):
        return get_phase_frequencies(self.pwm_freq)

    @property
    def servo_frequencies(self):
        return get_servo_frequencies(self.pwm_freq)

    @property
    def pwm_period(self):
        pwm_period = int((((117964.8 / self.pwm_freq) - 6) / 4))
        if not (0 <= pwm_period <= 32767):
            raise ValueError('PWM frequency out of range (i7100=%d)' % pwm_period)
        return pwm_period

    @property
    def servo_period(self):
        return int(640. / 9. * (2. * self.pwm_period + 3) * (self.phase_div + 1) * (self.servo_div + 1))

    @property
    def servo_period_ms(self):
        return self.servo_period / 8388608.

    @property
    def hw_clock(self):
        hw_clock = 512 * self.adc + 64 * self.dac + 8 * self.pfm + self.sclk
        if not (0 <= hw_clock <= 4095):
            raise ValueError('Hardware clock settings (adc, etc) out of range (i7003=%d)' %
                             hw_clock)
        return hw_clock

    @property
    def sclk_mhz(self):
        return 39.3216 / (2. ** self.sclk)

    @property
    def pfm_mhz(self):
        return 39.3216 / (2. ** self.pfm)

    @property
    def dac_mhz(self):
        return 39.3216 / (2. ** self.dac)

    @property
    def adc_mhz(self):
        return 39.3216 / (2. ** self.adc)

    @property
    def pwm_deadtime(self):
        # Deadtime is in units of 16*PWM_CLK cycles (or 0.135us) [ref: SRM pg 218]
        return int(self.pwm_deadtime_us / self.pwm_step)

    def motor_ect_starts(self):
        end_addrs = self.motor_ect_ends()
        return [self._ect_start_addr] + [addr + 1 for addr in end_addrs[:-1]]

    def motor_ect_ends(self):
        ends = []

        if self.dynamic_ect:
            # Dynamic ECT calculation takes the number of lines into account
            start = self._ect_start_addr
            for motor in self.motors:
                ends.append(start + motor.enc_lines - 1)
                start += motor.enc_lines
        else:
            # Static, however, has a fixed set of addresses
            for motor, ustep, other in zip(self.motors,
                                           self._microstep_static_ends,
                                           self._other_static_ends):
                if motor.uses_ustep:
                    ends.append(ustep)
                else:
                    ends.append(other)

        return ends

    def _check_clock(self):
        # Ensure the pwm frequency is exact
        self.pwm_freq = 117964.8 / (4 * self.pwm_period + 6)

        phase_freqs = self.phase_frequencies
        try:
            if self.phase_freq is not None:
                # TODO choose next closest, or best to be precise?
                phase_div = phase_freqs.index(self.phase_freq)
                phase_freq = self.phase_freq
            else:
                phase_div = self.phase_div
                phase_freq = phase_freqs[self.phase_div]
        except (IndexError, ValueError):
            raise ValueError('Phase frequency invalid (see get_phase_frequencies)')

        servo_freqs = self.servo_frequencies
        try:
            if self.servo_freq is not None:
                servo_div = servo_freqs.index(self.servo_freq)
                servo_freq = self.servo_freq
            else:
                servo_div = self.servo_div
                servo_freq = servo_freqs[self.servo_div]
        except (IndexError, ValueError):
            raise ValueError('Servo frequency invalid (see get_servo_frequencies)')

        self.phase_freq = phase_freq
        self.servo_freq = servo_freq
        self.phase_div = phase_div
        self.servo_div = servo_div
        return (servo_div, phase_div), (servo_freq, phase_freq)

    def get_servo_settings(self, ic):
        assert ic in range(0, 10), 'Invalid IC specified'

        divs, freqs = self._check_clock()
        servo_div, phase_div = divs
        servo_freq, phase_freq = freqs

        yield ''
        yield '// Servo IC {} frequency settings'.format(ic)
        yield 'I7{}00={:<5d}  // PWM frequency:   {:.4f} kHz'.format(ic, self.pwm_period, self.pwm_freq)
        yield 'I7{}01={:<5d}  // Phase frequency: {:.4f} kHz'.format(ic, phase_div, phase_freq)
        yield 'I7{}02={:<5d}  // Servo frequency: {:.4f} kHz'.format(ic, servo_div, servo_freq)
        yield 'I7{}03={:<5d}  // sclk={} pfm={} dac={} adc={} MHz'.format(
            ic, self.hw_clock, self.sclk_mhz, self.pfm_mhz, self.dac_mhz, self.adc_mhz)
        yield 'I7{}04={:<5d}  // PWM deadtime={} us'.format(ic, self.pwm_deadtime, self.pwm_deadtime_us)

    def get_servo_period(self):
        yield 'I10={}  // Servo period: {:.4f} ms'.format(self.servo_period, self.servo_period_ms)

    def get_macro_settings(self):
        divs, freqs = self._check_clock()
        servo_div, phase_div = divs
        servo_freq, phase_freq = freqs

        yield ''
        yield '// MACRO frequency settings'
        yield 'I6800={:<5d}  // PWM frequency:   {:.4f} kHz'.format(self.pwm_period, self.pwm_freq)
        yield 'I6801={:<5d}  // Phase frequency: {:.4f} kHz'.format(phase_div, phase_freq)
        yield 'I6802={:<5d}  // Servo frequency: {:.4f} kHz'.format(servo_div, servo_freq)

    def get_plc_setup(self, plc_num=1):
        yield ''
        yield '#define timer32     I6612'
        yield '#define msec32     *8388608/I10WHILE(I6612>0)ENDWHILE'
        yield ''

        yield 'OPEN PLC %d CLEAR' % plc_num
        yield 'DISABLE PLC 2..31'

        for motor in self.motors:
            for line in motor.plc_setup():
                yield line

            yield ''

        yield 'DISABLE PLC 1'
        yield 'CLOSE'

    def get_config(self):
        # Close any open PLCs
        yield 'CLOSE'

        # Delete the gather buffer
        yield 'DEL GAT'

        it_ = [self.get_servo_settings(0),
               self.get_macro_settings(),
               self.get_servo_settings(1),

               ['I5=2 // Background PLCs only'],
               self.get_plc_setup(),

               adc_mask_setup,
               ]

        for it in it_:
            for line in it:
                yield line

        motor_conf = [motor.get_config(use_comments=(i == 0))
                      for i, motor in enumerate(self.motors)]

        running = True
        while running:
            for conf in motor_conf:
                stop = []
                try:
                    line = next(conf)

                    if line.startswith('//'):
                        yield ''
                    yield line
                    if line.startswith('//'):
                        line = next(conf)
                        yield line
                except StopIteration:
                    stop.append(True)
                else:
                    stop.append(False)

            running = not any(stop)

    def get_pwm_sf(self, max_voltage):
        """
        Ref SRM pg 126:
            Some amplifiers require that the PWM command never turn fully on or off;
            in these amplifiers Ixx66 is usually set to about 95% of the PWM maximum count value.
        """
        # TODO pwm max
        # pwm_max = 0.95 * self.
        pwm_min = 0.95 * self.pwm_period
        sf = int(max_voltage / self.bus_voltage * self.pwm_period)
        return min(pwm_min, sf)

    @property
    def global_ect_setup(self):
        if self.dynamic_ect:
            yield '// Dynamic encoder conversion table'
        else:
            yield '// Static encoder conversion table'
            for line in static_ect_setup:
                yield static_ect_setup


if __name__ == '__main__':
    conf = LVConfig()
    motors = [LVMotor(conf, i,
                      'Stepper', 2.5, True, 13.1, True,
                      320, 1.13, 3.6, 'Micro Stepping', 32768,
                      3, 'Stepper Method', True,
                      1.8, 2000, 26,

                      cur_loop_bandwidth=300,
                      cur_loop_damping=0.707,
                      micro_stepping=65536)
              for i in range(1, 9)]

    for m in motors:
        conf.add_motor(m)

    for line in conf.get_config():
        print(line)

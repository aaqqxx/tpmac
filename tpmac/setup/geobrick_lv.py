'''
'''

from __future__ import print_function
# import numpy as np
from collections import namedtuple


def get_servo_frequencies(pwm_freq):
    return [(pwm_freq / (divider + 1))
            for divider in range(16)]


def get_phase_frequencies(pwm_freq):
    return [((2. * pwm_freq) / (divider + 1))
            for divider in range(16)]


# TODO individual servo ic config

motor_types = ['None',
               'Brush',
               'Brushless',
               'Stepper'
               ]


mtype = namedtuple('MotorType', ['type_setting',
                                 'clear_fault',
                                 'protection'])


mtype_info = {'None': mtype('NONE', 'CCFE', '0CFE'),
              'Brush': mtype('4CFE', 'CCFE', '0CFE'),
              'Brushless': mtype('4CFE', 'CCFE', '0CFE'),
              'Stepper': mtype('4DFE', 'CDFE', '0DFE'),
              }


ect_options = ['Dynamic', 'Static']


ect_type = namedtuple('EncoderType', ['lines', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8'])

ect_info = {'Quadrature': ect_type(1., '$78000', '$78008', '$78010', '$78018', '$78100', '$78108', '$78110', '$78118'),
            'Sin/Cos': ect_type(3., '$FF8000,$78B00,$0', '$FF8008,$78B02,$0', '$FF8010,$78B04,$0', '$FF8018,$78B06,$0', '$FF8100,$78B08,$0', '$FF8108,$78B0A,$0', '$FF8110,$78B0C,$0', '$FF8118,$78B0E,$0'),
            'Resolver': ect_type(8., '$F78B00,$478B10,$0,$D83503,$400,$80000,$0,$1', '$F78B02,$478B10,$000000,$D8350B,$400,$80000,$0,$1', '$F78B04,$478B10,$000000,$D83513,$400,$80000,$0,$1', '$F78B06,$478B10,$000000,$D8351B,$400,$80000,$0,$1', '$F78B08,$478B10,$000000,$D83523,$400,$80000,$0,$1', '$F78B0A,$478B10,$000000,$D8352B,$400,$80000,$0,$1', '$F78B0C,$478B10,$000000,$D83533,$400,$80000,$0,$1', '$F78B0E,$478B10,$000000,$D8353B,$400,$80000,$0,$1'),
            'SSI': ect_type(2., '$278B20,$18000', '$278B24,$18000', '$278B28,$18000', '$278B2C,$18000', '$278B30,$18000', '$278B34,$18000', '$278B38,$18000', '$278B3C,$18000'),
            'Endat2.2': ect_type(2., '$278B20,$18000', '$278B24,$18000', '$278B28,$18000', '$278B2C,$18000', '$278B30,$18000', '$278B34,$18000', '$278B38,$18000', '$278B3C,$18000'),
            'Yaskawa Abs 16bit': ect_type(2., '$278B20,$020004', '$278B24,$020004', '$278B28,$020004', '$278B2C,$020004', '$278B30,$020004', '$278B34,$020004', '$278B38,$020004', '$278B3C,$020004'),
            'Yaskawa Abs 17bit': ect_type(2., '$278B20,$021004', '$278B24,$021004', '$278B28,$021004', '$278B2C,$021004', '$278B30,$021004', '$278B34,$021004', '$278B38,$021004', '$278B3C,$021004'),
            'Yaskawa Abs 20bit': ect_type(2., '$278B20,$024004', '$278B24,$024004', '$278B28,$024004', '$278B2C,$024004', '$278B30,$024004', '$278B34,$024004', '$278B38,$024004', '$278B3C,$024004'),
            'Yaskawa Inc 13bit': ect_type(2., '$278B20,$00D006', '$278B24,$00D006', '$278B28,$00D006', '$278B2C,$00D006', '$278B30,$00D006', '$278B34,$00D006', '$278B38,$00D006', '$278B3C,$00D006'),
            'Yaskawa Inc 17bit': ect_type(2., '$278B20,$011006', '$278B24,$011006', '$278B28,$011006', '$278B2C,$011006', '$278B30,$011006', '$278B34,$011006', '$278B38,$011006', '$278B3C,$011006'),
            'Panasonic': ect_type(2., '$278B20,$18000', '$278B24,$18000', '$278B28,$18000', '$278B2C,$18000', '$278B30,$18000', '$278B34,$18000', '$278B38,$18000', '$278B3C,$18000'),
            'Tamagawa': ect_type(2., '$278B20,$18000', '$278B24,$18000', '$278B28,$18000', '$278B2C,$18000', '$278B30,$18000', '$278B34,$18000', '$278B38,$18000', '$278B3C,$18000'),
            'Biss B/C': ect_type(2., '$278B20,$18000', '$278B24,$18000', '$278B28,$18000', '$278B2C,$18000', '$278B30,$18000', '$278B34,$18000', '$278B38,$18000', '$278B3C,$18000'),
            'Micro Stepping': ect_type(3., '$6800BF,$018018,$EC0001', '$68013F,$018018,$EC0003', '$6801BF,$018018,$EC0005', '$68023F,$018018,$EC0007', '$6802BF,$018018,$EC0009', '$68033F,$018018,$EC000B', '$6803BF,$018018,$EC000D', '$68043F,$018018,$EC000F'),
            }


dyn_ect_type = namedtuple('DynamicECT', ['enc_type', 'lines', 'start_addr', 'end_addr', 'ect_setting'])
dynamic_ect = [dyn_ect_type('Biss B/C', 2.0, 0x3501, 0x3502, '$278B20,$18000'),
               dyn_ect_type('Biss B/C', 2.0, 0x3503, 0x3504, '$278B24,$18000'),
               dyn_ect_type('Biss B/C', 2.0, 0x3505, 0x3506, '$278B28,$18000'),
               dyn_ect_type('Biss B/C', 2.0, 0x3507, 0x3508, '$278B2C,$18000'),
               dyn_ect_type('Biss B/C', 2.0, 0x3509, 0x350A, '$278B30,$18000'),
               dyn_ect_type('Biss B/C', 2.0, 0x350B, 0x350C, '$278B34,$18000'),
               dyn_ect_type('Biss B/C', 2.0, 0x350D, 0x350E, '$278B38,$18000'),
               dyn_ect_type('Biss B/C', 2.0, 0x350F, 0x3510, '$278B3C,$18000'),
               ]

static_ects = [
    '$78000,$78008,$78010,$78018,$78100,$78108,$78110,$78118'
    '$6800BF,$018018,$EC0009,$68013F,$018018,$EC000C,$6801BF,$018018,$EC000F,$68023F,$018018,$EC0012,$6802BF,$018018,$EC0015,$68033F,$018018,$EC0018,$6803BF,$018018,$EC001B,$68043F,$018018,$EC001E',
]

static_ect_type = namedtuple('StaticECT', ['enc_type', 'end_addr'])
static_ect = [static_ect_type('Biss B/C', 3501),
              static_ect_type('Biss B/C', 3502),
              static_ect_type('Biss B/C', 3503),
              static_ect_type('Biss B/C', 3504),
              static_ect_type('Biss B/C', 3505),
              static_ect_type('Biss B/C', 3506),
              static_ect_type('Biss B/C', 3507),
              static_ect_type('Biss B/C', 3508),
              ]

current_units = ['RMS', 'Peak']
overtravel = ['Disabled', 'Enabled']
phasing_methods = ['2-Guess Method',
                   'Stepper Method',
                   'Hall Sensors',
                   ]


class LVConfig(object):
    def __init__(self, pwm_freq=19.6608, phase_freq=None, servo_freq=None,
                 phase_div=1, servo_div=3,
                 sclk=2, pfm=2, dac=3, adc=3,
                 pwm_deadtime=0.54,

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

        self.pwm_freq = pwm_freq
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

        if not (0 <= self.pwm_deadtime <= 255):
            raise ValueError('PWM deadtime settings out of range')

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
        # Deadtime is in units of 16*PWM_CLK cycles (or 0.135us) [ref: pg 218]
        return int(self.pwm_deadtime_us / self.pwm_step)

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

    def get_plc_setup(self):
        yield ''
        yield '#define timer32     I6612'
        yield '#define msec32     *8388608/I10WHILE(I6612>0)ENDWHILE'
        yield ''

        yield 'OPEN PLC %d CLEAR'
        yield 'DISABLE PLC 2..31'

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
               self.get_plc_setup(),
                # TODO
               self.config_motor(1),
               ]

        for it in it_:
            for line in it:
                yield line

    def get_pwm_sf(self, max_voltage):
        """
        Ref pg 126:
            Some amplifiers require that the PWM command never turn fully on or off;
            in these amplifiers Ixx66 is usually set to about 95% of the PWM maximum count value.
        """
        # TODO pwm max
        # pwm_max = 0.95 * self.
        return int(max_voltage / self.bus_voltage * self.pwm_period)

    def config_motor(self, mnum, sleep_time=50,
                     motor_type='Stepper'):

        assert motor_type in motor_types, 'Invalid motor type'

        assert mnum in range(1, 9), 'Motor number out of range'

        minfo = mtype_info[motor_type]
        # 78014 for motors 1-4, 78114 for motors 5-8
        if mnum <= 4:
            addr0 = 0x78014
        else:
            addr0 = 0x78114

        def _clear_fault():
            if mnum <= 4:
                idx = 7 + mnum
            else:
                idx = 7 + (mnum - 4)

            return '$F{:X}{}'.format(idx, minfo.clear_fault)

        def _motor_type():
            if mnum <= 4:
                idx = 7 + mnum
            else:
                idx = 7 + (mnum - 4)

            return '$F{:X}{}'.format(idx, minfo.type_setting)

        def _protection():
            if mnum <= 4:
                idx = mnum - 1
            else:
                idx = mnum - 5

            return '$F{:X}{}'.format(idx, minfo.protection)

        cmd_str = 'CMD"WX:${:X},%s"          // %s'.format(addr0, )

        sleep_str = 'timer32 = %d msec32' % sleep_time
        init_plc = [sleep_str,
                    cmd_str % (_clear_fault(), 'Motor #%d CLRF' % mnum),
                    sleep_str,
                    cmd_str % (_motor_type(), 'Motor #%d Type' % mnum),
                    sleep_str,
                    cmd_str % (_protection(), 'Motor #%d Protection' % mnum),
                    sleep_str,
                    ]
        for line in init_plc:
            yield line

if __name__ == '__main__':
    conf = LVConfig()
    for line in conf.get_config():
        print(line)


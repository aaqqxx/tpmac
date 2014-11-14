'''
'''

import numpy as np


def get_servo_frequencies(pwm_freq):
    return [(pwm_freq / (divider + 1))
            for divider in range(16)]


def get_phase_frequencies(pwm_freq):
    return [((2. * pwm_freq) / (divider + 1))
            for divider in range(16)]


# TODO individual servo ic config

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

        phase_freqs = get_phase_frequencies(self.pwm_freq)

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

        servo_freqs = get_servo_frequencies(self.pwm_freq)

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
               ]

        for it in it_:
            for line in it:
                yield line


if __name__ == '__main__':
    conf = LVConfig()
    for line in conf.get_config():
        print(line)

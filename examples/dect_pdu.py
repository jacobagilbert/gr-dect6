#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: DECT PDU Demod
# Author: J. Gilbert
# Copyright: J. Gilbert
# Description: DECT 6.0 PDU based demodulator
# GNU Radio version: v3.10.0.0git-544-gce99f57b

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from energy_tagger import energy_tagger  # grc-generated hier_block
from gnuradio import filter
from gnuradio import gr
from gnuradio.fft import window
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import pdu
import pmt
from gnuradio import uhd
import time
from gnuradio.filter import pfb
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore
import dect6
import pdu_utils



from gnuradio import qtgui

class dect_pdu(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "DECT PDU Demod", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("DECT PDU Demod")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "dect_pdu")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.dect_symbol_rate = dect_symbol_rate = 1152000
        self.threshold = threshold = 0.0002
        self.samp_rate = samp_rate = 8e6
        self.n = n = 8*40
        self.m = m = 8*8
        self.gain = gain = 40
        self.freq = freq = 1921.55
        self.fc = fc = 250000
        self.dect_obw = dect_obw = 1.2*dect_symbol_rate

        ##################################################
        # Blocks
        ##################################################
        self._threshold_range = Range(0.00001, 0.01, 0.00001, 0.0002, 200)
        self._threshold_win = RangeWidget(self._threshold_range, self.set_threshold, 'Threshold', "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._threshold_win, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._gain_range = Range(0, 76, 1, 40, 200)
        self._gain_win = RangeWidget(self._gain_range, self.set_gain, 'Gain', "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._gain_win, 0, 0, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._freq_range = Range(1920.0, 1926.0, 0.05, 1921.55, 200)
        self._freq_win = RangeWidget(self._freq_range, self.set_freq, 'Frequency (MHz)', "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._freq_win, 1, 0, 1, 2)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.waterfall = qtgui.waterfall_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            1, #number of inputs
            None # parent
        )
        self.waterfall.set_update_time(.002)
        self.waterfall.enable_grid(False)
        self.waterfall.enable_axis_labels(True)



        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.waterfall.set_line_label(i, "Data {0}".format(i))
            else:
                self.waterfall.set_line_label(i, labels[i])
            self.waterfall.set_color_map(i, colors[i])
            self.waterfall.set_line_alpha(i, alphas[i])

        self.waterfall.set_intensity_range(-140, 10)

        self._waterfall_win = sip.wrapinstance(self.waterfall.qwidget(), Qt.QWidget)

        self.top_grid_layout.addWidget(self._waterfall_win, 4, 0, 3, 1)
        for r in range(4, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.usrp = uhd.usrp_source(
            ",".join(('', "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.usrp.set_samp_rate(samp_rate)
        self.usrp.set_time_unknown_pps(uhd.time_spec(0))

        self.usrp.set_center_freq(freq*1e6, 0)
        self.usrp.set_antenna('RX2', 0)
        self.usrp.set_gain(gain, 0)
        self.unpack = pdu_utils.pack_unpack(pdu_utils.MODE_UNPACK_BYTE, pdu_utils.BIT_ORDER_MSB_FIRST)
        self.ts = qtgui.time_sink_f(
            1024, #size
            dect_symbol_rate, #samp_rate
            "Soft Symbols", #name
            0, #number of inputs
            None # parent
        )
        self.ts.set_update_time(0.10)
        self.ts.set_y_axis(-1, 1)

        self.ts.set_y_label('Amplitude', "")

        self.ts.enable_tags(True)
        self.ts.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.ts.enable_autoscale(False)
        self.ts.enable_grid(False)
        self.ts.enable_axis_labels(True)
        self.ts.enable_control_panel(False)
        self.ts.enable_stem_plot(True)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.ts.set_line_label(i, "Data {0}".format(i))
            else:
                self.ts.set_line_label(i, labels[i])
            self.ts.set_line_width(i, widths[i])
            self.ts.set_line_color(i, colors[i])
            self.ts.set_line_style(i, styles[i])
            self.ts.set_line_marker(i, markers[i])
            self.ts.set_line_alpha(i, alphas[i])

        self._ts_win = sip.wrapinstance(self.ts.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._ts_win, 4, 1, 1, 1)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.time_sink1 = qtgui.time_sink_f(
            4096, #size
            samp_rate, #samp_rate
            "", #name
            2, #number of inputs
            None # parent
        )
        self.time_sink1.set_update_time(0.10)
        self.time_sink1.set_y_axis(-1, 1)

        self.time_sink1.set_y_label('Amplitude', "")

        self.time_sink1.enable_tags(True)
        self.time_sink1.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.0, .0001, 1, "SOB")
        self.time_sink1.enable_autoscale(False)
        self.time_sink1.enable_grid(False)
        self.time_sink1.enable_axis_labels(True)
        self.time_sink1.enable_control_panel(False)
        self.time_sink1.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                self.time_sink1.set_line_label(i, "Data {0}".format(i))
            else:
                self.time_sink1.set_line_label(i, labels[i])
            self.time_sink1.set_line_width(i, widths[i])
            self.time_sink1.set_line_color(i, colors[i])
            self.time_sink1.set_line_style(i, styles[i])
            self.time_sink1.set_line_marker(i, markers[i])
            self.time_sink1.set_line_alpha(i, alphas[i])

        self._time_sink1_win = sip.wrapinstance(self.time_sink1.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._time_sink1_win, 3, 1, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.tags2pdu = pdu.tags_to_pdu_f(pmt.intern('SOB'), pmt.intern('EOB'), 4096, dect_symbol_rate*4, [], False, 0, 0.0)
        self.tags2pdu.set_eob_parameters(1, 0)
        self.tags2pdu.enable_time_debug(False)
        self.raster = qtgui.time_raster_sink_b(
            samp_rate,
            m,
            n,
            [],
            [],
            "",
            0,
            None
        )

        self.raster.set_update_time(0.10)
        self.raster.set_intensity_range(-1, 1)
        self.raster.enable_grid(False)
        self.raster.enable_axis_labels(True)
        self.raster.set_x_label("")
        self.raster.set_x_range(0.0, 0.0)
        self.raster.set_y_label("")
        self.raster.set_y_range(0.0, 0.0)

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [2, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.raster.set_line_label(i, "Data {0}".format(i))
            else:
                self.raster.set_line_label(i, labels[i])
            self.raster.set_color_map(i, colors[i])
            self.raster.set_line_alpha(i, alphas[i])

        self._raster_win = sip.wrapinstance(self.raster.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._raster_win, 5, 1, 1, 1)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.01)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 3, 0, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.pack = pdu_utils.pack_unpack(pdu_utils.MODE_PACK_BYTE, pdu_utils.BIT_ORDER_MSB_FIRST)
        self.input_resamp = pfb.arb_resampler_ccf(
            4*dect_symbol_rate / (samp_rate),
            taps=None,
            flt_size=32)
        self.input_resamp.declare_sample_delay(0)
        self.head_tail = pdu_utils.pdu_head_tail(pdu_utils.INPUTTYPE_UNPACKED_BYTE, n, m)
        self.energy_tagger = energy_tagger(
            threshold=threshold,
        )
        self.dect_deframer = dect6.dect_deframer()
        self.clock_recovery_0 = pdu_utils.pdu_clock_recovery(False, False, pdu_utils.TUKEY_WIN)
        self.clock_recovery = pdu_utils.pdu_clock_recovery(True, False, pdu_utils.TUKEY_WIN)
        self.chan_filt = filter.fir_filter_ccf(1, firdes.low_pass_2(1, 1, 0.1, 0.025, 50))
        self.chan_filt.declare_sample_delay(0)
        self.align = pdu_utils.pdu_align('10101010101010101110100110001010, 01010101010101010001011001110101', 0, -32)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.align, 'pdu_out'), (self.pack, 'pdu_in'))
        self.msg_connect((self.clock_recovery, 'pdu_out'), (self.align, 'pdu_in'))
        self.msg_connect((self.clock_recovery_0, 'pdu_out'), (self.ts, 'in'))
        self.msg_connect((self.dect_deframer, 'pdu'), (self.unpack, 'pdu_in'))
        self.msg_connect((self.head_tail, 'head'), (self.raster, 'in'))
        self.msg_connect((self.pack, 'pdu_out'), (self.dect_deframer, 'pdu'))
        self.msg_connect((self.tags2pdu, 'pdus'), (self.clock_recovery, 'pdu_in'))
        self.msg_connect((self.tags2pdu, 'pdus'), (self.clock_recovery_0, 'pdu_in'))
        self.msg_connect((self.unpack, 'pdu_out'), (self.head_tail, 'pdu_in'))
        self.connect((self.chan_filt, 0), (self.input_resamp, 0))
        self.connect((self.energy_tagger, 0), (self.tags2pdu, 0))
        self.connect((self.energy_tagger, 0), (self.time_sink1, 1))
        self.connect((self.energy_tagger, 1), (self.time_sink1, 0))
        self.connect((self.input_resamp, 0), (self.energy_tagger, 0))
        self.connect((self.input_resamp, 0), (self.waterfall, 0))
        self.connect((self.usrp, 0), (self.chan_filt, 0))
        self.connect((self.usrp, 0), (self.qtgui_freq_sink_x_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "dect_pdu")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_dect_symbol_rate(self):
        return self.dect_symbol_rate

    def set_dect_symbol_rate(self, dect_symbol_rate):
        self.dect_symbol_rate = dect_symbol_rate
        self.set_dect_obw(1.2*self.dect_symbol_rate)
        self.input_resamp.set_rate(4*self.dect_symbol_rate / (self.samp_rate))
        self.tags2pdu.set_rate(self.dect_symbol_rate*4)
        self.ts.set_samp_rate(self.dect_symbol_rate)

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold
        self.energy_tagger.set_threshold(self.threshold)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.input_resamp.set_rate(4*self.dect_symbol_rate / (self.samp_rate))
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.time_sink1.set_samp_rate(self.samp_rate)
        self.usrp.set_samp_rate(self.samp_rate)
        self.waterfall.set_frequency_range(0, self.samp_rate)

    def get_n(self):
        return self.n

    def set_n(self, n):
        self.n = n
        self.head_tail.set_length(self.n)
        self.raster.set_num_cols(self.n)

    def get_m(self):
        return self.m

    def set_m(self, m):
        self.m = m
        self.head_tail.set_histsize(self.m)
        self.raster.set_num_rows(self.m)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.usrp.set_gain(self.gain, 0)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.usrp.set_center_freq(self.freq*1e6, 0)

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc

    def get_dect_obw(self):
        return self.dect_obw

    def set_dect_obw(self, dect_obw):
        self.dect_obw = dect_obw




def main(top_block_cls=dect_pdu, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()

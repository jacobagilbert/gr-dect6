#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: v3.10.0.0git-486-g8adfad0a

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

from gnuradio import analog
import math
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation



from gnuradio import qtgui

class energy_tagger(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
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

        self.settings = Qt.QSettings("GNU Radio", "energy_tagger")

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
        self.samp_rate = samp_rate = 32000

        ##################################################
        # Blocks
        ##################################################
        self.thresh = blocks.threshold_ff(0.0002/4, 0.0002, 0)
        self.tagger = blocks.burst_tagger(gr.sizeof_float)
        self.tagger.set_true_tag('SOB',True)
        self.tagger.set_false_tag('EOB',True)
        self.s2f = blocks.short_to_float(1, 1)
        self.null = blocks.null_sink(gr.sizeof_float*1)
        self.ma = blocks.moving_average_ff(64, 1.0/64, 4000, 1)
        self.fm_demod_0 = analog.quadrature_demod_cf(1)
        self.fm_delay = blocks.delay(gr.sizeof_float*1, 0)
        self.f2s = blocks.float_to_short(1, 1)
        self.bbfilt = filter.fir_filter_fff(1, firdes.gaussian(-2, 4, 1.2, 63))
        self.bbfilt.declare_sample_delay(0)
        self.am_demod_0 = blocks.complex_to_mag_squared(1)
        self.am_delay = blocks.delay(gr.sizeof_short*1, 32)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.am_delay, 0), (self.s2f, 0))
        self.connect((self.am_delay, 0), (self.tagger, 1))
        self.connect((self.am_demod_0, 0), (self.ma, 0))
        self.connect((self.bbfilt, 0), (self.fm_delay, 0))
        self.connect((self.f2s, 0), (self.am_delay, 0))
        self.connect((self.fm_delay, 0), (self.tagger, 0))
        self.connect((self.fm_demod_0, 0), (self.bbfilt, 0))
        self.connect((self, 0), (self.am_demod_0, 0))
        self.connect((self, 0), (self.fm_demod_0, 0))
        self.connect((self.ma, 0), (self.thresh, 0))
        self.connect((self.s2f, 0), (self.null, 0))
        self.connect((self.s2f, 0), (self, 1))
        self.connect((self.tagger, 0), (self, 0))
        self.connect((self.thresh, 0), (self.f2s, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "energy_tagger")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate




def main(top_block_cls=energy_tagger, options=None):

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

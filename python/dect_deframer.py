#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2021 J. Gilbert.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
import pmt
from gnuradio import gr


RFP_SYNC_WORD = [0xAA, 0xAA, 0xE9, 0x8A]
PP_SYNC_WORD =  [0x55, 0x55, 0x16, 0x75]

SCRT = [[0x3B, 0xCD, 0x21, 0x5D, 0x88, 0x65, 0xBD, 0x44, 0xEF, 0x34, 0x85, 0x76, 0x21, 0x96, 0xF5, 0x13, 0xBC, 0xD2, 0x15, 0xD8, 0x86, 0x5B, 0xD4, 0x4E, 0xF3, 0x48, 0x57, 0x62, 0x19, 0x6F, 0x51],
        [0x32, 0xDE, 0xA2, 0x77, 0x9A, 0x42, 0xBB, 0x10, 0xCB, 0x7A, 0x89, 0xDE, 0x69, 0x0A, 0xEC, 0x43, 0x2D, 0xEA, 0x27, 0x79, 0xA4, 0x2B, 0xB1, 0x0C, 0xB7, 0xA8, 0x9D, 0xE6, 0x90, 0xAE, 0xC4],
        [0x2D, 0xEA, 0x27, 0x79, 0xA4, 0x2B, 0xB1, 0x0C, 0xB7, 0xA8, 0x9D, 0xE6, 0x90, 0xAE, 0xC4, 0x32, 0xDE, 0xA2, 0x77, 0x9A, 0x42, 0xBB, 0x10, 0xCB, 0x7A, 0x89, 0xDE, 0x69, 0x0A, 0xEC, 0x43],
        [0x27, 0x79, 0xA4, 0x2B, 0xB1, 0x0C, 0xB7, 0xA8, 0x9D, 0xE6, 0x90, 0xAE, 0xC4, 0x32, 0xDE, 0xA2, 0x77, 0x9A, 0x42, 0xBB, 0x10, 0xCB, 0x7A, 0x89, 0xDE, 0x69, 0x0A, 0xEC, 0x43, 0x2D, 0xEA],
        [0x19, 0x6F, 0x51, 0x3B, 0xCD, 0x21, 0x5D, 0x88, 0x65, 0xBD, 0x44, 0xEF, 0x34, 0x85, 0x76, 0x21, 0x96, 0xF5, 0x13, 0xBC, 0xD2, 0x15, 0xD8, 0x86, 0x5B, 0xD4, 0x4E, 0xF3, 0x48, 0x57, 0x62],
        [0x13, 0xBC, 0xD2, 0x15, 0xD8, 0x86, 0x5B, 0xD4, 0x4E, 0xF3, 0x48, 0x57, 0x62, 0x19, 0x6F, 0x51, 0x3B, 0xCD, 0x21, 0x5D, 0x88, 0x65, 0xBD, 0x44, 0xEF, 0x34, 0x85, 0x76, 0x21, 0x96, 0xF5],
        [0x0C, 0xB7, 0xA8, 0x9D, 0xE6, 0x90, 0xAE, 0xC4, 0x32, 0xDE, 0xA2, 0x77, 0x9A, 0x42, 0xBB, 0x10, 0xCB, 0x7A, 0x89, 0xDE, 0x69, 0x0A, 0xEC, 0x43, 0x2D, 0xEA, 0x27, 0x79, 0xA4, 0x2B, 0xB1],
        [0x79, 0xA4, 0x2B, 0xB1, 0x0C, 0xB7, 0xA8, 0x9D, 0xE6, 0x90, 0xAE, 0xC4, 0x32, 0xDE, 0xA2, 0x77, 0x9A, 0x42, 0xBB, 0x10, 0xCB, 0x7A, 0x89, 0xDE, 0x69, 0x0A, 0xEC, 0x43, 0x2D, 0xEA, 0x27]]


class dect_deframer(gr.basic_block):
    """
    docstring for block dect_deframer
    """
    def __init__(self):
        gr.basic_block.__init__(self,
            name="dect_deframer",
            in_sig=None,
            out_sig=None)

        self.rfp_frame_num = 0
        self.pp_frame_num = 0
        self.message_port_register_in(pmt.intern("pdu"))
        self.set_msg_handler(pmt.intern("pdu"), self.handler)
        self.message_port_register_out(pmt.intern("pdu"));

    def handler(self, pdu):
        """
        """
        if not pmt.is_pdu(pdu):
            print('input is not a PDU!, dropping')
        
        try:
            meta = pmt.car(pdu)
            data = pmt.u8vector_elements(pmt.cdr(pdu))
        except Exception as e:
            gr.log.error("failed to parse PDU because",e)
            return
            
        if len(data) < 54:
            gr.log.error("PDU is too short, dropping")
            return
        
        # check if Radio Fixed Part or Portable Part:
        part = "RFP"
        if data[0:4]==PP_SYNC_WORD:
            part = "PP"
        elif not data[0:4]==RFP_SYNC_WORD:
            gr.log.error("invalid sync word (not PP/RFP)")
            return
        meta = pmt.dict_add(meta, pmt.intern("part"), pmt.intern(part))
        meta = pmt.dict_add(meta, pmt.intern("rx_seq"), pmt.from_uint64(3))
        meta = pmt.dict_add(meta, pmt.intern("a_crc_ok"), pmt.PMT_T)
        
        a_field = data[4:12]
        a_crc = a_field[6]*256 + a_field[7]
        a_header_ta = (a_field[0] >> 5) & 0x03
        a_header_ba = (a_field[0] >> 1) & 0x03

        if a_header_ta == 3:
            if part == "RFP":
                self.rfp_frame_num = (self.rfp_frame_num + 1) % 8
            else:
                self.pp_frame_num = (self.pp_frame_num + 1) % 8
            part_id = 0
            for ii in range(5):
                part_id = (part_id << 8) + a_field[ii+1]
            meta = pmt.dict_add(meta, pmt.intern("part_id"), pmt.intern(hex(part_id)))
        elif a_header_ta == 4:
            if part == "RFP":
                self.rfp_frame_num = 0
            else:
                self.pp_frame_num = 0
        frame_num = self.pp_frame_num
        if part == "RFP":
            frame_num = 0
        meta = pmt.dict_add(meta, pmt.intern("frame_num"), pmt.from_uint64(frame_num))

        
        if a_header_ba == 0:
            meta = pmt.dict_add(meta, pmt.intern("audio"), pmt.PMT_T)
        else:
            meta = pmt.dict_add(meta, pmt.intern("audio"), pmt.PMT_F)

        out = np.array([0]*48,dtype=np.uint8)
        out[0:8] = a_field
        for ii in range(0,40):
            out[ii+8] = data[12+ii] ^ SCRT[frame_num-1][ii%31]

        #self.message_port_pub(pmt.intern("pdu"), pmt.cons(meta, pmt.cdr(pdu)))
        self.message_port_pub(pmt.intern("pdu"), pmt.cons(meta, pmt.init_u8vector(40,out)))        


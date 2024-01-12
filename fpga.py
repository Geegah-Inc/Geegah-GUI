# -*- coding: utf-8 -*-
"""
@author: rainer
"""
import ok
import datetime
import math

class fpga:
    class RegField:
        def __init__(self, regaddr, width, offset):
            self.regaddr = regaddr
            self.width = width
            self.offset = offset

    class Timing:
        def __init__(self, signum, rf_istate, rf_itog1, rf_itog2, rf_qtog1, rf_qtog2):
            self.signum = signum
            self.rf_istate = rf_istate
            self.rf_itog1 = rf_itog1
            self.rf_itog2 = rf_itog2
            self.rf_qtog1 = rf_qtog1
            self.rf_qtog2 = rf_qtog2
            
    def __init__(self):
        self.dev = ok.okCFrontPanel()
        self.dev.OpenBySerial()
        self.di = ok.okTDeviceInfo()
        self.dev.GetDeviceInfo(self.di)
        self.block_size = 1024
        
    def Open(self):
        self.dev = ok.okCFrontPanel()
        self.dev.OpenBySerial()
        self.di = ok.okTDeviceInfo()
        self.dev.GetDeviceInfo(self.di)
        self.block_size = 1024

    def USB_Speed(self):
        return self.di.usbSpeed

    def BoardName(self):
        return self.di.productName
    
    def Close(self):
        self.dev.Close()

    def Configure(self, bitfile):
        self.dev.ConfigureFPGA(bitfile)

    def GetRegister(self, addr):
        return self.dev.ReadRegister(addr)
    
    def SetRegister(self, addr, value):
        self.dev.WriteRegister(addr, value)

    def GetRegField(self, rf):
        regval = self.GetRegister(rf.regaddr)
        mask = ((2**rf.width)-1) << rf.offset
        return (regval & mask) >> rf.offset

    def SetRegField(self, rf, val):
        regval = self.dev.ReadRegister(rf.regaddr)
        mask = ((2**rf.width)-1) << rf.offset
        wrval = (val << rf.offset) & mask
        # Clear the bits
        regval = regval & ~mask
        # Or in the new bits
        regval = regval | wrval
        # Write it back out
        self.dev.WriteRegister(rf.regaddr, regval)

    ##########################################################################
    # Register addresses
    ##########################################################################
    r_miscctrl  = 0x0000
    r_trig0     = 0x0003
    r_sysfreq   = 0x0006
    # Acquisition control
    r_acqctrl   = 0x0010
    r_acqlisten = 0x0011
    r_acqroi    = 0x0012
    # 1x16 column selections
    r_colsel    = 0x0016
    # Pattern generator
    r_patgen = 0x0020
    # DAC
    r_dac_ctrl  = 0x0030
    # ADC
    r_adcdata  = 0x0040
    # Timing control registers
    r_timing_ctrl  = 0x0050
    r_i_toggle1_01 = 0x0051
    r_i_toggle1_23 = 0x0052
    r_i_toggle1_45 = 0x0053
    r_i_toggle1_67 = 0x0054
    r_i_toggle2_01 = 0x0055
    r_i_toggle2_23 = 0x0056
    r_i_toggle2_45 = 0x0057
    r_i_toggle2_67 = 0x0058
    r_q_toggle1_01 = 0x0059
    r_q_toggle1_23 = 0x005A
    r_q_toggle1_45 = 0x005B
    r_q_toggle1_67 = 0x005C
    r_q_toggle2_01 = 0x005D
    r_q_toggle2_23 = 0x005E
    r_q_toggle2_45 = 0x005F
    r_q_toggle2_67 = 0x0060

    # SPI - both VCO and iNEMO
    r_vco_spi_wdata   = 0x0070
    r_inemo_spi_wdata = 0x0071
    r_inemo_spi_rdata = 0x0072

    # Miscellaneous
    r_sentinel   = 0x1234
    r_version    = 0xFFF8
    r_time_stamp = 0xFFF9
    r_ser_num    = 0xFFFA

    ##########################################################################
    # Register Bit Fields. The arguments are
    #    register address
    #    width, in bits
    #    offset, or which bit in the register contains the LSB of the field
    # Many bit fields are just one bit wide.
    ##########################################################################
    # Control register
    disable_blinky  = RegField(r_miscctrl, 1, 0)
    software_reset  = RegField(r_miscctrl, 1, 1)
    xfer_enable     = RegField(r_miscctrl, 1, 2)
    okf_reset       = RegField(r_miscctrl, 1, 3)
    ok_led          = RegField(r_miscctrl, 4, 4)
    adc_select      = RegField(r_miscctrl, 1, 8)
    adc_usefake     = RegField(r_miscctrl, 1, 9)
    single_pixel    = RegField(r_miscctrl, 1, 10)
    fixed_col       = RegField(r_miscctrl, 7, 11)
    fixed_row       = RegField(r_miscctrl, 7, 18)
    pdbrf           = RegField(r_miscctrl, 1, 25)

    # Trigger register
    vco_spi_go      = RegField(r_trig0, 1, 0)
    dac_wren        = RegField(r_trig0, 1, 1)
    inemo_spi_go    = RegField(r_trig0, 1, 2)

    # Frequencies
    sysclk_freq = RegField(r_sysfreq, 20, 0)

    # Acquisition control
    acq_start     = RegField(r_acqctrl, 1, 0)
    ignore_first  = RegField(r_acqctrl, 1, 1)
    acq_navg      = RegField(r_acqctrl, 8, 8)
    acq_lastframe = RegField(r_acqctrl, 16, 16)

    listen_col_off = RegField(r_acqlisten, 8, 0)
    listen_row_off = RegField(r_acqlisten, 8, 8)

    roi_start_col = RegField(r_acqroi, 8, 0)
    roi_end_col   = RegField(r_acqroi, 8, 8)
    roi_start_row = RegField(r_acqroi, 8, 16)
    roi_end_row   = RegField(r_acqroi, 8, 24)

    # 1x16 column selections
    init_tx_colmask_1x16 = RegField(r_colsel, 16, 0)
    init_rx_colnum_1x16 = RegField(r_colsel, 4, 16)

    # Pattern generator
    pgen_enable = RegField(r_patgen, 1, 0)
    pgen_patsel = RegField(r_patgen, 3, 1)
    use_pgen    = RegField(r_patgen, 1, 4)

    # DAC
    dac_addr         = RegField(r_dac_ctrl, 15, 0)
    dac_data         = RegField(r_dac_ctrl, 12, 16)
    
    # ADC
    adc_data  = RegField(r_adcdata, 12, 0)

    # Timing control
    initial_states = RegField(r_timing_ctrl, 16, 0)
    initial_state_0 = RegField(r_timing_ctrl, 1, 0)
    initial_state_1 = RegField(r_timing_ctrl, 1, 1)
    initial_state_2 = RegField(r_timing_ctrl, 1, 2)
    initial_state_3 = RegField(r_timing_ctrl, 1, 3)
    initial_state_4 = RegField(r_timing_ctrl, 1, 4)
    initial_state_5 = RegField(r_timing_ctrl, 1, 5)
    initial_state_6 = RegField(r_timing_ctrl, 1, 6)
    term_count = RegField(r_timing_ctrl, 16, 16)
    I_toggle1_0 = RegField(r_i_toggle1_01, 16, 0)
    I_toggle1_1 = RegField(r_i_toggle1_01, 16, 16)
    I_toggle1_2 = RegField(r_i_toggle1_23, 16, 0)
    I_toggle1_3 = RegField(r_i_toggle1_23, 16, 16)
    I_toggle1_4 = RegField(r_i_toggle1_45, 16, 0)
    I_toggle1_5 = RegField(r_i_toggle1_45, 16, 16)
    I_toggle1_6 = RegField(r_i_toggle1_67, 16, 0)
    I_toggle1_7 = RegField(r_i_toggle1_67, 16, 16)
    I_toggle2_0 = RegField(r_i_toggle2_01, 16, 0)
    I_toggle2_1 = RegField(r_i_toggle2_01, 16, 16)
    I_toggle2_2 = RegField(r_i_toggle2_23, 16, 0)
    I_toggle2_3 = RegField(r_i_toggle2_23, 16, 16)
    I_toggle2_4 = RegField(r_i_toggle2_45, 16, 0)
    I_toggle2_5 = RegField(r_i_toggle2_45, 16, 16)
    I_toggle2_6 = RegField(r_i_toggle2_67, 16, 0)
    I_toggle2_7 = RegField(r_i_toggle2_67, 16, 16)
    Q_toggle1_0 = RegField(r_q_toggle1_01, 16, 0)
    Q_toggle1_1 = RegField(r_q_toggle1_01, 16, 16)
    Q_toggle1_2 = RegField(r_q_toggle1_23, 16, 0)
    Q_toggle1_3 = RegField(r_q_toggle1_23, 16, 16)
    Q_toggle1_4 = RegField(r_q_toggle1_45, 16, 0)
    Q_toggle1_5 = RegField(r_q_toggle1_45, 16, 16)
    Q_toggle1_6 = RegField(r_q_toggle1_67, 16, 0)
    Q_toggle1_7 = RegField(r_q_toggle1_67, 16, 16)
    Q_toggle2_0 = RegField(r_q_toggle2_01, 16, 0)
    Q_toggle2_1 = RegField(r_q_toggle2_01, 16, 16)
    Q_toggle2_2 = RegField(r_q_toggle2_23, 16, 0)
    Q_toggle2_3 = RegField(r_q_toggle2_23, 16, 16)
    Q_toggle2_4 = RegField(r_q_toggle2_45, 16, 0)
    Q_toggle2_5 = RegField(r_q_toggle2_45, 16, 16)
    Q_toggle2_6 = RegField(r_q_toggle2_67, 16, 0)
    Q_toggle2_7 = RegField(r_q_toggle2_67, 16, 16)

    # SPI
    spi_wdata   = RegField(r_vco_spi_wdata, 32, 0)
    inemo_spi_wdata = RegField(r_inemo_spi_wdata, 32, 0)
    inemo_spi_rdata = RegField(r_inemo_spi_rdata, 32, 0)

    # Sentinel register
    sentinel    = RegField(r_sentinel, 32, 0)
    version_id1 = RegField(r_version, 8, 24)
    version_id2 = RegField(r_version, 8, 16)
    version_num = RegField(r_version, 16, 0)
    time_stamp  = RegField(r_time_stamp, 32, 0)
    ser_num     = RegField(r_ser_num, 32, 0)

    # Return the system clock frequency
    def SysclkMHz(self):
        return 250.0 * self.GetRegField(self.sysclk_freq) / 1048575.0
    
    # Retrieve the version register, which consists of two chars and a number
    def Version(self):
        return chr(self.GetRegField(self.version_id1)) + \
            chr(self.GetRegField(self.version_id2)) + \
            str(self.GetRegField(self.version_num))

    # Return the sentinel register value
    def Sentinel(self):
        return self.GetRegField(self.sentinel)
    
    # Return the build time from the time stamp register
    def BuildTime(self):
        return datetime.datetime.fromtimestamp(self.GetRegField(self.time_stamp)).strftime('%Y-%m-%d %H:%M:%S')
        
    # Return the serial number register, which should be in the range 0-9999
    def SerialNumber(self):
        return self.GetRegField(self.ser_num)
    
    def EnableBlinky(self):
        self.SetRegField(self.disable_blinky, 0)

    def DisableBlinky(self):
        self.SetRegField(self.disable_blinky, 1)

    # Transfer data from memory to USB through the Opal Kelly pipe.
    def GetPipeData(self, bytedata):
        nbytes = self.dev.ReadFromBlockPipeOut(0xA0, self.block_size, bytedata)
        return nbytes
        
    def EnablePgen(self, val):
        self.SetRegField(self.pgen_enable, val)

    def ResetFifo(self):
        self.SetRegField(self.okf_reset, 1);
        self.SetRegField(self.okf_reset, 0);
    
    # Enable pipe transfer
    def EnablePipeTransfer(self, val):
        self.SetRegField(self.xfer_enable, val)
      
    # Set number of frames to acquire
    def SetNFrames(self, nframes):
        self.SetRegField(self.acq_lastframe, nframes-1)

    # Start an acquisition
    def StartAcq(self):
        self.SetRegField(self.acq_start, 1)
        self.SetRegField(self.acq_start, 0)
        
    # Set terminal count of timing block
    def SetTerminalCount(self, tc):
        self.SetRegField(self.term_count, tc)

    # 
    t = [Timing(0, initial_state_0, I_toggle1_0, I_toggle2_0, Q_toggle1_0, Q_toggle2_0),
         Timing(1, initial_state_1, I_toggle1_1, I_toggle2_1, Q_toggle1_1, Q_toggle2_1),
         Timing(2, initial_state_2, I_toggle1_2, I_toggle2_2, Q_toggle1_2, Q_toggle2_2),
         Timing(3, initial_state_3, I_toggle1_3, I_toggle2_3, Q_toggle1_3, Q_toggle2_3),
         Timing(4, initial_state_4, I_toggle1_4, I_toggle2_4, Q_toggle1_4, Q_toggle2_4),
         Timing(5, initial_state_5, I_toggle1_5, I_toggle2_5, Q_toggle1_5, Q_toggle2_5),
         Timing(6, initial_state_6, I_toggle1_6, I_toggle2_6, Q_toggle1_6, Q_toggle2_6)
         ]

    # Set timing values
    def SetTiming(self, signum, istate, itog1, itog2, qtog1, qtog2):
        self.SetRegField(self.t[signum].rf_istate, istate)
        self.SetRegField(self.t[signum].rf_itog1, itog1)
        self.SetRegField(self.t[signum].rf_itog2, itog2)
        self.SetRegField(self.t[signum].rf_qtog1, qtog1)
        self.SetRegField(self.t[signum].rf_qtog2, qtog2)
        
    # Choose an ADC, 0 or 1
    def SelectADC(self, val):
        self.SetRegField(self.adc_select, val)

    # Select the fake ADC input
    def SelectFakeADC(self, val):
        self.SetRegField(self.adc_usefake, val)        
        
    # Set single pixel mode
    def SinglePixelMode(self, val):
        self.SetRegField(self.single_pixel, val)
        
    # Set single pixel row and column
    def SinglePixelRowCol(self, row, col):
        self.SetRegField(self.fixed_row, row)
        self.SetRegField(self.fixed_col, col)
        
    # Load a DAC table entry
    def LoadDACEntry(self, row, col, i_or_q, val):
        addr = (row << 8) | (col << 1) | i_or_q
        self.SetRegField(self.dac_addr, addr)
        self.SetRegField(self.dac_data, val)
        self.SetRegField(self.dac_wren, 1)
        self.SetRegField(self.dac_wren, 0)
    
    # Set region of interest. Note that this is now always active, so for the
    # full display set the limits to 0 and 127
    def SetROI(self, col_min, col_max, row_min, row_max):
        self.SetRegField(self.roi_start_col, col_min)
        self.SetRegField(self.roi_end_col, col_max)
        self.SetRegField(self.roi_start_row, row_min)
        self.SetRegField(self.roi_end_row, row_max)

    # Set number of ADC samples to average
    def SetNAvg(self, navg):
        self.SetRegField(self.acq_navg, navg)

    # Set flag to ignore the first ADC sample
    def SetIgnoreFirstSample(self, one_if_true):
        self.SetRegField(self.ignore_first, one_if_true)

    # Set the listening offsets. These are 8-bit signed values.
    def SetListeningOffsets(self, col_off, row_off):
        self.SetRegField(self.listen_col_off, col_off)
        self.SetRegField(self.listen_row_off, row_off)

    # A VCO SPI command -- write only
    def VCOWrite(self, wdata):
        self.SetRegField(self.spi_wdata, wdata);
        self.SetRegField(self.vco_spi_go, 1);

    # An iNEMO SPI command; here there are read commands and write commands.
    def iNemoWrite(self, regaddr, regdata):
        # A write has bit 15 = 0
        wdata = ((regaddr << 8) | regdata) & 0x0007FFF
        self.SetRegField(self.inemo_spi_wdata, wdata)
        self.SetRegField(self.inemo_spi_go, 1)
    def iNemoRead(self, regaddr):
        wdata = ((regaddr << 8) & 0x7FFF) | 0x0008000
        self.SetRegField(self.inemo_spi_wdata, wdata)
        self.SetRegField(self.inemo_spi_go, 1)
        rdata = self.GetRegister(self.r_inemo_spi_rdata)
        return (rdata & 0x000000FF)

    def EnableVCOOutput(self, one_if_true):
        self.SetRegField(self.pdbrf, one_if_true)

    # 1x16 TX column mask - selects transmitting pixels
    def TxColMask_1x16(self, mask):
        self.SetRegField(self.init_tx_colmask_1x16, mask)

    # 1x16 RX pixel number -- colnum is 0-15
    def RxColNum_1x16(self, colnum):
        self.SetRegField(self.init_rx_colnum_1x16, colnum)

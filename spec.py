# spec.py
"""Constants for SSTV specification and each supported mode"""

from enum import Enum


class COL_FMT(Enum):
    RGB = 1
    GBR = 2
    YUV = 3
    BW = 4


class M1(object):
    NAME = "Martin M1"

    COLOR = COL_FMT.GBR
    LINE_WIDTH = 320
    LINE_COUNT = 256
    SCAN_TIME = 0.146432
    SYNC_PULSE = 0.004862
    SYNC_PORCH = 0.000572
    SEP_PULSE = 0.000572

    CHAN_COUNT = 3
    CHAN_SYNC = 0
    CHAN_TIME = SEP_PULSE + SCAN_TIME

    CHAN_OFFSETS = [
        SYNC_PULSE + SYNC_PORCH,
        SYNC_PULSE + SYNC_PORCH + CHAN_TIME,
        SYNC_PULSE + SYNC_PORCH + 2 * CHAN_TIME
    ]

    LINE_TIME = SYNC_PULSE + SYNC_PORCH + 3 * CHAN_TIME
    PIXEL_TIME = SCAN_TIME / LINE_WIDTH
    WINDOW_FACTOR = 2.34

    HAS_START_SYNC = False
    HAS_HALF_SCAN = False
    HAS_ALT_SCAN = False


class M2(M1):
    NAME = "Martin M2"

    LINE_WIDTH = 320
    SCAN_TIME = 0.073216
    SYNC_PULSE = 0.004862
    SYNC_PORCH = 0.000572
    SEP_PULSE = 0.000572

    CHAN_TIME = SEP_PULSE + SCAN_TIME

    CHAN_OFFSETS = [
        SYNC_PULSE + SYNC_PORCH,
        SYNC_PULSE + SYNC_PORCH + CHAN_TIME,
        SYNC_PULSE + SYNC_PORCH + 2 * CHAN_TIME
    ]

    LINE_TIME = SYNC_PULSE + SYNC_PORCH + 3 * CHAN_TIME
    PIXEL_TIME = SCAN_TIME / LINE_WIDTH
    WINDOW_FACTOR = 4.68


class S1(object):
    NAME = "Scottie S1"

    COLOR = COL_FMT.GBR
    LINE_WIDTH = 320
    LINE_COUNT = 256
    SCAN_TIME = 0.138240
    SYNC_PULSE = 0.009000
    SYNC_PORCH = 0.001500
    SEP_PULSE = 0.001500

    CHAN_COUNT = 3
    CHAN_SYNC = 2
    CHAN_TIME = SEP_PULSE + SCAN_TIME

    CHAN_OFFSETS = [
        SYNC_PULSE + SYNC_PORCH + CHAN_TIME,
        SYNC_PULSE + SYNC_PORCH + 2 * CHAN_TIME,
        SYNC_PULSE + SYNC_PORCH
    ]

    LINE_TIME = SYNC_PULSE + 3 * CHAN_TIME
    PIXEL_TIME = SCAN_TIME / LINE_WIDTH
    WINDOW_FACTOR = 2.48

    HAS_START_SYNC = True
    HAS_HALF_SCAN = False
    HAS_ALT_SCAN = False


class S2(S1):
    NAME = "Scottie S2"

    LINE_WIDTH = 320
    SCAN_TIME = 0.088064
    SYNC_PULSE = 0.009000
    SYNC_PORCH = 0.001500
    SEP_PULSE = 0.001500

    CHAN_TIME = SEP_PULSE + SCAN_TIME

    CHAN_OFFSETS = [
        SYNC_PULSE + SYNC_PORCH + CHAN_TIME,
        SYNC_PULSE + SYNC_PORCH + 2 * CHAN_TIME,
        SYNC_PULSE + SYNC_PORCH
    ]

    LINE_TIME = SYNC_PULSE + 3 * CHAN_TIME
    PIXEL_TIME = SCAN_TIME / LINE_WIDTH
    WINDOW_FACTOR = 3.82


class SDX(S2):
    NAME = "Scottie DX"

    LINE_WIDTH = 320
    SCAN_TIME = 0.345600
    SYNC_PULSE = 0.009000
    SYNC_PORCH = 0.001500
    SEP_PULSE = 0.001500

    CHAN_TIME = SEP_PULSE + SCAN_TIME

    CHAN_OFFSETS = [
        SYNC_PULSE + SYNC_PORCH + CHAN_TIME,
        SYNC_PULSE + SYNC_PORCH + 2 * CHAN_TIME,
        SYNC_PULSE + SYNC_PORCH
    ]

    LINE_TIME = SYNC_PULSE + 3 * CHAN_TIME
    PIXEL_TIME = SCAN_TIME / LINE_WIDTH
    WINDOW_FACTOR = 0.98


class R36(object):
    NAME = "Robot 36"

    COLOR = COL_FMT.YUV
    LINE_WIDTH = 320
    LINE_COUNT = 240
    SCAN_TIME = 0.088000
    HALF_SCAN_TIME = 0.044000
    SYNC_PULSE = 0.009000
    SYNC_PORCH = 0.003000
    SEP_PULSE = 0.004500
    SEP_PORCH = 0.001500

    CHAN_COUNT = 2
    CHAN_SYNC = 0
    CHAN_TIME = SEP_PULSE + SCAN_TIME

    CHAN_OFFSETS = [
        SYNC_PULSE + SYNC_PORCH,
        SYNC_PULSE + SYNC_PORCH + CHAN_TIME + SEP_PORCH
    ]

    LINE_TIME = CHAN_OFFSETS[1] + HALF_SCAN_TIME
    PIXEL_TIME = SCAN_TIME / LINE_WIDTH
    HALF_PIXEL_TIME = HALF_SCAN_TIME / LINE_WIDTH
    WINDOW_FACTOR = 7.70

    HAS_START_SYNC = False
    HAS_HALF_SCAN = True
    HAS_ALT_SCAN = True


class R72(R36):
    NAME = "Robot 72"

    LINE_WIDTH = 320
    SCAN_TIME = 0.138000
    HALF_SCAN_TIME = 0.069000
    SYNC_PULSE = 0.009000
    SYNC_PORCH = 0.003000
    SEP_PULSE = 0.004500
    SEP_PORCH = 0.001500

    CHAN_COUNT = 3
    CHAN_TIME = SEP_PULSE + SCAN_TIME
    HALF_CHAN_TIME = SEP_PULSE + HALF_SCAN_TIME

    CHAN_OFFSETS = [
        SYNC_PULSE + SYNC_PORCH + CHAN_TIME,
        SYNC_PULSE + SYNC_PORCH + 2 * CHAN_TIME,
        SYNC_PULSE + SYNC_PORCH + HALF_CHAN_TIME + SEP_PORCH
    ]

    LINE_TIME = CHAN_OFFSETS[2] + HALF_SCAN_TIME
    PIXEL_TIME = SCAN_TIME / LINE_WIDTH
    HALF_PIXEL_TIME = HALF_SCAN_TIME / LINE_WIDTH
    WINDOW_FACTOR = 4.88

    HAS_ALT_SCAN = False


# Mapping VIS values to mode classes
VIS_MAP = {
    8: R36,
    12: R72,
    40: M2,
    44: M1,
    56: S2,
    60: S1,
    76: SDX
}

# Header offsets and sizes
BREAK_OFFSET = 0.300
LEADER_OFFSET = 0.010 + BREAK_OFFSET
VIS_START_OFFSET = 0.300 + LEADER_OFFSET

HDR_SIZE = 0.030 + VIS_START_OFFSET
HDR_WINDOW_SIZE = 0.010

VIS_BIT_SIZE = 0.030

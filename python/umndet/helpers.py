"""
Helper functions for reading in binary data files
into structured data.

Each defined type of data file is read using the
function corresponding to it, which wraps
part of generic_read_binary or read_binary,
depending on the data structure in the binary data.
"""

import ctypes
import struct
from collections.abc import Callable
from typing import IO, Any

from . import data_structs as ds


def generic_read_binary(
    fn: str, open_func: Callable, function_body: Callable[[IO[bytes]], Any]
) -> list[Any]:
    ret = []
    with open_func(fn, "rb") as f:
        while True:
            try:
                new_data = function_body(f)
            except struct.error:
                break
            if not new_data:
                break
            ret.append(new_data)
    return ret


def read_binary(fn: str, type_: type, open_func: Callable) -> list:
    sz = ctypes.sizeof(type_)

    def read_elt(f: IO[bytes]):
        d = type_()
        eof = f.readinto(d) != sz
        if eof:
            return None
        return d

    return generic_read_binary(fn, open_func, read_elt)


def read_det_health(fn: str, open_func: Callable) -> list[ds.DetectorHealth]:
    return read_binary(fn, ds.DetectorHealth, open_func)


def read_hafx_sci(fn: str, open_func: Callable) -> list[ds.NominalHafx]:
    return read_binary(fn, ds.NominalHafx, open_func)


def read_x123_sci(fn: str, open_func: Callable) -> list[ds.X123NominalSpectrumStatus]:
    def read_elt(f: IO[bytes]):
        (timestamp,) = struct.unpack("<L", f.read(4))
        status_bytes = f.read(64)
        (spectrum_size,) = struct.unpack("<H", f.read(2))
        spectrum = list(
            struct.unpack("<" + ("L" * spectrum_size), f.read(4 * spectrum_size))
        )
        return ds.X123NominalSpectrumStatus(timestamp, spectrum, status_bytes)

    return generic_read_binary(fn, open_func, read_elt)


def read_x123_debug(fn: str, open_func: Callable) -> list[ds.X123Debug]:
    def read_elt(f: IO[bytes]):
        (debug_type,) = struct.unpack("<B", f.read(1))
        (size,) = struct.unpack("<L", f.read(4))
        data = f.read(size)
        return ds.X123Debug(debug_type, data)

    return generic_read_binary(fn, open_func, read_elt)


def read_hafx_debug(fn: str, open_func: Callable) -> list[ds.HafxDebug]:
    def read_elt(f: IO[bytes]):
        (type_,) = struct.unpack("<B", f.read(1))
        name, packing = ds.HafxDebug.TYPE_DECODE_MAP[type_]
        try:
            sz = struct.calcsize(packing)
        except TypeError:
            # we got a type which needs to be handled separately
            if name == "nrl_list_full_size":
                (num_evts,) = struct.unpack("<H", f.read(2))
                # seek backwards to put num_events back
                # in the byte stream
                # whence=1 means "from current position"
                f.seek(-2, 1)
                # num evts is 2B
                # each event is 12B
                # and then we put the timestamp, another 4B
                sz = 2 + (num_evts * 12) + 4

        bytes_ = f.read(sz)
        return ds.HafxDebug(type_, bytes_)

    return generic_read_binary(fn, open_func, read_elt)


def read_nrl_list(fn: str, open_func: Callable) -> list:
    """
    Read a file full of stripped NRL list mode data
    into a bunch of dictionards.

    The dicts contain the list-mode events with 25-bit relative time,
    4-bit energy, and some flags.

    The timestamp associated with the data is immediately after reading
    it out, so the most recent PPS in the event stream corresponds
    to when that second "ticked."
    """

    def read_element(f: IO[bytes]):
        (num_events,) = struct.unpack("<H", f.read(2))
        evts = []
        for _ in range(num_events):
            d = ds.FullSizeNrlDataPoint()
            f.readinto(d)
            evts.append(d)
        (timestamp,) = struct.unpack("<L", f.read(4))
        return {"unix_time": timestamp, "events": evts}

    return generic_read_binary(fn, open_func, read_element)
import datetime

import matplotlib.pyplot as plt
import numpy as np

from . import data_structs as ies


def plot_raw_time_slice_spectrogram(
    data: list[ies.NominalImpress], adc_bins: list[int], fig=None, ax=None
):
    counts_spectrogram = np.array([hd.histogram for hd in data])

    # Construct the timestamps from the given data points
    def from_timestamp(ts):
        return datetime.datetime.fromtimestamp(ts, tz=datetime.UTC)

    # recent = from_timestamp(data[0].time_anchor)
    times: list[datetime.datetime] = []
    for d in data:
        dtime = from_timestamp(d.unix_second)
        dtime += datetime.timedelta(seconds=(d.buffer_number % 32) / 32)
        times.append(dtime)

    # "time bins" are 1 larger than the # of histograms we get
    times.append(times[-1] + datetime.timedelta(seconds=1 / 32))

    fig = fig or plt.gcf()
    ax = ax or plt.gca()

    # Bridgeport natively maps to 124 customizable bins;
    # c.f. IMPRESS firwmare spec on Google Drive
    bins = np.arange(124)
    pcm = ax.pcolormesh(np.array(times), bins, counts_spectrogram.T, cmap="plasma")
    ax.set(
        xlabel="Time (UTC)",
        ylabel="Normal Bridgeport ADC bin",
        title="Counts spectrogram",
    )

    return fig, ax, pcm

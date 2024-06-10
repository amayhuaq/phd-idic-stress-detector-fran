import pandas as pd
from StressDetector import StressDetector

import matplotlib.pyplot as plt
import numpy as np


def show_signals(eda_signal, stress_levels):
    x = [i for i in range(len(eda_signal))]

    plt.plot(x, eda_signal)
    plt.plot(x, stress_levels)

    plt.show()


def process_from_csv(filename, show_graph=False):
    WIN_SIZE = 3 # 720  # 3 mins x 4 samples x 60 seconds
    detector = StressDetector(3, 1)
    df_data = pd.read_csv(filename, header=None)
    eda_data_raw = df_data[0].tolist()
    last_val = len(eda_data_raw) // WIN_SIZE
    eda_data = eda_data_raw[0:(last_val * WIN_SIZE)]

    detector.process_gsr(eda_data)
    stress_levels = detector.get_sax_values()
    stress_levels = np.repeat(stress_levels, WIN_SIZE)

    df = pd.DataFrame(stress_levels)
    df.to_csv("stress_levels.csv", header=None, index=None)

    if show_graph:
        show_signals(eda_data, stress_levels)


if __name__ == '__main__':
    #process_from_csv("EDA_raw.csv", True)
    process_from_csv("embrace.csv", True)

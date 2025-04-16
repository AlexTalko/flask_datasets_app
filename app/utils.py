import numpy as np
from scipy.signal import find_peaks


def count_special_peaks(angle_data):
    """Анализирует массив углов, подсчитывая пики, превышающие последний минимум на 20, с использованием SciPy"""
    angle_array = np.array(angle_data)
    peaks, _ = find_peaks(angle_array)
    minima, _ = find_peaks(-angle_array)
    critical_points = sorted([(idx, 'max' if idx in peaks else 'min') for idx in np.concatenate([peaks, minima])])
    count = 0
    last_min_value = None
    for idx, typ in critical_points:
        if typ == 'min':
            last_min_value = angle_array[idx]
        elif typ == 'max' and last_min_value is not None:
            if angle_array[idx] > last_min_value + 20:
                count += 1
    return count

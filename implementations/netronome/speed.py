#!/usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import glob


def process_data(df):
    # Convert packet length from bytes to bits
    df['length'] *= 8

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(float), unit='s')

    # Calculate elapsed time in seconds from the start of the capture
    start_time = df['timestamp'].min()
    df['elapsed'] = (df['timestamp'] - start_time).dt.total_seconds()

    # Round to nearest second for aggregation
    df['elapsed_rounded'] = df['elapsed'].round()

    # Group by the rounded elapsed time and sum lengths
    throughput = df.groupby('elapsed_rounded')['length'].sum()

    # Convert bits to gigabits
    throughput /= 1e9

    return throughput

def plot_throughput(df1, df2):
    throughput1 = process_data(df1)
    throughput2 = process_data(df2)

    plt.figure(figsize=(10, 6))
    #plt.grid(True, zorder=0, linewidth=0.5, alpha=0.5)
    plt.plot(throughput1.index, throughput1, 'blue', label='Single service', linewidth=2, alpha=0.7)
    plt.plot(throughput2.index, throughput2, 'red', label='Multiple services', linewidth=2, alpha=0.7)
    plt.xlabel('Time Elapsed (s)', fontsize=20)
    plt.ylabel('Throughput (Gbps)', fontsize=20)
    plt.ylim(9.4, 9.5)
    plt.xlim(0, 15)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.legend(fontsize=18)
    plt.tight_layout()
    #plt.savefig('../dissertation/images/figures/combined_throughput.pgf', bbox_inches='tight', dpi=300)
    plt.show()

def plot_packet_rate(df2):
    #df1['timestamp'] = pd.to_datetime(df1['timestamp'].astype(float), unit='s')
    df2['timestamp'] = pd.to_datetime(df2['timestamp'].astype(float), unit='s')

    #start_time1 = df1['timestamp'].min()
    start_time2 = df2['timestamp'].min()

    #df1['elapsed'] = (df1['timestamp'] - start_time1).dt.total_seconds()
    df2['elapsed'] = (df2['timestamp'] - start_time2).dt.total_seconds()

    #df1['elapsed_rounded'] = df1['elapsed'].round()
    df2['elapsed_rounded'] = df2['elapsed'].round()

    #packet_rate1 = df1.groupby('elapsed_rounded').size()
    packet_rate2 = df2.groupby('elapsed_rounded').size()
    packet_rate2 = packet_rate2.iloc[1:-1]

    plt.figure(figsize=(10, 6))
    #plt.grid(True, zorder=0, linewidth=0.5, alpha=0.5)
    #plt.plot(packet_rate1.index, packet_rate1, 'green', label='Dataset 1', linewidth=2, marker='o', markersize=4, alpha=0.7)
    plt.plot(packet_rate2.index, packet_rate2, 'red')
    print(sum(packet_rate2)/len(packet_rate2))
    #plt.plot(packet_rate2.index, packet_rate2, 'blue', label='Dataset 2', linewidth=2, marker='x', markersize=4, alpha=0.7)
    plt.xlabel('Time Elapsed (s)', fontsize=20)
    plt.ylabel('Packets per Second', fontsize=20)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    #plt.legend()
    plt.tight_layout()
    #plt.savefig('../dissertation/images/figures/pps.pgf', bbox_inches='tight', dpi=300)
    plt.show()

def convert_to_gbps(bitrate_str):
    """
    Convert a bitrate string to Gbits/sec.
    
    Parameters:
    bitrate_str (str): Bitrate string with units.
    
    Returns:
    float: Bitrate in Gbits/sec.
    """
    value, unit = bitrate_str.split()
    value = float(value)
    
    if unit == 'Gbits/sec':
        return value
    elif unit == 'Mbits/sec':
        return value / 1000
    elif unit == 'Kbits/sec':
        return value / (1000 * 1000)
    elif unit == 'bits/sec':
        return value / (1000 * 1000 * 1000)
    else:
        raise ValueError(f"Unknown unit: {unit}")

def normalize_whitespace(line):
    """
    Normalize whitespace in a line so that there is only one space between fields.
    
    Parameters:
    line (str): The line to normalize.
    
    Returns:
    str: The normalized line.
    """
    return re.sub(r'\s+', ' ', line.strip())

def sum_bitrates_per_interval(file_list, unit='Gbps'):
    """
    Calculate the sum of bitrates per interval from a list of files.

    Parameters:
    file_list (list of str): List of file paths to process.
    unit (str): Desired unit for the resulting bitrate values ('Gbps' or 'Mbps').

    Returns:
    list of float: List where each element is the sum of bitrates for a specific interval in the desired unit.
    """
    # Dictionary to store sum of bitrates for each interval
    interval_sums = {}

    # Regex to match bitrate values
    bitrate_pattern = re.compile(r'\d+(\.\d+)? (Gbits/sec|Mbits/sec|Kbits/sec|bits/sec)')
    
    # Process each file
    for file in file_list:
        try:
            with open(file, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"File not found: {file}")
            continue

        # Extract bitrates and intervals
        for line in lines:
            normalized_line = normalize_whitespace(line)
            match = bitrate_pattern.search(normalized_line)
            if match:
                bitrate_str = match.group()
                bitrate = convert_to_gbps(bitrate_str)
                # Get the interval line
                interval_line = normalized_line.split(' sec')[0]
                interval = interval_line.split()[-1]
                if interval not in interval_sums:
                    interval_sums[interval] = 0.0
                interval_sums[interval] += bitrate

    # Sort intervals and prepare result list
    intervals = sorted(interval_sums.keys(), key=lambda x: float(x.split('-')[0]))
    result = [interval_sums[interval] for interval in intervals]

    return result

def new_throughput(throughput_list1, throughput_list2):
    """
    Plot throughput for multiple services and single service.

    Parameters:
    throughput_list1 (list of float): Throughput values for multiple services in Gbps.
    throughput_list2 (list of float): Throughput values for single service in Gbps.
    """
    time_elapsed = list(range(len(throughput_list1)))
    print(f"Average throughput for multiple services: {sum(throughput_list1) / len(throughput_list1)} Gbps")
    print(f"Average throughput for single service: {sum(throughput_list2) / len(throughput_list2)} Gbps")
    
    plt.figure(figsize=(10, 6))
    plt.plot(time_elapsed, throughput_list2, 'blue', label=f'Single service; {round(sum(throughput_list2) / len(throughput_list2),4)}', linewidth=2, alpha=0.7)
    plt.plot(time_elapsed, throughput_list1, 'red', label=f'Multiple services; {round(sum(throughput_list1) / len(throughput_list1),4)}', linewidth=2, alpha=0.7)
    plt.xlabel('Time Elapsed (s)', fontsize=24)
    plt.ylabel('Throughput (Gbps)', fontsize=24)
    #plt.ylim(0, max(max(throughput_list1), max(throughput_list2)) * 1.1)
    print(max(throughput_list1))
    fname = ''
    if max(throughput_list1) > 9:
        plt.ylim(8.4,10.1)
        plt.legend(fontsize=22, title = f"          Service; Average (Gbps)", title_fontsize=20, loc='lower right')
        fname = '../dissertation/images/figures/combined_throughput_netronome.pgf'
        plt.yticks(np.arange(8.4, 10.1, 0.2), fontsize=22)
    else: 
        plt.ylim(0,0.53)
        plt.legend(fontsize=22, title = f"          Service; Average (Gbps)", title_fontsize=20)
        fname = '../dissertation/images/figures/combined_throughput_bmv2.pgf'
        plt.yticks(np.arange(min(throughput_list2), 0.53, 0.05), fontsize=22)

    plt.xticks(fontsize=22)
    plt.tight_layout()
    #plt.show()
    plt.savefig(fname, bbox_inches='tight', dpi=300)

# Example usage:
file_list_0 = [
    "multi_throughput_1.txt",
    "multi_throughput_2.txt",
    "multi_throughput_3.txt",
    "multi_throughput_4.txt"
]

file_list_1 = ["single_throughput.txt"]
# Call the function and print the result
summed_bitrates_0 = sum_bitrates_per_interval(file_list_0, unit='Gbps')
summed_bitrates_1 = sum_bitrates_per_interval(file_list_1, unit='Gbps')
print(len(summed_bitrates_0), len(summed_bitrates_1))
new_throughput(summed_bitrates_0, summed_bitrates_1)

# Example usage:
file_list = [
    "multi_throughput_bmv2_1.txt",
    "multi_throughput_bmv2_2.txt",
    "multi_throughput_bmv2_3.txt",
    "multi_throughput_bmv2_4.txt"
]

file_list_2 = ["single_throughput_bmv2.txt"]
# Call the function and print the result
summed_bitrates_2 = sum_bitrates_per_interval(file_list, unit='Gbps')
summed_bitrates_3 = sum_bitrates_per_interval(file_list_2, unit='Gbps')
print(len(summed_bitrates_2), len(summed_bitrates_3))
new_throughput(summed_bitrates_2, summed_bitrates_3)

# Load the datasets
df_single = pd.read_csv('single.csv', header=None, names=['timestamp', 'length'], delimiter='\t')
df_multi = pd.read_csv('multi.csv', header=None, names=['timestamp', 'length'], delimiter='\t')
df_multi_120 = pd.read_csv('multi_120.csv', header=None, names=['timestamp', 'length'], delimiter='\t')

# Plot throughput and packet rate for both datasets
#plot_throughput(df_single, df_multi)
#plot_packet_rate(df_multi_120)
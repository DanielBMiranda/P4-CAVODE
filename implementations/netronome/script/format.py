#!/usr/bin/env python3

import argparse, re, csv, math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
import sys
from matplotlib.pyplot import figure
from collections import Counter
from matplotlib.gridspec import GridSpec



maxi = 0

def hex_to_decimal(hex_str):
    return int(hex_str, 16)

def format_file(input_filename, output_filename):
    with open(input_filename, 'r') as input_file:
        content = input_file.read()

    matches = re.findall(r'digest _digest_notification_digest_t_1 .*?\{(.*?)\}', content, re.DOTALL)

    data = []
    for match in matches:
        entries = re.findall(r'scalars\.(.*?) : (0x[0-9a-fA-F]+)', match)
        entry_dict = {key.strip(): hex_to_decimal(value) for key, value in entries}

        # Additional conversions
        entry_dict['tmp_10'] /= 1e9
        entry_dict['tmp_9'] += entry_dict['tmp_10']
        entry_dict['tmp_7'] /= 100
        entry_dict['tmp_8'] /= 100
        del entry_dict['tmp_10']
        data.append(entry_dict)
    
    fieldnames = data[0].keys() if data else []
    with open(output_filename, 'w', newline='') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writerows(data)

def process_differences(ax, input_filename, delay_val, col):
    try:
        with open(input_filename, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header if present
            data = list(reader)

        values = [float(row[0]) for row in data]
        differences = [values[i + 1] - values[i] for i in range(len(values) - 1)]

        global maxi
        if maxi < max(differences[1:]):
            maxi = max(differences[1:])

        ref_values = [int(delay_val)] * len(differences)

        ax.scatter(differences[1:], ref_values[1:], s=50, c=col, edgecolor='none', alpha=0.6)
    except Exception as e:
        print(f"Error processing differences for file {input_filename}: {e}")

def dispersion(sizes, test_type, delays, colors):
    max_cols = 3  # Maximum number of subplots per row
    num_sizes = len(sizes)
    num_rows = math.ceil(num_sizes / max_cols)
    num_cols = min(max_cols, num_sizes)

    fig = plt.figure(figsize=(4 * max_cols, 4 * num_rows + 1))  # Adjusting height for legend space

    # Custom column width ratios for 6 columns
    widths = [1, 1, 1, 1, 1, 1]
    gs = GridSpec(num_rows, 6, figure=fig, width_ratios=widths)
    legend_entries = []

    for idx, size in enumerate(sizes):
        row = idx // max_cols
        col = idx % max_cols

        if row == 1:
            start_col = int(col * 3)  # Ensure correct spacing for 1.5 columns each
            ax = fig.add_subplot(gs[row, start_col:start_col + 3])  # Each subplot in the second row spans 1.5 columns
        else:
            ax = fig.add_subplot(gs[row, col*2:col*2+2])

        for delay, color in zip(delays, colors):
            ax.axhline(y=int(delay), color='gray', linestyle='--', linewidth=0.5)
            if len(legend_entries) < 3:
                legend_entries.append(Line2D([0], [0], marker='o', color='w', markersize=8, markerfacecolor=color, label=f"{delay}s"))
            file_path = f'results/{size}/{delay}/alarms.'
            format_file(file_path + 'txt', file_path + 'csv')
            process_differences(ax, file_path + 'csv', delay, color)

        ax.plot([0,maxi],[0,maxi], 'k-')
        ax.set_ylim(0, 32)
        ax.set_xlim(-2, 63.5)
        ax.set_xlabel("Time passed (s)", fontsize=16, labelpad=10)  # Adjust labelpad as needed
        if col == 0:
            ax.set_ylabel('Time expected (s)', fontsize=16)  # Adjust labelpad as needed
        ax.set_title(f'Cyclic buffer size - {size}', fontsize=14)
        ax.tick_params(axis='x', labelsize=14) 
        ax.tick_params(axis='y', labelsize=14)

    #fig.text(0.04, 0.5, 'Time expected (s)', va='center', ha='center', rotation='vertical', fontsize=16)
    #fig.text(0.5, 0.015, 'Time passed (s)', va='center', ha='center', rotation='horizontal', fontsize=16)

    legend = fig.legend(handles=legend_entries, loc='upper center', title='Probe delays', ncol=3, fontsize=14)
    legend.get_title().set_fontsize(14)
    plt.subplots_adjust(top=0.88, bottom=0.08, left=0.08, right=0.975, wspace=0.4, hspace=0.38)  # Adjusting space to make room for legend
    #plt.savefig('../dissertation/images/figures/dispersion.pgf', bbox_inches='tight', dpi=300)
    plt.show()

def diffs_graph(size, test_type, delay):
    file_path = f'results/{size}/sporadic/{delay}/alarms.'

    format_file(file_path + 'txt', file_path + 'csv')

    with open(file_path + 'csv', 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
    
    values = [float(row[0]) for row in data]

    differences = [values[i + 1] - values[i] for i in range(len(values) - 1)][1:]

    plt.plot(range(1, len(differences) + 1), differences, marker='o')
    plt.xlabel('Alarm index')
    plt.ylabel('Delta between alarms')
    plt.title(f'Cyclic buffer size - {size}\nDelay - {delay}')
    plt.show()


def new_diffs_graph(size, test_type, delay):
    file_path = f'results/{size}/sporadic/{delay}/alarms.'

    format_file(file_path + 'txt', file_path + 'csv')

    with open(file_path + 'csv', 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
    
    values = [float(row[0]) for row in data]

    differences = [values[i + 1] - values[i] for i in range(len(values) - 1)][1:]

    # Assuming 'differences' is your dataset

    # Define the start, end, and width of your bins
    bin_start = 0  # Adjust if you expect values lower than 0
    bin_end = max(differences) + 2  # Extend beyond the max value to include all data
    bin_width = 2  # Interval width

    # Create bins based on the defined start, end, and width
    bins = np.arange(bin_start, bin_end, bin_width)

    plt.figure(figsize=(10, 4))
    #plt.grid(True, zorder=0, linewidth=0.5, alpha=0.5)
    # Plot the histogram
    n, bins, patches = plt.hist(differences, bins=bins, color='lightskyblue', zorder=2, linewidth=0.2, edgecolor='black')

    #plt.title('Distribution of Time Differences Between Triggers')
    plt.xlabel('Time difference interval (s)', fontsize=16)
    plt.ylabel('Number of ocurrences\n(symmetrical log scale)', fontsize=16)
    plt.ylim(0, 8000)
    # Applying a logarithmic scale to make low-frequency bins more noticeable
    plt.yscale('symlog')
    plt.tick_params(axis='x', labelsize=14) 
    plt.tick_params(axis='y', labelsize=14)

    mean_diff = np.mean(differences)
    ref = plt.axvline(mean_diff, color='r', linestyle='dashed', linewidth=2, label='Average time\ndifference value')
    plt.text(mean_diff + 3.7, plt.ylim()[1] * 0.35, f'{mean_diff:.2f}', color='r', fontsize=16)
    
    plt.tight_layout()

    print("\nStatistics per Bin:")
    tick_positions = []
    for i in range(len(bins) - 1):
        bin_mask = (differences >= bins[i]) & (differences < bins[i + 1])
        bin_values = np.array(differences)[bin_mask]
        if bin_values.size > 0:
            bin_mean = np.mean(bin_values)
            bin_std = np.std(bin_values)
            bin_max = np.max(bin_values)
            bin_min = np.min(bin_values)
            print(f"Bin {bins[i]} to {bins[i+1]} - Mean: {bin_mean:.5f}, Frequency: {int(n[i])} , Std Dev: {bin_std:.5f}, Max: {bin_max:.5f}, Min: {bin_min:.5f}")
            if n[i] > 1:
                tick_positions.extend([bins[i], bins[i + 1]])
    
    tick_positions = sorted(set(tick_positions))
    #plt.xticks(tick_positions, fontsize=14)
    current_ticks = plt.xticks()[0]  # Retrieve the current tick positions
    updated_ticks = np.append(current_ticks, 20)  # Add 20 to the tick positions
    plt.xticks(updated_ticks, fontsize=14)
    plt.xlim(-15.10,320)
    plt.legend(handles=[ref], fontsize=14)
    
    #plt.savefig('../dissertation/images/figures/freq_10000_sporadic.pgf', bbox_inches='tight', dpi=300)
    plt.show()

def full_value_graph():
    data = {
        10: {
            550: {4: 1136, 5: 32},
            10000: {4: 1018, 5: 32}
        },
        20: {
            550: {4: 1230, 5: 33},
            10000: {4: 1050, 5: 32}
        },
        30: {
            550: {4: 1328, 5: 32},
            10000: {4: 1083, 5: 32}
        }
    }

    colors = {
        550: 'orange',
        10000: 'lightskyblue'
    }

    fig, axs = plt.subplots(1, 3, figsize=(12, 7), sharey=True)
    delays = [10, 20, 30]
    bar_width = 0.3  # Adjusted width of each bar to create more space
    num_bars = len(colors)  # Number of bars at each x position

    for i, delay in enumerate(delays):
        x_values = sorted(set().union(*[data[delay][size].keys() for size in data[delay].keys()]))
        x_indices = np.arange(len(x_values))

        for j, size in enumerate(sorted(colors.keys())):
            offsets = x_indices + (j - num_bars / 2) * bar_width + bar_width / 2  # Calculate bar positions
            heights = [data[delay][size].get(x, 0) for x in x_values]

            bars = axs[i].bar(offsets, heights, bar_width, color=colors[size], label=f'{size}', edgecolor='black', zorder=3)
            
            # Adding text annotations on top of each bar
            for rect in bars:
                height = rect.get_height()
                if height == 990:
                    axs[i].annotate(f'{height}',
                                    xy=(rect.get_x() + rect.get_width() / 2, height),
                                    xytext=(0, -5),  # 12 points vertical offset downwards
                                    textcoords="offset points",
                                    ha='center', va='top', fontsize=13, color='black', zorder=5)
                else:
                    axs[i].annotate(f'{height}',
                                    xy=(rect.get_x() + rect.get_width() / 2, height),
                                    xytext=(0, 2),  # 3 points vertical offset upwards
                                    textcoords="offset points",
                                    ha='center', va='bottom', fontsize=13, color='black', zorder=5)

        axs[i].set_title(f'Probe delay: {delay}s', fontsize=14)
        axs[i].set_yscale('symlog')
        axs[i].set_xticks(x_indices)
        axs[i].set_xticklabels(x_values)
        axs[i].set_xlim(min(x_indices) - 0.5, max(x_indices) + 0.5)  # Adding gap on both sides
        axs[i].set_ylim(0, 3000)
        axs[i].set_xlabel("Distinct counter value", fontsize=16, labelpad=10)
        axs[i].tick_params(axis='x', labelsize=14)
        axs[i].tick_params(axis='y', labelsize=14)

    fig.text(0.04, 0.5, 'Number of occurrences\n(symmetrical log scale)', va='center', ha='center', rotation='vertical', fontsize=16)

    # Create a custom legend
    handles = [plt.Line2D([0], [0], color=colors[size], lw=4) for size in sorted(colors.keys())]
    labels = [str(size) for size in sorted(colors.keys())]
    legend = fig.legend(handles, labels, title='Cyclic buffer sizes', loc='upper center', ncol=len(labels), fontsize=14)
    legend.get_title().set_fontsize(14)
    
    plt.tight_layout(pad=2.0)
    plt.subplots_adjust(top=0.84, left=0.1, right=0.975, wspace=0.15)  # Adjusting the subplot spacing
    #plt.savefig('../dissertation/images/figures/count_all_sporadic.pgf', bbox_inches='tight', dpi=300)
    plt.show()


def value_frequency_graph():
    delay_list = [10, 20, 30]
    # Custom RGB colors for better visibility
    colors = [
        'lightcoral',  # Lighter Red
        'mediumspringgreen',  # Lighter Green
        (1, 1, 0.5),    # Lighter Yellow
        'orange',
        'lightskyblue',   # Lighter Blue
    ]

    # Set up the figure for plotting
    fig, axs = plt.subplots(1, len(delay_list), figsize=(12, 5), sharey=True)  # Reduced width

    if len(delay_list) == 1:
        axs = [axs]

    all_values = set()
    for i, delay in enumerate(delay_list):
        for index, size in enumerate(sizes):
            file_path = f'results/{size}/{delay}/alarms.csv'
            
            # Load data from the csv file
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                data = list(reader)
            
            # Extract the second column from each row
            values = [int(row[1]) for row in data]
            all_values.update(values)
            
            # Count frequencies of each distinct value
            #frequency_dict = Counter(values)
            #sorted_counter = {k: frequency_dict[k] for k in sorted(frequency_dict, key=frequency_dict.get)}
            #print(delay, size, sorted_counter)
            
            # Define the start, end, and width of your bins
            bin_width = 0.5  # Increased bin width
            bin_start = min(values) - bin_width / 2
            bin_end = max(values) + bin_width * 1.5
            
            # Create bins based on the defined start, end, and width
            bins = np.arange(bin_start, bin_end, bin_width)

            # Calculate histogram
            hist, bin_edges = np.histogram(values, bins=bins)
            
            # Convert bin_edges to bin centers
            bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
            
            # Plot the bars
            #print(bin_centers)
            bars = axs[i].bar(bin_centers, hist, align='center', width=bin_width, color=colors[index], edgecolor='black', log=True, zorder=3)

        axs[i].set_xlabel(f'Delay {delay}', fontsize=12)
        axs[i].set_yscale('symlog')
        axs[i].set_xticks(np.arange(min(all_values), max(all_values) + 1, 1))
        axs[i].set_xlim(min(all_values) - 0.5, max(all_values) + 0.5)  # Set x-axis limits to reduce spacing
        axs[i].grid(True, zorder=0)

    # Create a single legend for all sizes
    legend_handles = [plt.Rectangle((0,0),1,1, color=color, edgecolor='black') for color in colors]
    fig.legend(legend_handles, [f'Size {size}' for size in sizes], title='Sizes', fontsize=12, loc='upper center', ncol=len(sizes))

    fig.text(0.04, 0.5, 'Number of occurrences\n(symmetrical log scale)', va='center', ha='center', rotation='vertical', fontsize=12)

    plt.tight_layout(pad=2.0)
    plt.subplots_adjust(top=0.85, left=0.075, right=0.975, wspace=0.1)  # Adjust the left and right to fit the y-axis label, reduced wspace
    #plt.savefig('../dissertation/images/figures/count_all.pgf', bbox_inches='tight', dpi=300)
    plt.show()

    
def prepare_histogram_data(size, test_type, delay):
    file_path = f'results/{size}/{delay}/alarms.'
    
    format_file(file_path + 'txt', file_path + 'csv')
    
    with open(file_path + 'csv', 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
    
    values = [float(row[0]) for row in data]
    differences = [values[i + 1] - values[i] for i in range(len(values) - 1)][1:]
    
    bin_start = 0  # Adjust if you expect values lower than 0
    bin_end = max(differences) + 5  # Extend beyond the max value to include all data
    bin_width = 5  # Interval width
    bins = np.arange(bin_start, bin_end, bin_width)
    counts, bin_edges = np.histogram(differences, bins=bins)

    # Save histogram data
    with open("histogram_data.txt", "w") as out_file:
        for count, edge in zip(counts, bin_edges[:-1]):
            out_file.write(f"{edge} {count}\n")

def bars_graph(sizes, test_type, delays):
    delay_values = [[], [], []]
    
    for delay_count, delay in enumerate(delays):
        for size in sizes:
            file_path = f'results/{size}/sporadic/{delay}/alarms.'
            format_file(file_path + 'txt', file_path + 'csv')
            with open(file_path + 'csv', 'r') as file:
                delay_values[delay_count].append(len(file.readlines()))
    plt.figure(figsize=(10, 6))
    # Create the dashed reference line
    #plt.grid(True, zorder=0)
    ref_line = plt.axhline(y=998, color='gray', linestyle='--', linewidth=1, label='998 packets')
    
    plt.xlabel("Cyclic buffer sizes", fontsize=20)
    plt.ylabel('Alarm count', fontsize=20)

    barWidth = 0.25

    br1 = np.arange(len(delay_values[0])) 
    br2 = [x + barWidth for x in br1] 
    br3 = [x + barWidth for x in br2]

    bars1 = plt.bar(br1, delay_values[0], color ='lightcoral', width = barWidth, edgecolor ='grey', label ='10s delay') 
    bars2 = plt.bar(br2, delay_values[1], color ='mediumspringgreen', width = barWidth, edgecolor ='grey', label ='20s delay') 
    bars3 = plt.bar(br3, delay_values[2], color ='lightskyblue', width = barWidth, edgecolor ='grey', label ='30s delay') 
    
    plt.xticks([r + barWidth for r in range(len(delay_values[0]))], sizes, fontsize=16)
    plt.yticks(fontsize=16)

    # Add text annotations to the bars
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval+15, int(yval), ha='center', va='bottom', color='black', fontsize=12)
    plt.ylim(0, 1700)
    # Creating a custom legend
    plt.legend(handles=[bars1, bars2, bars3, ref_line], fontsize=14, loc='upper center', ncol=4)#, title='Delays and Reference')
    #plt.savefig('../dissertation/images/figures/results.pgf', bbox_inches='tight', dpi=300)
    
    plt.show()

def inversed_bars_graph(sizes, test_type, delays):

    delay_values = [[],
                    [],
                    [],
                    []]
    
    for size_count, size in enumerate(sizes):
        for delay in delays:
            file_path = f'results/{size}/{test_type}/{delay}/alarms.'
            format_file(file_path + 'txt', file_path + 'csv')
            with open(file_path + 'csv', 'r') as file:
                delay_values[size_count].append(len(file.readlines()))
    
    plt.ylim(1000, 1250)
    plt.xlabel("Delays")
    plt.ylabel('Alarm count')

    barWidth = 0.15

    br1 = np.arange(len(delay_values[0])) 
    br2 = [x + barWidth for x in br1] 
    br3 = [x + barWidth for x in br2]
    br4 = [x + barWidth for x in br3]
    
    plt.bar(br1, delay_values[0], color ='lightcoral', width = barWidth, 
            edgecolor ='grey', label ='1000') 
    plt.bar(br2, delay_values[1], color ='lime', width = barWidth, 
            edgecolor ='grey', label ='2000') 
    plt.bar(br3, delay_values[2], color ='aqua', width = barWidth, 
            edgecolor ='grey', label ='5000')
    plt.bar(br4, delay_values[3], color ='yellow', width = barWidth, 
            edgecolor ='grey', label ='10000') 
    
    plt.xticks([r + barWidth + 0.075 for r in range(len(delay_values[0]))], 
            ['10', '20', '30'])
    
    plt.legend(title='Cyclic buffer sizes')
    plt.show()

def single_bar_graph(sizes, test_type, delays):
    delay_values = [[]]  # Adjusted for a single delay value

    for delay in delays:
        for size in sizes:
            file_path = f'results/{size}/sporadic/{delay}/alarms.'
            format_file(file_path + 'txt', file_path + 'csv')
            with open(file_path + 'csv', 'r') as file:
                delay_values[0].append(len(file.readlines()))
    
    plt.figure(figsize=(10, 6))
    
    plt.xlabel("Cyclic buffer sizes", fontsize=20)
    plt.ylabel('Alarm count\n(symmetrical log scale)', fontsize=20)

    barWidth = 0.2  # Adjusted bar width for better visualization

    # Directly use the indices of sizes for bar positions
    br1 = np.arange(len(sizes)) 

    # Plotting the single set of bars centered over the x-ticks
    bars1 = plt.bar(br1, delay_values[0], color='lightskyblue', width=barWidth, edgecolor='grey', label='10s delay') 
    
    plt.yscale('symlog')
    plt.xticks(br1, sizes, fontsize=16)
    plt.yticks(fontsize=16)
    plt.ylim(0, 500)

    # Add text annotations to the bars
    for bar in bars1:
        yval = bar.get_height()
        if yval > 10:
            plt.text(bar.get_x() + bar.get_width()/2, yval+15, int(yval), ha='center', va='bottom', color='black', fontsize=14)
        else:
            plt.text(bar.get_x() + bar.get_width()/2, yval+0.2, int(yval), ha='center', va='bottom', color='black', fontsize=14)

    #plt.legend(fontsize=18)
    plt.tight_layout(pad=6.0)
    #plt.savefig('../dissertation/images/figures/fast_results_sporadic.pgf', bbox_inches='tight', dpi=300)
    plt.show()

if __name__ == "__main__":
    sizes = [400,450,500,550,10000]
    test_type = 'default'
    delays = ['10', '20', '30']
    colors = ['red', 'blue', 'green']
    #dispersion([400,450,500, 550, 10000], test_type, delays, colors)
    #diffs_graph(550, test_type, 'fast1')
    #new_diffs_graph(550, test_type, 'fast')
    #value_frequency_graph()
    #prepare_histogram_data(size, test_type, '20')
    #bars_graph(sizes, test_type, delays)
    #inversed_bars_graph(sizes, test_type, delays)
    #full_value_graph()
    #single_bar_graph(sizes, test_type, ['fast'])
    format_file(f'results/10000/sporadic/example/alarms.txt', f'results/10000/sporadic/example/alarms.csv')


"""
def bars_graph(sizes, test_type, delays):
    delay_values = [[]]  # Adjusted for a single delay value

    for delay in delays:
        for size in sizes:
            file_path = f'results/{size}/{delay}/alarms.'
            format_file(file_path + 'txt', file_path + 'csv')
            with open(file_path + 'csv', 'r') as file:
                delay_values[0].append(len(file.readlines()))
    
    plt.figure(figsize=(10, 6))
    
    plt.xlabel("Cyclic buffer sizes", fontsize=20)
    plt.ylabel('Alarm count', fontsize=20)

    barWidth = 0.5  # Adjusted bar width for better visualization

    # Directly use the indices of sizes for bar positions
    br1 = np.arange(len(sizes)) 

    # Plotting the single set of bars centered over the x-ticks
    bars1 = plt.bar(br1, delay_values[0], color='lightcoral', width=barWidth, edgecolor='grey', label='10s delay') 
    
    plt.yscale('symlog')
    plt.xticks(br1, sizes, fontsize=16)
    plt.yticks(fontsize=16)
    plt.ylim(0, 500)

    # Add text annotations to the bars
    for bar in bars1:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom', color='black', fontsize=12)

    plt.legend(fontsize=18)
    plt.show()

    
    def format_file(input_filename, output_filename):
    with open(input_filename, 'r') as input_file:
        content = input_file.read()

    matches = re.findall(r'digest _digest_notification_digest_t_1 .*?\{(.*?)\}', content, re.DOTALL)

    data = []
    for match in matches:
        entries = re.findall(r'scalars\.(.*?) : (0x[0-9a-fA-F]+)', match)
        entry_dict = {key.strip(): hex_to_decimal(value) for key, value in entries}

        # Additional conversions
        entry_dict['tmp_10'] /= 1e9
        entry_dict['tmp_9'] += entry_dict['tmp_10']
        entry_dict['tmp_7'] /= 100
        entry_dict['tmp_8'] /= 100
        del entry_dict['tmp_10']
        data.append(entry_dict)
    
    fieldnames = data[0].keys() if data else []
    with open(output_filename, 'w', newline='') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writerows(data)

def process_differences(input_filename, delay_val, col):
    with open(input_filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header if present
        data = list(reader)

    values = [float(row[0]) for row in data]

    differences = [values[i + 1] - values[i] for i in range(len(values) - 1)]
    
    global maxi
    if maxi < max(differences[1:]):
        maxi = max(differences[1:])

    ref_values = [int(delay_val)] * len(differences)

    plt.scatter(differences[1:], ref_values[1:], s=50, c=col, edgecolor='none', alpha=0.1)

def dispersion(size, test_type, delays, colors):

    legend_entries = []

    for delay, color in zip(delays, colors):
        plt.axhline(y=int(delay), color='gray', linestyle='--', linewidth=0.5)
        legend_entries.append(Line2D([0], [0], marker='o', color='w', markersize=5, markerfacecolor=f"{color}", label=f"{delay}s"))
        file_path = f'results/{size}/{delay}/alarms.'
        format_file(file_path + 'txt', file_path + 'csv')
        process_differences(file_path + 'csv', delay, color)

    plt.plot([0,maxi],[0,maxi], 'k-')
    plt.ylim(0, 31)
    plt.xlim(-0.3, 61)
    plt.xlabel("Time passed")
    plt.ylabel('Time expected')
    plt.title(f'Cyclic buffer size - {size}')
    plt.legend(handles=legend_entries, loc='lower right', title='Delays')
    plt.show()
    
def full_value_graph():
    data = {
        10: {
            400: {4: 58, 5: 991},
            450: {4: 122, 5: 991},
            500: {4: 1, 5: 991},
            550: {4: 1, 5: 991},
            10000: {4: 1, 5: 991}
        },
        20: {
            400: {4: 733, 5: 990},
            450: {4: 16, 5: 990},
            500: {4: 4, 5: 991},
            550: {4: 1, 5: 991},
            10000: {4: 1, 5: 991}
        },
        30: {
            400: {2: 1, 3: 3, 4: 513, 5: 991},
            450: {4: 2, 5: 991},
            500: {4: 3, 5: 991},
            550: {4: 1, 5: 991},
            10000: {4: 1, 5: 991}
        }
    }

    colors = {
        400: 'lightcoral',
        450: 'mediumspringgreen',
        500: (1, 1, 0.5),
        550: 'orange',
        10000: 'lightskyblue'
    }

    fig, axs = plt.subplots(1, 3, figsize=(12, 7), sharey=True)
    delays = [10, 20, 30]

    for i, delay in enumerate(delays):
        #axs[i].grid(True, zorder=0, linewidth=0.5, alpha=0.5) 
        x_values = sorted(set().union(*[data[delay][size].keys() for size in data[delay].keys()]))
        max_dict = {}

        for size in sorted(colors.keys(), reverse=True):
            for x in x_values:
                y_val = data[delay][size].get(x, 0)
                if y_val > 0:
                    if x not in max_dict:
                        max_dict[x] = [[y_val, size]]
                    else:
                        found = False
                        for item in max_dict[x]:
                            if item[0] == y_val:
                                if size > item[1]:
                                    item[1] = size
                                found = True
                        if not found:
                            max_dict[x].append([y_val, size])

        for x in sorted(max_dict.keys()):
            start_val = 0
            for val, size in sorted(max_dict[x], key=lambda item: item[0]):
                bar = axs[i].bar(x, val - start_val, bottom=start_val, color=colors[size], width=0.4, linewidth=0.4, edgecolor='black',zorder=3)
                # Adding text annotations on top of each bar
                for rect in bar:
                    height = rect.get_height()
                    if height == 990:
                        # Adjust the text to be slightly below the top if the height is 990
                        axs[i].annotate(f'{start_val + height}',
                                        xy=(rect.get_x() + rect.get_width() / 2, start_val + height),
                                        xytext=(0, -5),  # 12 points vertical offset downwards
                                        textcoords="offset points",
                                        ha='center', va='top', fontsize=13, color='black', zorder=5)
                    else:
                        axs[i].annotate(f'{start_val + height}',
                                        xy=(rect.get_x() + rect.get_width() / 2, start_val + height),
                                        xytext=(0, 2),  # 3 points vertical offset upwards
                                        textcoords="offset points",
                                        ha='center', va='bottom', fontsize=13, color='black', zorder=5)
                start_val = val

        axs[i].set_title(f'Probe delay: {delay}s', fontsize=14)
        axs[i].set_yscale('symlog')
        axs[i].set_xticks(np.arange(min(x_values), max(x_values) + 1, 1))
        axs[i].set_xlim(min(x_values) - 0.5, max(x_values) + 0.5)
        axs[i].set_ylim(0,3000)
        #axs[i].set_xticks(x_values)
        axs[i].set_xlabel("Distinct counter value", fontsize=16, labelpad=10)
        axs[i].set_xticklabels(x_values)
        axs[i].tick_params(axis='x', labelsize=14) 
        axs[i].tick_params(axis='y', labelsize=14)

    fig.text(0.04, 0.5, 'Number of occurrences\n(symmetrical log scale)', va='center', ha='center', rotation='vertical', fontsize=16)
    #fig.text(0.5, 0.015, 'Distinct counter value', va='center', ha='center', rotation='horizontal', fontsize=16)

    # Create a custom legend
    handles = [plt.Line2D([0], [0], color=colors[size], lw=4) for size in sorted(colors.keys())]
    labels = [str(size) for size in sorted(colors.keys())]
    legend = fig.legend(handles, labels, title='Cyclic buffer sizes', loc='upper center', ncol=len(labels), fontsize=14)  # Adjust fontsize as needed
    legend.get_title().set_fontsize(14)
    
    plt.tight_layout(pad=2.0)
    plt.subplots_adjust(top=0.84, left=0.1, right=0.975, wspace=0.05)
    #plt.savefig('../dissertation/images/figures/count_all.pgf', bbox_inches='tight', dpi=300)
    plt.show()
        
    
"""
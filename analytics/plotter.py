import matplotlib.pyplot as plt
import os

def generate_plots(exp1_results, exp2_results):
    # Ensure directory exists for saving plots
    os.makedirs('analytics/plots', exist_ok=True)
    
    # --- Experiment 1: Varying Green Light Time ---
    green_times = [res[0] for res in exp1_results]
    wait_times_1 = [res[1]['avg_wait_time'] for res in exp1_results]
    throughputs_1 = [res[1]['throughput'] for res in exp1_results]
    queues_1 = [res[1]['max_queue_length'] for res in exp1_results]
    
    # Plot 1a: Wait Time vs. Green Light Time
    plt.figure(figsize=(8, 5))
    plt.plot(green_times, wait_times_1, marker='o', color='b')
    plt.title('Average Wait Time vs. Green Light Duration')
    plt.xlabel('Green Light Duration (seconds)')
    plt.ylabel('Average Wait Time (seconds)')
    plt.grid(True)
    plt.savefig('analytics/plots/plt_exp1_wait_time.png')
    plt.close()
    
    # Plot 1b: Throughput vs. Green Light Time
    plt.figure(figsize=(8, 5))
    plt.plot(green_times, throughputs_1, marker='s', color='g')
    plt.title('Throughput vs. Green Light Duration')
    plt.xlabel('Green Light Duration (seconds)')
    plt.ylabel('Throughput (vehicles/min)')
    plt.grid(True)
    plt.savefig('analytics/plots/plt_exp1_throughput.png')
    plt.close()
    
    # Plot 1c: Max Queue Length vs. Green Light Time
    plt.figure(figsize=(8, 5))
    plt.plot(green_times, queues_1, marker='^', color='orange')
    plt.title('Maximum Queue Length vs. Green Light Duration')
    plt.xlabel('Green Light Duration (seconds)')
    plt.ylabel('Max Queue Length (vehicles)')
    plt.grid(True)
    plt.savefig('analytics/plots/plt_exp1_queue_length.png')
    plt.close()
    
    # --- Experiment 2: Varying Arrival Rate ---
    arrival_rates = [res[0] for res in exp2_results]
    wait_times_2 = [res[1]['avg_wait_time'] for res in exp2_results]
    throughputs_2 = [res[1]['throughput'] for res in exp2_results]
    queues_2 = [res[1]['max_queue_length'] for res in exp2_results]
    
    # Plot 2a: Wait Time vs. Arrival Rate
    plt.figure(figsize=(8, 5))
    plt.plot(arrival_rates, wait_times_2, marker='o', color='r')
    plt.title('Average Wait Time vs. Arrival Rate')
    plt.xlabel('Arrival Rate (vehicles/second)')
    plt.ylabel('Average Wait Time (seconds)')
    plt.grid(True)
    plt.savefig('analytics/plots/plt_exp2_wait_time.png')
    plt.close()
    
    # Plot 2b: Throughput vs. Arrival Rate
    plt.figure(figsize=(8, 5))
    plt.plot(arrival_rates, throughputs_2, marker='s', color='purple')
    plt.title('Throughput vs. Arrival Rate')
    plt.xlabel('Arrival Rate (vehicles/second)')
    plt.ylabel('Throughput (vehicles/min)')
    plt.grid(True)
    plt.savefig('analytics/plots/plt_exp2_throughput.png')
    plt.close()
    
    # Plot 2c: Max Queue Length vs. Arrival Rate
    plt.figure(figsize=(8, 5))
    plt.plot(arrival_rates, queues_2, marker='^', color='orange')
    plt.title('Maximum Queue Length vs. Arrival Rate')
    plt.xlabel('Arrival Rate (vehicles/second)')
    plt.ylabel('Max Queue Length (vehicles)')
    plt.grid(True)
    plt.savefig('analytics/plots/plt_exp2_queue_length.png')
    plt.close()

import os
import time
import hashlib
import csv
import matplotlib.pyplot as plt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def generate_timestamp():
    return time.time()

def generate_random_number():
    return os.urandom(16)

def hash_data(data):
    sha1 = hashlib.sha1()
    sha1.update(data)
    return sha1.digest()

def encrypt_data(data):
    key = os.urandom(32)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()
    return encrypted_data

def perform_operations(steps):
    total_time = 0
    total_size_mb = 0
    results = []
    
    for step in steps:
        step_time = 0
        step_size = 0
        step_result = {'step': step['step'], 'operations': []}
        
        for _ in range(step['num_operations']):
            start_time = time.time()
            
            for _ in range(step['generate_timestamp']):
                generate_timestamp()
                
            for _ in range(step['generate_random']):
                generate_random_number()
                
            for _ in range(step['hash']):
                data = os.urandom(1024)
                hash_data(data)
                
            for _ in range(step['encrypt']):
                data = os.urandom(1024)
                encrypt_data(data)
                
            end_time = time.time()
            
            step_time += end_time - start_time
            step_size += step['photos'] * 10
            
            step_result['operations'].append({
                'generate_timestamp': step['generate_timestamp'],
                'generate_random': step['generate_random'],
                'hash': step['hash'],
                'encrypt': step['encrypt'],
                'photos': step['photos'],
                'time': end_time - start_time
            })
        
        total_time += step_time
        total_size_mb += step_size
        step_result['total_time'] = step_time
        step_result['total_size_mb'] = step_size
        results.append(step_result)
        
    return total_time, total_size_mb, results

def read_input_file(filename):
    phases = {}
    with open(filename, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            phase_name = row['phase_name']
            step = {
                'step': row['step'],
                'generate_timestamp': int(row['generate_timestamp']),
                'generate_random': int(row['generate_random']),
                'hash': int(row['hash']),
                'encrypt': int(row['encrypt']),
                'photos': int(row['photos']),
                'num_operations': 1
            }
            if phase_name not in phases:
                phases[phase_name] = []
            phases[phase_name].append(step)
    return phases

def write_results_to_csv(filename, results):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['phase_name', 'step', 'generate_timestamp', 'generate_random', 'hash', 'encrypt', 'photos', 'time', 'total_time', 'total_size_mb', 'ram', 'cpu_cores'])
        for phase in results:
            for step in phase['steps']:
                for operation in step['operations']:
                    writer.writerow([
                        phase['phase_name'], step['step'], operation['generate_timestamp'], operation['generate_random'],
                        operation['hash'], operation['encrypt'], operation['photos'], 
                        format(operation['time'], '.6f'),
                        format(step['total_time'], '.6f'), 
                        format(step['total_size_mb'], '.6f'),
                        phase['ram'], phase['cpu_cores']
                    ])

def write_summary_to_csv(filename, grouped_results, phases, ram_values, cpu_core_values):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['phase_name', 'ram', 'cpu_cores', 'total_time'])
        for phase in phases:
            for ram in ram_values:
                for cores in cpu_core_values:
                    total_time = grouped_results.get((phase, ram, cores), 0)
                    writer.writerow([phase, ram, cores, total_time])

def read_results_from_csv(filename):
    results = []
    with open(filename, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            results.append({
                'phase_name': row['phase_name'],
                'step': row['step'],
                'generate_timestamp': int(row['generate_timestamp']),
                'generate_random': int(row['generate_random']),
                'hash': int(row['hash']),
                'encrypt': int(row['encrypt']),
                'photos': int(row['photos']),
                'time': float(row['time']),
                'total_time': float(row['total_time']),
                'total_size_mb': float(row['total_size_mb']),
                'ram': int(row['ram']),
                'cpu_cores': int(row['cpu_cores'])
            })
    return results

def plot_results(results):
    # Grupowanie wyników według fazy i konfiguracji sprzętowej
    grouped_results = {}
    for result in results:
        key = (result['phase_name'], result['ram'], result['cpu_cores'])
        if key not in grouped_results:
            grouped_results[key] = 0
        grouped_results[key] += result['total_time']

    # Przygotowanie danych do wykresu
    phases = sorted(set(key[0] for key in grouped_results.keys()))
    ram_values = [1, 2, 4, 8]
    cpu_core_values = [1, 2, 4, 8]

    fig, axs = plt.subplots(2, 2, figsize=(16, 12))
    fig.subplots_adjust(hspace=0.4, wspace=0.4)
    
    for i, ram in enumerate(ram_values):
        ax = axs[i // 2, i % 2]
        for phase in phases:
            phase_results = [grouped_results.get((phase, ram, cores), 0) for cores in cpu_core_values]
            ax.plot(cpu_core_values, phase_results, marker='o', label=phase)
        
        ax.set_xlabel('CPU Cores')
        ax.set_ylabel('Total Time (s)')
        ax.set_title(f'Total Time for Each Phase (RAM {ram}GB)')
        ax.legend()

    plt.tight_layout()
    plt.savefig('total_time_by_phase_and_configuration.png')
    plt.show()

    return grouped_results, phases, ram_values, cpu_core_values

def main():
    input_filename = 'input.csv'
    output_filename = 'results.csv'
    summary_filename = 'summary_results.csv'
    configurations = []
    ram_values = [1, 2, 4, 8, 16]
    cpu_core_values = [1, 2, 4, 8]
    
    for ram in ram_values:
        for cores in cpu_core_values:
            configurations.append({'ram': ram, 'cpu_cores': cores})

    phases = read_input_file(input_filename)
    all_results = []

    for config in configurations:
        config_results = []
        for phase_name, steps in phases.items():
            total_time, total_size_mb, phase_results = perform_operations(steps)
            config_results.append({
                'phase_name': phase_name,
                'ram': config['ram'],
                'cpu_cores': config['cpu_cores'],
                'total_time': total_time,
                'total_size_mb': total_size_mb,
                'steps': phase_results
            })
        all_results.extend(config_results)

    write_results_to_csv(output_filename, all_results)
    results = read_results_from_csv(output_filename)
    grouped_results, phases, ram_values, cpu_core_values = plot_results(results)
    write_summary_to_csv(summary_filename, grouped_results, phases, ram_values, cpu_core_values)
    print("Wyniki zostały zapisane do pliku 'results.csv' oraz wykresy zostały wygenerowane.")
    print("Podsumowanie wyników zostało zapisane do pliku 'summary_results.csv'.")

if __name__ == "__main__":
    main()

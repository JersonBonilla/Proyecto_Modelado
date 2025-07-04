'''
Main entry point of the simulation. Allows the user to run several runs
of the 3-computer system simulation, view the progress on the console and display
detailed statistics at the end of each run, as well as a final summary.
'''

from simulator import Simulation
from statistics import mean, stdev
from math import sqrt

def run_simulations(runs=5, duration=100, slow=False):
    '''
    Runs multiple consecutive simulations, collects statistics for each and 
    displays detailed results and overall averages.

    :param runs: Number of times the simulation will be executed.
    :param duration: Maximum time (in simulated seconds) for each run.
    :param slow: If True, it is shown step by step with pause between events.
    '''

    all_stats = []  # List for accumulating statistics of every run.

    for i in range(runs):
        print(f"\n--- Starting Run {i + 1}/{runs} ---\n")

        # Create and execute simulation.
        sim = Simulation(duration, run_number=i + 1, slow=slow)
        sim.run()

        # Get statistics of this run.
        stats = sim.collect_stats()
        stats['run'] = i + 1
        all_stats.append(stats)

        # Ask if user wants to see detailed statistics.
        show_stats = input(f"\nDo you want to see statistics for run #{i + 1}? (y/n): ").strip().lower()
        if show_stats.startswith('y'):
            print("\n" + "="*40)
            print(f"STATISTICS FOR RUN #{i + 1}".center(40))
            print("="*40)

            # Show key metrics (confidence intervals omitted here).
            for key, val in stats.items():
                if key.startswith("CI_") or key == "run":
                    continue
                label = {
                    'T_C2': 'Avg time (C2)',
                    'T_C3': 'Avg time (C3)',
                    'T_RJ': 'Avg time (Rejected)',
                    'T_ALL': 'Avg total time',
                    'E_C2': 'Efficiency (C2)',
                    'E_C3': 'Efficiency (C3)',
                    'E_RJ': 'Efficiency (Rejected)',
                    'E_ALL': 'Overall efficiency',
                    'U_C1': 'Utilization (C1)',
                    'U_C2': 'Utilization (C2)',
                    'U_C3': 'Utilization (C3)',
                    'TRIO_TIME': 'Total Trio Time',
                    'TRIO_PERCENT': 'Trio Occupancy %'
                }.get(key, key)

                # Add units to metrics.
                unit = "s" if "time" in label.lower() else ("%" if "Percent" in key or "Utilization" in label else "")
                print(f"{label:<24}: {val:.4f} {unit}")


    # ================= AFTER FINISHING ALL RUNS =================
    # Show short summary for each run.
    print("\n" + "="*40)
    print("RUN SUMMARIES".center(40))
    print("="*40)
    for s in all_stats:
        print(f"Run {s['run']:>2}: Avg Total Time (T_ALL) = {s['T_ALL']:.2f} s | Efficiency = {s['E_ALL']:.2f}")

    # Average of all key metrics
    print("\n" + "="*40)
    print("AVERAGE METRICS".center(40))
    print("="*40)
    for key in [k for k in all_stats[0] if k != 'run' and not k.startswith('CI_')]:
        vals = [s[key] for s in all_stats]
        label = {
            'T_C2': 'Avg time (C2)',
            'T_C3': 'Avg time (C3)',
            'T_RJ': 'Avg time (Rejected)',
            'T_ALL': 'Avg total time',
            'E_C2': 'Efficiency (C2)',
            'E_C3': 'Efficiency (C3)',
            'E_RJ': 'Efficiency (Rejected)',
            'E_ALL': 'Overall efficiency',
            'U_C1': 'Utilization (C1)',
            'U_C2': 'Utilization (C2)',
            'U_C3': 'Utilization (C3)',
            'TRIO_TIME': 'Total Trio Time',
            'TRIO_PERCENT': 'Trio Occupancy %'
        }.get(key, key)

        unit = "s" if "time" in label.lower() else ("%" if "Percent" in key or "Utilization" in label else "")
        print(f"{label:<24}: {sum(vals)/len(vals):.4f} {unit}")

    def confidence_interval(data):
        if len(data) < 2:
            return (0.0, 0.0)
        m = mean(data)
        s = stdev(data)
        h = 1.96 * s / sqrt(len(data))  # 95% confidence
        return (m - h, m + h)

    # Show confidence intervals (last run used as reference).
    print("\n" + "="*40)
    print("95% CONFIDENCE INTERVALS".center(40))
    print("="*40)
    names = {
        'T_C2': 'Time (C2)',
        'T_C3': 'Time (C3)',
        'T_RJ': 'Time (Rejected)',
        'T_ALL': 'Total Time'
    }
    
    for key in ['T_C2', 'T_C3', 'T_RJ', 'T_ALL']:
        values = [s[key] for s in all_stats]
        ci = confidence_interval(values)
        print(f"{names[key]:<18}: [{ci[0]:.2f}, {ci[1]:.2f}] s")
    
    with open("simulation_results.txt", "w") as f:
        f.write("=== DETAILED RUN STATISTICS ===\n\n")
        for s in all_stats:
            f.write(f"--- Run {s['run']} ---\n")
            for key, val in s.items():
                if key.startswith("CI_") or key == "run":
                    continue
                label = {
                    'T_C2': 'Avg time (C2)',
                    'T_C3': 'Avg time (C3)',
                    'T_RJ': 'Avg time (Rejected)',
                    'T_ALL': 'Avg total time',
                    'E_C2': 'Efficiency (C2)',
                    'E_C3': 'Efficiency (C3)',
                    'E_RJ': 'Efficiency (Rejected)',
                    'E_ALL': 'Overall efficiency',
                    'U_C1': 'Utilization (C1)',
                    'U_C2': 'Utilization (C2)',
                    'U_C3': 'Utilization (C3)',
                    'TRIO_TIME': 'Total Trio Time',
                    'TRIO_PERCENT': 'Trio Occupancy %'
                }.get(key, key)
                unit = "s" if "time" in label.lower() else ("%" if "Percent" in key or "Utilization" in label else "")
                f.write(f"{label:<24}: {val:.4f} {unit}\n")
            f.write("\n")

        f.write("="*40 + "\n")
        f.write("RUN SUMMARIES\n")
        f.write("="*40 + "\n")
        for s in all_stats:
            f.write(f"Run {s['run']:>2}: Avg Total Time (T_ALL) = {s['T_ALL']:.2f} s | Efficiency = {s['E_ALL']:.2f}\n")

        f.write("\n" + "="*40 + "\n")
        f.write("AVERAGE METRICS\n")
        f.write("="*40 + "\n")
        for key in [k for k in all_stats[0] if k != 'run' and not k.startswith('CI_')]:
            vals = [s[key] for s in all_stats]
            label = {
                'T_C2': 'Avg time (C2)',
                'T_C3': 'Avg time (C3)',
                'T_RJ': 'Avg time (Rejected)',
                'T_ALL': 'Avg total time',
                'E_C2': 'Efficiency (C2)',
                'E_C3': 'Efficiency (C3)',
                'E_RJ': 'Efficiency (Rejected)',
                'E_ALL': 'Overall efficiency',
                'U_C1': 'Utilization (C1)',
                'U_C2': 'Utilization (C2)',
                'U_C3': 'Utilization (C3)',
                'TRIO_TIME': 'Total Trio Time',
                'TRIO_PERCENT': 'Trio Occupancy %'
            }.get(key, key)
            unit = "s" if "time" in label.lower() else ("%" if "Percent" in key or "Utilization" in label else "")
            f.write(f"{label:<24}: {sum(vals)/len(vals):.4f} {unit}\n")

        f.write("\n" + "="*40 + "\n")
        f.write("95% CONFIDENCE INTERVALS\n")
        f.write("="*40 + "\n")
        names = {
            'T_C2': 'Time (C2)',
            'T_C3': 'Time (C3)',
            'T_RJ': 'Time (Rejected)',
            'T_ALL': 'Total Time'
        }

        for key in ['T_C2', 'T_C3', 'T_RJ', 'T_ALL']:
            values = [s[key] for s in all_stats]
            ci = confidence_interval(values)
            f.write(f"{names[key]:<18}: [{ci[0]:.2f}, {ci[1]:.2f}] s\n")

    print("\nResults saved to 'simulation_results.txt'!")


if __name__ == "__main__":
    print("=== Simulation Setup ===")
    try:
        # Ask user for configuration.
        runs = int(input("Enter number of runs: "))
        duration = float(input("Enter max simulation time (in seconds): "))
        mode = input("Simulation mode ('slow' or 'fast'): ").strip().lower()
        slow = (mode == "slow")
    except Exception as e:
        # If error, use default settings.
        print("Invalid input. Using default settings.")
        runs = 5
        duration = 100
        slow = False

    # Execute simulations
    run_simulations(runs=runs, duration=duration, slow=slow)
    
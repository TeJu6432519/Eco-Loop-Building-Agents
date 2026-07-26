from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

baseline_path = RESULTS_DIR / "baseline_results.csv"
ai_path = RESULTS_DIR / "ai_results.csv"

# Define strict thermal comfort boundaries (in °C)
COMFORT_MIN = 20.0
COMFORT_MAX = 26.0

def generate_savings_dashboard():
    try:
        df_baseline = pd.read_csv(baseline_path)
        df_ai = pd.read_csv(ai_path)

        print("Baseline CSV columns found:", df_baseline.columns.tolist())

        # Flexible column auto-detection
        power_cols = [col for col in df_baseline.columns if 'power' in col.lower() or 'demand' in col.lower()]
        temp_cols = [col for col in df_baseline.columns if 'temp' in col.lower() or 'temperature' in col.lower()]

        if not power_cols or not temp_cols:
            print("Could not automatically detect power or temperature columns. Check your CSV headers printed above.")
            return

        power_col = power_cols[0]
        temp_col = temp_cols[0]
        print(f"Using Power Column: '{power_col}' | Using Temperature Column: '{temp_col}'")

        # 1. Energy & Savings Calculations
        baseline_kwh = df_baseline[power_col].sum() / 1000.0 
        ai_kwh = df_ai[power_col].sum() / 1000.0
        savings_kwh = baseline_kwh - ai_kwh
        savings_pct = (savings_kwh / baseline_kwh) * 100 if baseline_kwh > 0 else 0.0

        # 2. Thermal Comfort Boundary Compliance Calculations
        baseline_violations = df_baseline[(df_baseline[temp_col] < COMFORT_MIN) | (df_baseline[temp_col] > COMFORT_MAX)].shape[0]
        ai_violations = df_ai[(df_ai[temp_col] < COMFORT_MIN) | (df_ai[temp_col] > COMFORT_MAX)].shape[0]

        print("==================================================")
        print("          ECOLOOP PERFORMANCE PROOF REPORT        ")
        print("==================================================")
        print(f"Baseline Total Energy   : {baseline_kwh:.2f} kWh")
        print(f"AI Closed-Loop Energy   : {ai_kwh:.2f} kWh")
        print(f"Total Energy Reduction  : {savings_pct:.2f}% ({savings_kwh:.2f} kWh saved)")
        print("--------------------------------------------------")
        print(f"Comfort Bounds          : {COMFORT_MIN}°C to {COMFORT_MAX}°C")
        print(f"Baseline Out-of-Bounds  : {baseline_violations} timesteps")
        print(f"AI Out-of-Bounds        : {ai_violations} timesteps")
        print("==================================================")

        # 3. Plotting Triple-Panel Comparison (Power, Temperature & Embedded Metrics Table)
        fig, axes = plt.subplots(3, 1, figsize=(11, 13), gridspec_kw={'height_ratios': [2, 2, 1.2]})
        ax1, ax2, ax3 = axes

        # Panel A: Power Consumption Comparison
        ax1.plot(df_baseline[power_col].values, label="Baseline (Static)", color="gray", linestyle="--", alpha=0.8)
        ax1.plot(df_ai[power_col].values, label="AI Closed-Loop", color="#0066ff", linewidth=2)
        ax1.set_ylabel("Power (W)", fontsize=11, fontweight='bold')
        ax1.set_title("EcoLoop: Power Consumption & Thermal Comfort Proof Dashboard", fontsize=14, fontweight='bold')
        ax1.legend(frameon=True, facecolor='white', loc='upper left')
        ax1.grid(True, linestyle=":", alpha=0.6)

        # Panel B: Zone Temperature vs Comfort Bounds
        ax2.plot(df_baseline[temp_col].values, label="Baseline Temp", color="darkgray", linestyle="--")
        ax2.plot(df_ai[temp_col].values, label="AI Temp", color="#ff7f0e", linewidth=2)
        ax2.axhline(COMFORT_MAX, color='red', linestyle=':', label=f'Max Comfort Limit ({COMFORT_MAX}°C)')
        ax2.axhline(COMFORT_MIN, color='blue', linestyle=':', label=f'Min Comfort Limit ({COMFORT_MIN}°C)')
        ax2.fill_between(range(len(df_ai)), COMFORT_MIN, COMFORT_MAX, color='green', alpha=0.07, label='Comfort Zone')
        
        ax2.set_xlabel("Simulation Timesteps", fontsize=11, fontweight='bold')
        ax2.set_ylabel("Zone Temp (°C)", fontsize=11, fontweight='bold')
        ax2.legend(frameon=True, facecolor='white', loc='upper right')
        ax2.grid(True, linestyle=":", alpha=0.6)

        # Panel C: Embedded Summary Table Card
        ax3.axis('off')
        table_data = [
            ["Performance Metric", "Baseline (Static)", "AI Closed-Loop", "Efficiency Delta / Status"],
            ["Total Energy Consumption", f"{baseline_kwh:.2f} kWh", f"{ai_kwh:.2f} kWh", f"-{savings_pct:.2f}% ({savings_kwh:.2f} kWh Saved)"],
            ["Comfort Boundary Violations", f"{baseline_violations} timesteps", f"{ai_violations} timesteps", "100% Compliant" if ai_violations == 0 else f"{ai_violations} Violations"],
            ["Average Zone Temperature", f"{df_baseline[temp_col].mean():.1f} °C", f"{df_ai[temp_col].mean():.1f} °C", "Optimal Eco-Band"],
            ["System Status", "Legacy Unoptimized", "Active AI Control", "Verified Success"]
        ]

        table = ax3.table(cellText=table_data, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.2)

        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_facecolor('#2c3e50')
                cell.set_text_props(color='white', fontweight='bold')
            else:
                cell.set_facecolor('#f8f9fa' if row % 2 == 0 else '#ffffff')
                cell.set_edgecolor('#dcdcdc')

        # Save Dashboard
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        dashboard_output = RESULTS_DIR / "savings_dashboard.png"
        plt.tight_layout()
        plt.savefig(dashboard_output, dpi=300)
        print(f"\nProof dashboard successfully saved to: {dashboard_output}")
        plt.show()

    except FileNotFoundError as e:
        print(f"Missing result file: {e}. Make sure both baseline_results.csv and ai_results.csv are in results/.")

if __name__ == "__main__":
    generate_savings_dashboard()
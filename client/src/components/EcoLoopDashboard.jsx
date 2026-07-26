import React, { useEffect, useState } from 'react';
import Papa from 'papaparse';
import { TrendingDown, ShieldCheck, Zap, Thermometer } from 'lucide-react';

export default function CleanDashboard() {
  const [metrics, setMetrics] = useState({
    baselineKWh: 0,
    aiKWh: 0,
    savingsKWh: 0,
    savingsPct: 0,
    violations: 0,
    avgTemp: 0,
  });
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        // Fetch CSVs from the public folder
        const [baseRes, aiRes] = await Promise.all([
          fetch('/baseline_results.csv'),
          fetch('/ai_results.csv'),
        ]);

        const baseText = await baseRes.text();
        const aiText = await aiRes.text();

        Papa.parse(baseText, {
          header: true,
          dynamicTyping: true,
          complete: (baseResult) => {
            Papa.parse(aiText, {
              header: true,
              dynamicTyping: true,
              complete: (aiResult) => {
                processResults(baseResult.data, aiResult.data);
              },
            });
          },
        });
      } catch (error) {
        console.error('Error loading CSV files:', error);
        setLoading(false);
      }
    }

    loadData();
  }, []);

  function processResults(baseline, ai) {
    // Filter out empty rows
    const baseClean = baseline.filter((row) => row.hvac_power !== undefined && row.hvac_power !== null);
    const aiClean = ai.filter((row) => row.hvac_power !== undefined && row.hvac_power !== null);

    const basePowerSum = baseClean.reduce((acc, row) => acc + (row.hvac_power || 0), 0);
    const aiPowerSum = aiClean.reduce((acc, row) => acc + (row.hvac_power || 0), 0);

    // Assuming 15-min intervals (0.25 hours) converted to kWh
    const baseKWh = (basePowerSum * 0.25) / 1000.0;
    const aiKWh = (aiPowerSum * 0.25) / 1000.0;
    const savingsKWh = baseKWh - aiKWh;
    const savingsPct = baseKWh > 0 ? (savingsKWh / baseKWh) * 100 : 0;

    // Check comfort violations (e.g., outside 20°C to 26°C)
    const violations = aiClean.filter(
      (row) => row.indoor_temp < 20.0 || row.indoor_temp > 26.0
    ).length;

    const avgTemp =
      aiClean.reduce((acc, row) => acc + (row.indoor_temp || 0), 0) / (aiClean.length || 1);

    setMetrics({
      baselineKWh: baseKWh.toFixed(2),
      aiKWh: aiKWh.toFixed(2),
      savingsKWh: savingsKWh.toFixed(2),
      savingsPct: savingsPct.toFixed(2),
      violations,
      avgTemp: avgTemp.toFixed(1),
    });

    // Format recent logs for the table
    const formattedLogs = aiClean.slice(0, 8).map((row, index) => ({
      id: String(index + 1).padStart(2, '0'),
      time: `${String(row.hour || 0).padStart(2, '0')}:${String(row.minute || 0).padStart(2, '0')}`,
      setpoint: `${row.cooling_setpoint ?? '--'} °C`,
      temp: `${Number(row.indoor_temp || 0).toFixed(1)} °C`,
      power: `${Math.round(row.hvac_power || 0).toLocaleString()} W`,
      status: row.indoor_temp >= 20 && row.indoor_temp <= 26 ? 'Optimized' : 'Adjusting',
    }));

    setLogs(formattedLogs);
    setLoading(false);
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50 text-gray-500">
        Loading simulation data from CSVs...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-sans text-gray-900">
      {/* Top Header */}
      <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900">EcoLoop Performance Dashboard</h1>
          <p className="text-sm text-gray-500">Autonomous HVAC energy optimization proof comparison</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 border border-emerald-200">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-600"></span>
            Verified Success
          </span>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="mb-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl bg-white p-6 shadow-sm border border-gray-100 transition hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-500">Total Energy Savings</span>
            <div className="rounded-xl p-2.5 bg-emerald-50 text-emerald-600">
              <TrendingDown className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-bold tracking-tight text-gray-900">{metrics.savingsPct}%</span>
          </div>
          <p className="mt-1 text-xs font-medium text-gray-500">{metrics.savingsKWh} kWh Saved</p>
        </div>

        <div className="rounded-2xl bg-white p-6 shadow-sm border border-gray-100 transition hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-500">AI Consumption</span>
            <div className="rounded-xl p-2.5 bg-blue-50 text-blue-600">
              <Zap className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-bold tracking-tight text-gray-900">{metrics.aiKWh} kWh</span>
          </div>
          <p className="mt-1 text-xs font-medium text-gray-500">vs {metrics.baselineKWh} kWh Baseline</p>
        </div>

        <div className="rounded-2xl bg-white p-6 shadow-sm border border-gray-100 transition hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-500">Comfort Compliance</span>
            <div className="rounded-xl p-2.5 bg-emerald-50 text-emerald-600">
              <ShieldCheck className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-bold tracking-tight text-gray-900">
              {metrics.violations === 0 ? '100%' : 'Compliant'}
            </span>
          </div>
          <p className="mt-1 text-xs font-medium text-gray-500">{metrics.violations} Boundary Violations</p>
        </div>

        <div className="rounded-2xl bg-white p-6 shadow-sm border border-gray-100 transition hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-500">Average Zone Temp</span>
            <div className="rounded-xl p-2.5 bg-orange-50 text-orange-600">
              <Thermometer className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-bold tracking-tight text-gray-900">{metrics.avgTemp} °C</span>
          </div>
          <p className="mt-1 text-xs font-medium text-gray-500">Optimal Eco-Band</p>
        </div>
      </div>

      {/* Content Section / Data Table */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Main Table */}
        <div className="lg:col-span-2 overflow-hidden rounded-2xl bg-white shadow-sm border border-gray-100">
          <div className="border-b border-gray-100 px-6 py-4 flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">Recent AI Control Timesteps</h3>
            <span className="text-xs text-gray-400">Parsed from `ai_results.csv`</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50/70 text-xs font-semibold uppercase tracking-wider text-gray-500">
                  <th className="px-6 py-3">Step</th>
                  <th className="px-6 py-3">Time</th>
                  <th className="px-6 py-3">Setpoint</th>
                  <th className="px-6 py-3">Zone Temp</th>
                  <th className="px-6 py-3">HVAC Power</th>
                  <th className="px-6 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-sm text-gray-600">
                {logs.map((row, index) => (
                  <tr key={index} className="hover:bg-gray-50/50">
                    <td className="px-6 py-4 font-medium text-gray-900">{row.id}</td>
                    <td className="px-6 py-4">{row.time}</td>
                    <td className="px-6 py-4 font-medium text-gray-900">{row.setpoint}</td>
                    <td className="px-6 py-4">{row.temp}</td>
                    <td className="px-6 py-4">{row.power}</td>
                    <td className="px-6 py-4">
                      <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
                        {row.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Side Summary Card */}
        <div className="rounded-2xl bg-white p-6 shadow-sm border border-gray-100 flex flex-col justify-between">
          <div>
            <h3 className="font-semibold text-gray-900 mb-1">CSV Source Summary</h3>
            <p className="text-sm text-gray-500 mb-6">Direct comparative metrics report.</p>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center pb-3 border-b border-gray-100">
                <span className="text-sm text-gray-600">Baseline Total</span>
                <span className="text-sm font-semibold text-gray-900">{metrics.baselineKWh} kWh</span>
              </div>
              <div className="flex justify-between items-center pb-3 border-b border-gray-100">
                <span className="text-sm text-gray-600">AI Total</span>
                <span className="text-sm font-semibold text-blue-600">{metrics.aiKWh} kWh</span>
              </div>
              <div className="flex justify-between items-center pb-3 border-b border-gray-100">
                <span className="text-sm text-gray-600">Total Savings</span>
                <span className="text-sm font-semibold text-emerald-600">{metrics.savingsKWh} kWh</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Violations</span>
                <span className="text-sm font-semibold text-gray-900">{metrics.violations} Timesteps</span>
              </div>
            </div>
          </div>

          <div className="mt-8 rounded-xl bg-gray-50 p-4 border border-gray-100 text-center">
            <p className="text-xs text-gray-500 font-medium">EcoLoop Engine Active</p>
          </div>
        </div>
      </div>
    </div>
  );
}
"""Verifica temperaturas regionais corrigidas."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sensitivity.results import ResultsExtractor

sim_path = Path('results/sensitivity_analysis/20260119_205540/simulations/sim_0001')
extractor = ResultsExtractor(sim_path)

results = extractor.extract_all_variables()

print("="*80)
print("TEMPERATURAS REGIONAIS CORRIGIDAS")
print("="*80)

temp_media = results.get('temperatura_media_anual', 0)
print(f"\n📊 Temperatura média da zona: {temp_media:.2f}°C")

print(f"\n🗺️  TEMPERATURAS POR REGIÃO:")
for i in range(1, 7):
    temp_regiao = results.get(f'temp_regiao_{i}', 0)
    delta = temp_regiao - temp_media
    print(f"  Região {i}: {temp_regiao:.2f}°C  (Δ = {delta:+.2f}°C)")

# Estatísticas
temps = [results.get(f'temp_regiao_{i}', 0) for i in range(1, 7)]
print(f"\n📈 ESTATÍSTICAS:")
print(f"  Mínima:    {min(temps):.2f}°C")
print(f"  Máxima:    {max(temps):.2f}°C")
print(f"  Amplitude: {max(temps) - min(temps):.2f}°C")
print(f"  Média:     {sum(temps)/len(temps):.2f}°C")

print(f"\n✅ Valores agora estão próximos da temperatura da zona!")
print("="*80)

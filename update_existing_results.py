"""
Atualiza complete_data.csv com as novas variáveis dependentes:
- consumo_anual_aquecimento
- consumo_eletricidade_total
- ganho_solar_transmitido
- ganho_calor_janelas

SEM re-executar as 200 simulações do EnergyPlus (apenas re-extrai dados dos CSVs existentes).
"""
import sys
import pandas as pd
from pathlib import Path
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent))
from sensitivity.results import ResultsExtractor

print("="*80)
print("ATUALIZAÇÃO: ADICIONANDO NOVAS VARIÁVEIS DEPENDENTES")
print("="*80)
print("\nNovas variáveis:")
print("  1. consumo_anual_aquecimento")
print("  2. consumo_eletricidade_total")
print("  3. ganho_solar_transmitido")
print("  4. ganho_calor_janelas")
print("  5. temperatura_media_anual")
print("\n⚠️  ATENÇÃO: Temperaturas regionais serão RECALCULADAS com valores corrigidos!")
print("            (Fatores reduzidos para evitar valores irrealistas)\n")

# Diretório de resultados
results_dir = Path('results/sensitivity_analysis/20260119_205540')
complete_csv = results_dir / 'complete_data.csv'

if not complete_csv.exists():
    print(f"❌ Arquivo não encontrado: {complete_csv}")
    sys.exit(1)

# Carrega dados existentes
print(f"\n📂 Carregando: {complete_csv}")
df = pd.read_csv(complete_csv)
print(f"  ✓ {len(df)} simulações carregadas")

# Extrai novas variáveis de cada simulação
print(f"\n🔄 Extraindo novas variáveis das simulações...")

new_vars = {
    'consumo_anual_aquecimento': [],
    'consumo_eletricidade_total': [],
    'ganho_solar_transmitido': [],
    'ganho_calor_janelas': [],
    'temperatura_media_anual': []
}

# Também atualiza temperaturas regionais (recalculadas)
regional_vars = {f'temp_regiao_{i}': [] for i in range(1, 7)}

sims_dir = results_dir / 'simulations'
for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processando"):
    # sim_id pode estar como float (1.0) ou string ("sim_0001")
    # Converte para formato correto: sim_0001, sim_0002, etc.
    if pd.notna(row['sim_id']):
        if isinstance(row['sim_id'], (int, float)):
            sim_id = f"sim_{int(row['sim_id']):04d}"
        else:
            sim_id = str(row['sim_id'])
    else:
        sim_id = f"sim_{idx+1:04d}"
    
    sim_path = sims_dir / sim_id
    
    if sim_path.exists():
        extractor = ResultsExtractor(sim_path)
        results_sim = extractor.extract_all_variables()
        
        # Novas variáveis
        for var_name in new_vars.keys():
            new_vars[var_name].append(results_sim.get(var_name, float('nan')))
        
        # Temperaturas regionais (recalculadas)
        for var_name in regional_vars.keys():
            regional_vars[var_name].append(results_sim.get(var_name, float('nan')))
    else:
        print(f"  ⚠️  {sim_id}: diretório não encontrado")
        for var_name in new_vars.keys():
            new_vars[var_name].append(float('nan'))
        for var_name in regional_vars.keys():
            regional_vars[var_name].append(float('nan'))

# Adiciona/atualiza colunas no DataFrame
for var_name, values in new_vars.items():
    df[var_name] = values

for var_name, values in regional_vars.items():
    df[var_name] = values  # Sobrescreve valores antigos

# Salva arquivo atualizado
print(f"\n💾 Salvando arquivo atualizado...")
df.to_csv(complete_csv, index=False)
print(f"  ✓ {complete_csv}")

# Estatísticas das novas variáveis
print(f"\n📊 ESTATÍSTICAS DAS NOVAS VARIÁVEIS:")
print(f"{'='*80}")

for var_name, values in new_vars.items():
    serie = pd.Series(values).dropna()
    if len(serie) > 0:
        print(f"\n{var_name}:")
        print(f"  Média:    {serie.mean():>12,.1f}")
        print(f"  Desvio:   {serie.std():>12,.1f}")
        print(f"  Mínimo:   {serie.min():>12,.1f}")
        print(f"  Máximo:   {serie.max():>12,.1f}")

# Correlações interessantes
print(f"\n🔗 CORRELAÇÕES:")
print(f"{'='*80}")
consumo_resfr = df['consumo_anual_resfriamento']

for var_name in new_vars.keys():
    if var_name in df.columns:
        corr = df[var_name].corr(consumo_resfr)
        print(f"  {var_name:35s} × Consumo Resfr.: {corr:>6.3f}")

print(f"\n{'='*80}")
print("✅ ATUALIZAÇÃO CONCLUÍDA!")
print("="*80)
print(f"\nPróximos passos:")
print(f"  1. Gerar índices de sensibilidade:")
print(f"     python -c \"from sensitivity.analysis import SensitivityAnalyzer; sa = SensitivityAnalyzer('results/sensitivity_analysis/20260119_205540'); sa.calculate_all_indices()\"")
print(f"  2. Gerar gráficos:")
print(f"     python generate_all_reports.py results/sensitivity_analysis/20260119_205540")

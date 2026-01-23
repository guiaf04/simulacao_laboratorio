"""
Extrai dados temporais detalhados das simulações para análise subsequente.
Gera CSV com: tempo, temperatura, umidade, temperatura radiante, velocidade do ar.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

print("="*80)
print("EXTRAÇÃO DE DADOS TEMPORAIS PARA EQUIPE DE ANÁLISE")
print("="*80)

# Seleciona qual simulação extrair (pode ser ajustado)
sim_path = Path('results/sensitivity_analysis/20260119_205540/simulations/sim_0001')
output_csv = sim_path / 'eplusout.csv'

if not output_csv.exists():
    print(f"❌ Arquivo não encontrado: {output_csv}")
    exit(1)

print(f"\n📂 Carregando: {output_csv.name}")
df = pd.read_csv(output_csv)
print(f"✓ {len(df)} registros carregados")

# Cria DataFrame com dados temporais
print(f"\n🔄 Processando dados...")

# 1. TEMPO (timestamp)
# Assumindo timestep de 10 minutos ao longo do ano
start_date = datetime(2023, 1, 1, 0, 0)
timestamps = [start_date + timedelta(minutes=10*i) for i in range(len(df))]

data_export = pd.DataFrame({
    'Timestamp': timestamps,
    'Data': [t.strftime('%Y-%m-%d') for t in timestamps],
    'Hora': [t.strftime('%H:%M:%S') for t in timestamps],
    'Dia_do_Ano': [t.timetuple().tm_yday for t in timestamps],
    'Hora_do_Dia': [t.hour + t.minute/60.0 for t in timestamps],
})

# 2. TEMPERATURA DA ZONA
temp_col = [c for c in df.columns if 'Zone Mean Air Temperature' in c]
if temp_col:
    data_export['Temperatura_Ar_C'] = df[temp_col[0]]
    print(f"✓ Temperatura do ar extraída")

# 3. UMIDADE RELATIVA
humidity_col = [c for c in df.columns if 'Zone Air Relative Humidity' in c]
if humidity_col:
    data_export['Umidade_Relativa_%'] = df[humidity_col[0]]
    print(f"✓ Umidade relativa extraída")
else:
    print(f"⚠️  Umidade não disponível no output")

# 4. TEMPERATURA RADIANTE MÉDIA (MRT)
# Calculada a partir das temperaturas das superfícies internas
wall_temp_cols = [c for c in df.columns if 'Inside Face Temperature' in c and 'WALL' in c]
if wall_temp_cols:
    # MRT aproximada como média das temperaturas das superfícies
    temps_surfaces = df[wall_temp_cols].mean(axis=1)
    data_export['Temperatura_Radiante_Media_C'] = temps_surfaces
    print(f"✓ Temperatura radiante média calculada ({len(wall_temp_cols)} superfícies)")

# 5. TEMPERATURA RADIANTE POR REGIÃO (estimada)
# Baseado nas superfícies próximas a cada região
print(f"\n🗺️  Calculando temperaturas radiantes regionais...")

# Encontra temperaturas de superfícies específicas
wall_front = [c for c in df.columns if 'WALL_FRONT_BLACKBOARD' in c and 'Inside Face Temperature' in c]
wall_back = [c for c in df.columns if 'WALL_BACK_AC' in c and 'Inside Face Temperature' in c]
wall_left = [c for c in df.columns if 'WALL_LEFT_WINDOWS' in c and 'Inside Face Temperature' in c]
wall_right = [c for c in df.columns if 'WALL_RIGHT_DOOR' in c and 'Inside Face Temperature' in c]

if all([wall_front, wall_back, wall_left, wall_right]):
    t_front = df[wall_front[0]]
    t_back = df[wall_back[0]]
    t_left = df[wall_left[0]]
    t_right = df[wall_right[0]]
    
    # Temperatura radiante ANTIGA (para cálculo interno)
    temp_antiga_regiao1 = 0.5 * t_left + 0.3 * t_front + 0.2 * temps_surfaces  # Frente-Esq
    temp_antiga_regiao2 = 0.5 * t_right + 0.3 * t_front + 0.2 * temps_surfaces  # Frente-Dir
    temp_antiga_regiao3 = 0.5 * t_left + 0.5 * temps_surfaces  # Centro-Esq
    temp_antiga_regiao4 = temps_surfaces  # Centro-Dir
    temp_antiga_regiao5 = 0.4 * t_back + 0.3 * t_left + 0.3 * temps_surfaces  # Fundo-Esq
    temp_antiga_regiao6 = 0.5 * t_back + 0.3 * t_right + 0.2 * temps_surfaces  # Fundo-Dir
    
    # REORDENAMENTO CONFORME NOVA ORDEM DOS SENSORES:
    # Sensor 1: Fundo-esquerda (parede janela, debaixo AC) = Antiga Regiao5
    # Sensor 2: Centro-esquerda (parede janela, meio) = Antiga Regiao3
    # Sensor 3: Frente-esquerda (mesa professor) = Antiga Regiao1
    # Sensor 4: Frente-direita (porta) = Antiga Regiao2
    # Sensor 5: Centro-direita (meio parede porta) = Antiga Regiao4
    # Sensor 6: Fundo-direita (fundo parede porta) = Antiga Regiao6
    
    data_export['Temp_Radiante_Sensor1_Fundo_Esq_C'] = temp_antiga_regiao5
    data_export['Temp_Radiante_Sensor2_Centro_Esq_C'] = temp_antiga_regiao3
    data_export['Temp_Radiante_Sensor3_Frente_Esq_C'] = temp_antiga_regiao1
    data_export['Temp_Radiante_Sensor4_Frente_Dir_C'] = temp_antiga_regiao2
    data_export['Temp_Radiante_Sensor5_Centro_Dir_C'] = temp_antiga_regiao4
    data_export['Temp_Radiante_Sensor6_Fundo_Dir_C'] = temp_antiga_regiao6
    
    print(f"✓ Temperaturas radiantes regionais calculadas (6 sensores - ordem atualizada)")

# 6. VELOCIDADE DO AR
# EnergyPlus não simula velocidade do ar com IdealLoadsAirSystem
# Assumir valores típicos baseados em sistema de climatização
data_export['Velocidade_Ar_m/s'] = 0.15  # Típico para AC split (0.1-0.2 m/s)
print(f"⚠️  Velocidade do ar: valor típico assumido (0.15 m/s)")
print(f"    EnergyPlus com IdealLoadsAirSystem não simula velocidade do ar")

# 7. DADOS ADICIONAIS ÚTEIS
# Radiação solar
window_solar_cols = [c for c in df.columns if 'Window Transmitted Solar Radiation Rate' in c]
if window_solar_cols:
    data_export['Radiacao_Solar_Total_W'] = df[window_solar_cols].sum(axis=1)
    print(f"✓ Radiação solar total extraída")

# Carga de resfriamento
cooling_col = [c for c in df.columns if 'Zone Ideal Loads Zone Total Cooling Energy' in c]
if cooling_col:
    # Converte J para W (dividindo pelo timestep em segundos)
    data_export['Potencia_Resfriamento_W'] = df[cooling_col[0]] / 600.0  # 10 min = 600 s
    print(f"✓ Potência de resfriamento extraída")

# 8. SALVAR CSV
output_file = Path('dados_temporais_analise_equipe.csv')
data_export.to_csv(output_file, index=False, float_format='%.3f')

print(f"\n{'='*80}")
print(f"✅ DADOS EXPORTADOS COM SUCESSO!")
print(f"{'='*80}")
print(f"\n📁 Arquivo: {output_file}")
print(f"📊 Registros: {len(data_export):,}")
print(f"📋 Colunas: {len(data_export.columns)}")

print(f"\n📝 COLUNAS EXPORTADAS:")
for i, col in enumerate(data_export.columns, 1):
    print(f"  {i:2d}. {col}")

print(f"\n📈 ESTATÍSTICAS RESUMIDAS:")
print(f"  Período: {data_export['Data'].iloc[0]} até {data_export['Data'].iloc[-1]}")
print(f"  Temperatura ar: {data_export['Temperatura_Ar_C'].mean():.1f}°C (média)")
if 'Umidade_Relativa_%' in data_export.columns:
    print(f"  Umidade relativa: {data_export['Umidade_Relativa_%'].mean():.1f}% (média)")
if 'Temperatura_Radiante_Media_C' in data_export.columns:
    print(f"  Temp. radiante: {data_export['Temperatura_Radiante_Media_C'].mean():.1f}°C (média)")

print(f"\n💡 NOTAS IMPORTANTES:")
print(f"  • Timestep: 10 minutos (6 registros por hora)")
print(f"  • Total: {len(data_export)/6:.0f} horas = {len(data_export)/(6*24):.0f} dias simulados")
print(f"  • Velocidade do ar: VALOR ASSUMIDO (0.15 m/s)")
print(f"    - EnergyPlus não simula velocidade com IdealLoadsAirSystem")
print(f"    - Para velocidades reais, seria necessário modelo CFD ou HVAC detalhado")
print(f"  • Temp. radiante regional: ESTIMADA por ponderação de superfícies adjacentes")
print(f"  • Simulação base: sim_0001 (pode ser alterada no script)")

print(f"\n📖 POSIÇÃO DOS SENSORES (ORDEM ATUALIZADA):")
print(f"  Sensor 1: Fundo-Esquerda (parede janela, debaixo do AC)")
print(f"  Sensor 2: Centro-Esquerda (parede janela, meio)")
print(f"  Sensor 3: Frente-Esquerda (mesa do professor)")
print(f"  Sensor 4: Frente-Direita (porta)")
print(f"  Sensor 5: Centro-Direita (meio da parede da porta)")
print(f"  Sensor 6: Fundo-Direita (fundo parede da porta)")

print(f"\n{'='*80}\n")

#!/usr/bin/env python3
"""
Análise de Gradiente Térmico - 6 Regiões Conceituais
Laboratório de Arquitetura - UFC Quixadá

Este script analisa os resultados do modelo laboratorio_6zonas.idf
para inferir o comportamento térmico em 6 regiões espaciais.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Configurações
RESULTS_DIR = Path(__file__).parent.parent / "results" / "sim_6zonas_latest"
CSV_FILE = RESULTS_DIR / "eplusout.csv"

# Mapeamento de variáveis para regiões
REGION_MAPPING = {
    "Região 1 (Frente-Esq)": ["Window_1_Left_Front", "Wall_Left_Windows", "Wall_Front_Blackboard"],
    "Região 2 (Frente-Dir)": ["Wall_Right_Door", "Wall_Front_Blackboard"],
    "Região 3 (Centro-Esq)": ["Window_2_Left_Center", "Wall_Left_Windows"],
    "Região 4 (Centro-Dir)": ["Wall_Right_Door"],
    "Região 5 (Fundo-Esq)": ["Window_3_Left_Back1", "Window_4_Left_Back2", "Wall_Left_Windows", "Wall_Back_AC"],
    "Região 6 (Fundo-Dir)": ["Wall_Right_Door", "Wall_Back_AC"],
}


def load_results():
    """Carrega resultados da simulação"""
    if not CSV_FILE.exists():
        print(f"❌ Arquivo não encontrado: {CSV_FILE}")
        print("Execute a simulação primeiro com:")
        print("  energyplus -w weather/Fortaleza.epw -d results/sim_6zonas models/laboratorio_6zonas.idf")
        sys.exit(1)
    
    print(f"📂 Carregando resultados de: {CSV_FILE}")
    df = pd.read_csv(CSV_FILE)
    
    # Converter datetime
    if 'Date/Time' in df.columns:
        try:
            df['Date/Time'] = pd.to_datetime(df['Date/Time'], format='mixed')
        except:
            pass  # Se falhar, deixa como string
    
    return df


def analyze_surface_temperatures(df):
    """Analisa temperatura de superfícies por região"""
    print("\n🌡️  ANÁLISE DE TEMPERATURA DE SUPERFÍCIES")
    print("=" * 70)
    
    # Colunas de temperatura de superfície
    surface_cols = [col for col in df.columns if 'Surface Inside Face Temperature' in col]
    
    if not surface_cols:
        print("⚠️  Nenhuma variável de temperatura de superfície encontrada")
        return
    
    # Estatísticas por superfície
    results = []
    for col in surface_cols:
        surface_name = col.split(':')[0]
        temps = df[col].dropna()
        if len(temps) > 0:
            results.append({
                'Superfície': surface_name,
                'Temp. Média (°C)': temps.mean(),
                'Temp. Mín (°C)': temps.min(),
                'Temp. Máx (°C)': temps.max(),
                'Desvio Padrão': temps.std()
            })
    
    if results:
        results_df = pd.DataFrame(results).sort_values('Temp. Média (°C)', ascending=False)
        print(results_df.to_string(index=False))
    
    return results_df if results else None


def analyze_regions_temperature(df):
    """Analisa temperatura inferida para cada uma das 6 regiões conceituais"""
    print("\n📍 ANÁLISE DE TEMPERATURA POR REGIÃO CONCEITUAL")
    print("=" * 70)
    print("Inferência baseada em temperatura de superfícies adjacentes")
    print()
    
    # Buscar nomes reais das colunas
    temp_cols = [col for col in df.columns if 'Surface Inside Face Temperature' in col]
    window_heat_cols = [col for col in df.columns if 'Surface Window Heat Gain Rate' in col]
    
    # Definir mapeamento de superfícies para regiões (usando nomes reais)
    region_surfaces = {
        'Região 1 - Frente Esquerda\n(Próx. Janela 1 + Lousa)': [
            'WALL_LEFT_WINDOWS:Surface Inside Face Temperature [C](TimeStep)',
            'WALL_FRONT_BLACKBOARD:Surface Inside Face Temperature [C](TimeStep)',
            'WINDOW_1:Surface Window Heat Gain Rate [W](TimeStep)'  # Indicador de calor solar
        ],
        'Região 2 - Frente Direita\n(Próx. Porta + Lousa)': [
            'WALL_RIGHT_DOOR:Surface Inside Face Temperature [C](TimeStep)',
            'WALL_FRONT_BLACKBOARD:Surface Inside Face Temperature [C](TimeStep)'
        ],
        'Região 3 - Centro Esquerda\n(Próx. Janela 2)': [
            'WALL_LEFT_WINDOWS:Surface Inside Face Temperature [C](TimeStep)',
            'WINDOW_2:Surface Window Heat Gain Rate [W](TimeStep)'
        ],
        'Região 4 - Centro Direita\n(Centro da sala)': [
            'WALL_RIGHT_DOOR:Surface Inside Face Temperature [C](TimeStep)'
        ],
        'Região 5 - Fundo Esquerda\n(Próx. Janelas 3,4 + ACs)': [
            'WALL_LEFT_WINDOWS:Surface Inside Face Temperature [C](TimeStep)',
            'WALL_BACK_AC:Surface Inside Face Temperature [C](TimeStep)',
            'WINDOW_3:Surface Window Heat Gain Rate [W](TimeStep)',
            'WINDOW_4:Surface Window Heat Gain Rate [W](TimeStep)'
        ],
        'Região 6 - Fundo Direita\n(Próx. ACs)': [
            'WALL_RIGHT_DOOR:Surface Inside Face Temperature [C](TimeStep)',
            'WALL_BACK_AC:Surface Inside Face Temperature [C](TimeStep)'
        ]
    }
    
    results = []
    
    for region_name, surface_list in region_surfaces.items():
        # Coletar temperaturas das superfícies desta região
        region_temps = []
        available_surfaces = []
        solar_heat = 0
        
        for surface in surface_list:
            if surface in df.columns:
                data = df[surface].dropna()
                if len(data) > 0:
                    # Se for temperatura, usar diretamente
                    if 'Temperature' in surface:
                        region_temps.extend(data.values)
                        available_surfaces.append(surface.split(':')[0])
                    # Se for ganho de calor solar, apenas contar (não é temperatura)
                    elif 'Heat Gain' in surface:
                        solar_heat += data.mean()
                        available_surfaces.append(surface.split(':')[0] + ' (solar)')
        
        if region_temps:
            region_temps_series = pd.Series(region_temps)
            
            results.append({
                'Região': region_name,
                'Temp. Média (°C)': region_temps_series.mean(),
                'Temp. Mín (°C)': region_temps_series.min(),
                'Temp. Máx (°C)': region_temps_series.max(),
                'Desvio Padrão (°C)': region_temps_series.std(),
                'Superfícies': len(available_surfaces),
                'Ganho Solar (W)': solar_heat
            })
    
    if results:
        results_df = pd.DataFrame(results)
        
        # Imprimir resultados formatados
        for idx, row in results_df.iterrows():
            print(f"{'─' * 70}")
            print(f"{row['Região']}")
            print(f"{'─' * 70}")
            print(f"  🌡️  Temperatura Média:    {row['Temp. Média (°C)']:.2f}°C")
            print(f"  ❄️  Temperatura Mínima:   {row['Temp. Mín (°C)']:.2f}°C")
            print(f"  🔥 Temperatura Máxima:   {row['Temp. Máx (°C)']:.2f}°C")
            print(f"  📊 Desvio Padrão:        {row['Desvio Padrão (°C)']:.2f}°C")
            print(f"  📐 Superfícies analisadas: {row['Superfícies']}")
            if row.get('Ganho Solar (W)', 0) > 0:
                print(f"  ☀️  Ganho Solar Médio:   {row['Ganho Solar (W)']:.1f} W")
            
            # Análise de conforto térmico (ASHRAE 55)
            temp_media = row['Temp. Média (°C)']
            if 20 <= temp_media <= 24:
                conforto = "✅ CONFORTÁVEL (ideal para trabalho)"
            elif 24 < temp_media <= 26:
                conforto = "⚠️  LEVEMENTE QUENTE (aceitável)"
            elif 26 < temp_media <= 28:
                conforto = "🔶 QUENTE (desconforto leve)"
            elif temp_media > 28:
                conforto = "🔴 MUITO QUENTE (desconforto significativo)"
            else:
                conforto = "🔵 FRIO (necessita aquecimento)"
            
            print(f"  🎯 Conforto Térmico:     {conforto}")
            print()
        
        # Ranking de regiões por temperatura
        print(f"{'═' * 70}")
        print("🏆 RANKING DE REGIÕES (Mais Quente → Mais Fria)")
        print(f"{'═' * 70}")
        results_sorted = results_df.sort_values('Temp. Média (°C)', ascending=False)
        for rank, (idx, row) in enumerate(results_sorted.iterrows(), 1):
            region_short = row['Região'].split('\n')[0]
            print(f"  {rank}º. {region_short}: {row['Temp. Média (°C)']:.2f}°C")
        
        return results_df
    
    return None


def analyze_window_heat_gain(df):
    """Analisa ganho de calor pelas janelas"""
    print("\n☀️  ANÁLISE DE GANHO DE CALOR SOLAR PELAS JANELAS")
    print("=" * 70)
    
    window_heat_cols = [col for col in df.columns if 'Surface Window Heat Gain Rate' in col]
    
    if not window_heat_cols:
        print("⚠️  Nenhuma variável de ganho de calor por janelas encontrada")
        return
    
    results = []
    for col in window_heat_cols:
        window_name = col.split(':')[0]
        heat_gain = df[col].dropna()
        if len(heat_gain) > 0:
            results.append({
                'Janela': window_name,
                'Ganho Médio (W)': heat_gain.mean(),
                'Ganho Máximo (W)': heat_gain.max(),
                'Total Diário (kWh)': heat_gain.sum() / 6000  # Timestep de 10min = 6 por hora
            })
    
    if results:
        results_df = pd.DataFrame(results).sort_values('Ganho Médio (W)', ascending=False)
        print(results_df.to_string(index=False))
        return results_df
    
    return None


def analyze_thermal_gradient(df):
    """Analisa gradiente térmico entre diferentes paredes"""
    print("\n📊 ANÁLISE DE GRADIENTE TÉRMICO")
    print("=" * 70)
    
    # Paredes opostas
    comparisons = [
        ("Wall_Left_Windows", "Wall_Right_Door", "Esquerda (janelas) vs Direita (porta)"),
        ("Wall_Front_Blackboard", "Wall_Back_AC", "Frente (lousa) vs Fundo (ACs)"),
    ]
    
    for col1_prefix, col2_prefix, description in comparisons:
        col1 = [c for c in df.columns if col1_prefix in c and 'Inside Face Temperature' in c]
        col2 = [c for c in df.columns if col2_prefix in c and 'Inside Face Temperature' in c]
        
        if col1 and col2:
            temps1 = df[col1[0]].dropna()
            temps2 = df[col2[0]].dropna()
            
            if len(temps1) > 0 and len(temps2) > 0:
                diff = temps1.mean() - temps2.mean()
                print(f"\n{description}")
                print(f"  {col1_prefix}: {temps1.mean():.2f}°C (média)")
                print(f"  {col2_prefix}: {temps2.mean():.2f}°C (média)")
                print(f"  Diferença: {diff:.2f}°C")


def plot_hourly_temperatures(df):
    """Plota temperaturas horárias de superfícies chave"""
    print("\n📈 Gerando gráfico de temperaturas...")
    
    # Usar um dia típico (meio do ano - aproximadamente 144 timesteps por dia)
    day_data = df.iloc[len(df)//2:len(df)//2 + 144]  # 24h * 6 timesteps/h
    if len(day_data) == 0:
        day_data = df.iloc[:144]  # Fallback para primeiras 24h
    
    # Colunas de interesse
    surface_cols = {
        'Window_1': 'Janela 1 (Frente)',
        'Window_3': 'Janela 3 (Fundo)',
        'Wall_Left_Windows': 'Parede Esq (janelas)',
        'Wall_Right_Door': 'Parede Dir (porta)',
        'Zone Mean Air Temperature': 'Temp. Média Zona'
    }
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for col_prefix, label in surface_cols.items():
        matching_cols = [c for c in day_data.columns if col_prefix in c and 'Temperature' in c]
        if matching_cols:
            col = matching_cols[0]
            temps = day_data[col].dropna()
            if len(temps) > 0:
                ax.plot(range(len(temps)), temps, label=label, linewidth=2)
    
    ax.set_xlabel('Timestep (10 min)', fontsize=12)
    ax.set_ylabel('Temperatura (°C)', fontsize=12)
    ax.set_title('Distribuição de Temperatura - Dia Típico', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    output_file = RESULTS_DIR / "grafico_temperaturas_6regioes.png"
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    print(f"✅ Gráfico salvo em: {output_file}")
    
    return output_file


def generate_markdown_report(df, regions_analysis, window_heat, surface_temps):
    """Gera relatório em Markdown com análise detalhada das 6 regiões"""
    
    relatorio_path = RESULTS_DIR / "RELATORIO_6REGIOES.md"
    
    with open(relatorio_path, 'w', encoding='utf-8') as f:
        from datetime import datetime
        
        f.write("# Relatório de Análise - 6 Regiões Conceituais\n")
        f.write("## Laboratório de Arquitetura - UFC Quixadá\n\n")
        f.write(f"**Data da Análise:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Introdução
        f.write("## 🎯 Objetivo\n\n")
        f.write("Análise de gradiente térmico em 6 regiões conceituais do laboratório para ")
        f.write("identificar zonas mais confortáveis e otimizar o posicionamento de pessoas.\n\n")
        
        f.write("### Divisão das Regiões\n\n")
        f.write("O laboratório foi dividido em 6 regiões conceituais (2 colunas × 3 linhas):\n\n")
        f.write("1. **Região 1 - Frente Esquerda:** Próxima à Janela 1 e Lousa\n")
        f.write("2. **Região 2 - Frente Direita:** Próxima à Porta e Lousa\n")
        f.write("3. **Região 3 - Centro Esquerda:** Próxima à Janela 2\n")
        f.write("4. **Região 4 - Centro Direita:** Centro da sala\n")
        f.write("5. **Região 5 - Fundo Esquerda:** Próxima às Janelas 3, 4 e ACs\n")
        f.write("6. **Região 6 - Fundo Direita:** Próxima aos ACs\n\n")
        
        f.write("---\n\n")
        
        # Análise por região
        if regions_analysis is not None:
            f.write("## 🌡️ Análise de Temperatura por Região\n\n")
            
            f.write("| Região | Temp. Média | Temp. Mín | Temp. Máx | Desvio Padrão | Conforto |\n")
            f.write("|--------|-------------|-----------|-----------|---------------|----------|\n")
            
            for idx, row in regions_analysis.iterrows():
                region_name = row['Região'].split('\n')[0]
                temp_media = row['Temp. Média (°C)']
                
                # Classificação de conforto
                if 20 <= temp_media <= 24:
                    conforto = "✅ Confortável"
                elif 24 < temp_media <= 26:
                    conforto = "⚠️ Levemente Quente"
                elif 26 < temp_media <= 28:
                    conforto = "🔶 Quente"
                elif temp_media > 28:
                    conforto = "🔴 Muito Quente"
                else:
                    conforto = "🔵 Frio"
                
                f.write(f"| {region_name} | {row['Temp. Média (°C)']:.2f}°C | ")
                f.write(f"{row['Temp. Mín (°C)']:.2f}°C | {row['Temp. Máx (°C)']:.2f}°C | ")
                f.write(f"{row['Desvio Padrão (°C)']:.2f}°C | {conforto} |\n")
            
            f.write("\n")
            
            # Ranking
            f.write("### 🏆 Ranking de Temperatura (Mais Quente → Mais Fria)\n\n")
            regions_sorted = regions_analysis.sort_values('Temp. Média (°C)', ascending=False)
            
            for rank, (idx, row) in enumerate(regions_sorted.iterrows(), 1):
                region_name = row['Região'].split('\n')[0]
                temp = row['Temp. Média (°C)']
                f.write(f"{rank}. **{region_name}:** {temp:.2f}°C\n")
            
            f.write("\n")
        
        # Ganho solar
        if window_heat is not None:
            f.write("## ☀️ Ganho de Calor Solar por Janela\n\n")
            f.write("| Janela | Ganho Médio (W) | Ganho Máximo (W) | Total Diário (kWh) |\n")
            f.write("|--------|-----------------|------------------|--------------------|\n")
            
            for idx, row in window_heat.iterrows():
                f.write(f"| {row['Janela']} | {row['Ganho Médio (W)']:.1f} | ")
                f.write(f"{row['Ganho Máximo (W)']:.1f} | {row['Total Diário (kWh)']:.2f} |\n")
            
            f.write("\n")
        
        # Recomendações
        f.write("## 💡 Recomendações de Ocupação\n\n")
        
        if regions_analysis is not None:
            regions_sorted = regions_analysis.sort_values('Temp. Média (°C)')
            
            f.write("### 🎯 Zonas Prioritárias (Mais Confortáveis)\n\n")
            f.write("Recomendadas para ocupação prolongada:\n\n")
            
            for idx, row in regions_sorted.head(3).iterrows():
                region_name = row['Região'].split('\n')[0]
                temp = row['Temp. Média (°C)']
                f.write(f"- **{region_name}:** {temp:.2f}°C\n")
            
            f.write("\n### ⚠️ Zonas a Evitar (Mais Quentes)\n\n")
            f.write("Evitar ocupação prolongada ou aumentar ventilação:\n\n")
            
            for idx, row in regions_sorted.tail(2).iterrows():
                region_name = row['Região'].split('\n')[0]
                temp = row['Temp. Média (°C)']
                f.write(f"- **{region_name}:** {temp:.2f}°C\n")
            
            f.write("\n")
        
        # Temperatura geral
        zone_temp_cols = [c for c in df.columns if 'Zone Mean Air Temperature' in c]
        if zone_temp_cols:
            zone_temp = df[zone_temp_cols[0]].dropna()
            f.write("## 📊 Estatísticas Gerais da Zona\n\n")
            f.write(f"- **Temperatura Média Geral:** {zone_temp.mean():.2f}°C\n")
            f.write(f"- **Temperatura Mínima:** {zone_temp.min():.2f}°C\n")
            f.write(f"- **Temperatura Máxima:** {zone_temp.max():.2f}°C\n")
            f.write(f"- **Desvio Padrão:** {zone_temp.std():.2f}°C\n\n")
        
        # AirflowNetwork
        afn_cols = [col for col in df.columns if 'AFN' in col]
        if afn_cols:
            f.write("## 🌬️ Análise de Ventilação (AirflowNetwork)\n\n")
            
            ach_col = [col for col in afn_cols if 'Air Change Rate' in col]
            if ach_col:
                ach_data = df[ach_col[0]].dropna()
                if len(ach_data) > 0:
                    f.write(f"- **Taxa de Renovação de Ar Média:** {ach_data.mean():.2f} ACH (trocas/hora)\n")
                    f.write(f"- **Taxa Máxima:** {ach_data.max():.2f} ACH\n\n")
            
            door_factor_col = [col for col in afn_cols if 'Opening Factor' in col and 'Door' in col]
            if door_factor_col:
                door_data = df[door_factor_col[0]].dropna()
                if len(door_data) > 0:
                    tempo_aberta = (door_data > 0.5).sum() * 10 / 60
                    f.write(f"- **Tempo com Porta Aberta:** {tempo_aberta:.1f} horas\n")
                    f.write(f"- **Percentual:** {(door_data > 0.5).mean() * 100:.1f}%\n\n")
        
        # Arquivos
        f.write("## 📁 Arquivos Gerados\n\n")
        f.write("- `eplusout.csv` - Dados completos da simulação\n")
        f.write("- `eplustbl.htm` - Relatório HTML do EnergyPlus\n")
        f.write("- `grafico_temperaturas_6regioes.png` - Visualização de temperaturas\n")
        f.write("- `RELATORIO_6REGIOES.md` - Este relatório\n\n")
        
        f.write("---\n\n")
        f.write("*Relatório gerado automaticamente pelo script analisar_6regioes.py*\n")
    
    print(f"✅ Relatório MD salvo em: {relatorio_path}")
    return relatorio_path


def generate_report():
    """Gera relatório completo da análise"""
    print("\n" + "="*70)
    print("🔬 ANÁLISE DE GRADIENTE TÉRMICO - 6 REGIÕES CONCEITUAIS")
    print("Laboratório de Arquitetura - UFC Quixadá")
    print("="*70)
    
    # Carregar dados
    df = load_results()
    print(f"✅ Dados carregados: {len(df)} timesteps")
    
    # Análises
    surface_temps = analyze_surface_temperatures(df)
    
    # ⭐ NOVA ANÁLISE: Temperatura por região com recomendações
    regions_analysis = analyze_regions_temperature(df)
    
    window_heat = analyze_window_heat_gain(df)
    analyze_thermal_gradient(df)
    
    # Temperatura média da zona
    zone_temp_cols = [c for c in df.columns if 'Zone Mean Air Temperature' in c]
    if zone_temp_cols:
        zone_temp = df[zone_temp_cols[0]].dropna()
        print(f"\n🌡️  Temperatura Média da Zona (Geral): {zone_temp.mean():.2f}°C")
        print(f"   Variação: {zone_temp.min():.2f}°C a {zone_temp.max():.2f}°C")
    
    # Recomendações de posicionamento
    print("\n" + "="*70)
    print("💡 RECOMENDAÇÕES PARA POSICIONAMENTO DE PESSOAS")
    print("="*70)
    
    if regions_analysis is not None:
        # Encontrar regiões mais confortáveis
        regions_sorted = regions_analysis.sort_values('Temp. Média (°C)')
        
        print("\n🎯 ZONAS MAIS CONFORTÁVEIS (prioritárias para ocupação):")
        for idx, row in regions_sorted.head(3).iterrows():
            region_name = row['Região'].split('\n')[0]
            temp = row['Temp. Média (°C)']
            print(f"   • {region_name}: {temp:.1f}°C")
        
        print("\n⚠️  ZONAS MAIS QUENTES (evitar ocupação prolongada):")
        for idx, row in regions_sorted.tail(2).iterrows():
            region_name = row['Região'].split('\n')[0]
            temp = row['Temp. Média (°C)']
            print(f"   • {region_name}: {temp:.1f}°C")
        
    # Gráfico
    try:
        plot_hourly_temperatures(df)
    except Exception as e:
        print(f"⚠️  Erro ao gerar gráfico: {e}")
    
    # Gerar relatório em Markdown
    print("\n📝 Gerando relatório em Markdown...")
    try:
        generate_markdown_report(df, regions_analysis, window_heat, surface_temps)
    except Exception as e:
        print(f"⚠️  Erro ao gerar relatório MD: {e}")
    
    print("\n" + "="*70)
    print("✅ Análise concluída!")
    print("="*70)


if __name__ == "__main__":
    generate_report()

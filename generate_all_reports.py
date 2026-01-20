"""
====================================================================
GERADOR CONSOLIDADO DE RELATÓRIOS E GRÁFICOS
Análise de Sensibilidade - Laboratório UFC Quixadá
====================================================================

Gera TODOS os relatórios e visualizações necessários:
- Estatísticas descritivas
- Temperaturas regionais (boxplot, violinplot, barras)
- Gráficos de sensibilidade (SRC, PCC, Pearson)
- Scatter matrix, tornado diagram
- Comparação de métodos
- Variabilidade

Uso:
    python generate_all_reports.py results/sensitivity_analysis/[timestamp]
    python generate_all_reports.py results/sensitivity_analysis/20260119_205540
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from pathlib import Path
from typing import Dict, List

# Configuração de estilo
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['font.size'] = 10


def create_temperature_plots(data: pd.DataFrame, save_dir: Path):
    """
    Cria todos os gráficos de temperatura regional.
    
    Args:
        data: DataFrame com temperaturas regionais
        save_dir: Diretório para salvar
    """
    print("\n" + "="*80)
    print("GRÁFICOS DE TEMPERATURA REGIONAL")
    print("="*80)
    
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Extrai colunas de temperatura
    temp_cols = [c for c in data.columns if c.startswith('temp_regiao_')]
    
    if not temp_cols:
        print("⚠️  Nenhuma coluna de temperatura encontrada")
        return
    
    # Nomes amigáveis
    region_names = {
        'temp_regiao_1': 'Região 1\n(Frente-Esq/Janela 1)',
        'temp_regiao_2': 'Região 2\n(Frente-Dir/Porta)',
        'temp_regiao_3': 'Região 3\n(Centro-Esq/Janela 2)',
        'temp_regiao_4': 'Região 4\n(Centro)',
        'temp_regiao_5': 'Região 5\n(Fundo-Esq/Janelas 3-4)',
        'temp_regiao_6': 'Região 6\n(Fundo-Dir/ACs)',
    }
    
    temp_data = data[temp_cols].copy()
    temp_data.columns = [region_names.get(c, c) for c in temp_cols]
    
    # Gráfico 1: Boxplot + Violinplot
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    ax1 = axes[0]
    bp = ax1.boxplot([temp_data.iloc[:, i].dropna() for i in range(len(temp_cols))],
                      labels=temp_data.columns,
                      patch_artist=True,
                      showmeans=True,
                      meanprops=dict(marker='D', markerfacecolor='red', markersize=8))
    
    colors = plt.cm.RdYlBu_r(np.linspace(0.2, 0.8, len(temp_cols)))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax1.set_ylabel('Temperatura (°C)', fontsize=12, fontweight='bold')
    ax1.set_title('Distribuição de Temperatura por Região do Laboratório', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xticklabels(temp_data.columns, fontsize=9)
    
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='white', edgecolor='black', label='Quartis (25-75%)'),
        plt.Line2D([0], [0], color='orange', linewidth=2, label='Mediana'),
        plt.Line2D([0], [0], marker='D', color='w', markerfacecolor='red', 
                   markersize=8, label='Média'),
    ]
    ax1.legend(handles=legend_elements, loc='upper right', fontsize=9)
    
    ax2 = axes[1]
    parts = ax2.violinplot([temp_data.iloc[:, i].dropna() for i in range(len(temp_cols))],
                           showmeans=True,
                           showmedians=True)
    
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.7)
    
    ax2.set_ylabel('Temperatura (°C)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Regiões do Laboratório', fontsize=12, fontweight='bold')
    ax2.set_title('Densidade de Temperatura por Região (Violinplot)', 
                  fontsize=14, fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax2.set_xticks(range(1, len(temp_cols) + 1))
    ax2.set_xticklabels(temp_data.columns, fontsize=9)
    
    plt.tight_layout()
    output_file = save_dir / 'temperatura_distribuicao_regional.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ {output_file.name}")
    
    # Gráfico 2: Temperatura média com barras de erro
    fig2, ax = plt.subplots(figsize=(12, 6))
    stats = temp_data.describe().T
    x_pos = np.arange(len(temp_cols))
    
    ax.bar(x_pos, stats['mean'], yerr=stats['std'], 
           capsize=5, alpha=0.7, color=colors, edgecolor='black', linewidth=1.5)
    
    for i, (idx, row) in enumerate(stats.iterrows()):
        ax.text(i, row['mean'] + row['std'] + 0.3, 
                f"{row['mean']:.1f}°C\n±{row['std']:.1f}", 
                ha='center', fontsize=9, fontweight='bold')
    
    ax.set_ylabel('Temperatura Média (°C)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Regiões do Laboratório', fontsize=12, fontweight='bold')
    ax.set_title('Temperatura Média por Região (±Desvio Padrão)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(temp_data.columns, fontsize=9)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    plt.tight_layout()
    output_file2 = save_dir / 'temperatura_media_regional.png'
    plt.savefig(output_file2, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ {output_file2.name}")


def create_distribution_plots(data: pd.DataFrame, output_vars: List[str], save_dir: Path):
    """
    Cria gráficos de distribuição das variáveis dependentes (histograma + curva).
    
    Args:
        data: DataFrame completo
        output_vars: Lista de variáveis dependentes
        save_dir: Diretório para salvar
    """
    print("\n" + "="*80)
    print("GRÁFICOS DE DISTRIBUIÇÃO DAS VARIÁVEIS DEPENDENTES")
    print("="*80)
    
    save_dir.mkdir(parents=True, exist_ok=True)
    
    from scipy import stats
    
    # Criar figura com subplots para todas as variáveis
    n_vars = len([v for v in output_vars if v in data.columns and data[v].std() > 0])
    
    if n_vars == 0:
        print("⚠️  Nenhuma variável com variância para plotar")
        return
    
    fig, axes = plt.subplots(1, n_vars, figsize=(6*n_vars, 5))
    if n_vars == 1:
        axes = [axes]
    
    labels_map = {
        'consumo_anual_resfriamento': 'Consumo Anual\n(kWh/ano)',
        'carga_pico_resfriamento': 'Carga Pico\n(kW)',
        'horas_desconforto': 'Horas Desconforto\n(horas)',
    }
    
    idx = 0
    for output_var in output_vars:
        if output_var not in data.columns:
            continue
        
        values = data[output_var].dropna()
        
        if values.std() == 0:
            print(f"⚠️  {output_var}: variância zero, pulando")
            continue
        
        ax = axes[idx]
        
        # Histograma
        n, bins, patches = ax.hist(values, bins=20, density=True, alpha=0.7, 
                                   color='gray', edgecolor='black', linewidth=1.2)
        
        # Curva de densidade normal
        mu, sigma = values.mean(), values.std()
        x = np.linspace(values.min(), values.max(), 100)
        ax.plot(x, stats.norm.pdf(x, mu, sigma), 'b-', linewidth=3, label='Normal')
        
        # Formatação
        ax.set_xlabel(labels_map.get(output_var, output_var), fontsize=11, fontweight='bold')
        ax.set_ylabel('Frequência', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=9)
        
        # Adicionar estatísticas no gráfico
        textstr = f'Média: {mu:.2f}\nDesvPad: {sigma:.2f}\nn: {len(values)}'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.95, 0.95, textstr, transform=ax.transAxes, fontsize=9,
               verticalalignment='top', horizontalalignment='right', bbox=props)
        
        print(f"  ✓ {output_var}: média={mu:.2f}, std={sigma:.2f}")
        idx += 1
    
    fig.suptitle('Análise de Variabilidade dos Valores Médios', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_file = save_dir / 'distribuicao_variaveis_dependentes.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ distribuicao_variaveis_dependentes.png")


def create_sensitivity_plots(data: pd.DataFrame, sensitivity_results: Dict, 
                            output_vars: List[str], save_dir: Path):
    """
    Cria todos os gráficos de análise de sensibilidade.
    
    Args:
        data: DataFrame completo
        sensitivity_results: Dicionário com resultados de sensibilidade
        output_vars: Lista de variáveis dependentes
        save_dir: Diretório para salvar
    """
    print("\n" + "="*80)
    print("GRÁFICOS DE SENSIBILIDADE")
    print("="*80)
    
    save_dir.mkdir(parents=True, exist_ok=True)
    
    for output_var in output_vars:
        if output_var not in sensitivity_results:
            print(f"⚠️  {output_var}: sem dados de sensibilidade")
            continue
        
        df = sensitivity_results[output_var]
        
        # Verifica se tem dados válidos
        if df['SRC_abs'].sum() == 0:
            print(f"⚠️  {output_var}: variância zero, pulando gráficos")
            continue
        
        print(f"\n{output_var}:")
        
        # 1. Barras SRC
        df_sorted = df.sort_values('SRC_abs', ascending=True).tail(10)
        fig, ax = plt.subplots(figsize=(10, max(6, len(df_sorted) * 0.4)))
        colors = ['#d62728' if x < 0 else '#2ca02c' for x in df_sorted['SRC']]
        ax.barh(df_sorted.index, df_sorted['SRC'], color=colors, alpha=0.7)
        ax.set_xlabel('SRC (Standardized Regression Coefficient)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Parâmetros', fontsize=12, fontweight='bold')
        ax.set_title(f'Análise de Sensibilidade: {output_var}', fontsize=14, fontweight='bold')
        ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
        ax.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        out_file = save_dir / f"{output_var}_src_bars.png"
        plt.savefig(out_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ {out_file.name}")
        
        # 2. Comparação SRC/PCC/Pearson
        top_params = df.nlargest(8, 'SRC_abs').index
        df_top = df.loc[top_params]
        
        fig, axes = plt.subplots(1, 3, figsize=(16, 6), sharey=True)
        methods = ['SRC', 'PCC', 'Pearson']
        
        for ax, method in zip(axes, methods):
            df_sorted = df_top.sort_values(f'{method}_abs', ascending=True)
            colors_method = ['#d62728' if x < 0 else '#2ca02c' for x in df_sorted[method]]
            ax.barh(df_sorted.index, df_sorted[method], color=colors_method, alpha=0.7)
            ax.set_xlabel(method, fontsize=12, fontweight='bold')
            ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
            ax.grid(axis='x', alpha=0.3)
        
        axes[0].set_ylabel('Parâmetros', fontsize=12, fontweight='bold')
        fig.suptitle(f'Comparação de Métodos - {output_var}', fontsize=14, fontweight='bold')
        plt.tight_layout()
        out_file = save_dir / f"{output_var}_comparison.png"
        plt.savefig(out_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ {out_file.name}")
        
        # 3. Tornado diagram
        df_sorted = df.sort_values('SRC_abs', ascending=True).tail(10)
        fig, ax = plt.subplots(figsize=(12, max(6, len(df_sorted) * 0.5)))
        
        y_pos = np.arange(len(df_sorted))
        widths = df_sorted['SRC_abs']
        colors_tornado = plt.cm.RdYlGn_r(widths / widths.max())
        
        bars = ax.barh(y_pos, widths, color=colors_tornado, alpha=0.8, edgecolor='black', linewidth=1)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(df_sorted.index)
        ax.set_xlabel('|SRC| (Valor Absoluto)', fontsize=12, fontweight='bold')
        ax.set_title(f'Tornado Diagram - {output_var}', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        for i, (bar, val) in enumerate(zip(bars, df_sorted['SRC'])):
            ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                   f'SRC={val:+.3f}', va='center', fontsize=9)
        
        plt.tight_layout()
        out_file = save_dir / f"{output_var}_tornado.png"
        plt.savefig(out_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ {out_file.name}")


def generate_text_report(data: pd.DataFrame, sensitivity_results: Dict, 
                         descriptive_stats: pd.DataFrame, results_dir: Path):
    """
    Gera relatório consolidado em texto.
    
    Args:
        data: DataFrame completo
        sensitivity_results: Resultados de sensibilidade
        descriptive_stats: Estatísticas descritivas
        results_dir: Diretório dos resultados
    """
    print("\n" + "="*80)
    print("RELATÓRIO CONSOLIDADO - ANÁLISE DE SENSIBILIDADE")
    print("Laboratório de Arquitetura - UFC Quixadá")
    print("="*80)
    
    print(f"\n📊 ESTATÍSTICAS DESCRITIVAS")
    print("="*80)
    print(descriptive_stats.to_string())
    
    print(f"\n\n🌡️  TEMPERATURAS REGIONAIS")
    print("="*80)
    temp_cols = [c for c in data.columns if 'temp_regiao' in c]
    if temp_cols:
        temp_stats = data[temp_cols].describe()
        print(temp_stats.to_string())
    else:
        print("⚠️  Dados de temperatura não disponíveis")
    
    print(f"\n\n📈 ANÁLISE DE SENSIBILIDADE - TOP 3 PARÂMETROS")
    print("="*80)
    
    for output_var, df in sensitivity_results.items():
        if df['SRC_abs'].sum() == 0:
            continue
        
        top3 = df.nlargest(3, 'SRC_abs')
        print(f"\n{output_var}:")
        for i, (param, row) in enumerate(top3.iterrows(), 1):
            sign = '+' if row['SRC'] > 0 else ''
            print(f"  {i}. {param:30s} SRC={sign}{row['SRC']:.3f}  |  PCC={sign}{row['PCC']:.3f}")
    
    print(f"\n{'='*80}\n")


def main():
    """Função principal."""
    if len(sys.argv) < 2:
        print("Uso: python generate_all_reports.py <diretório_resultados>")
        print("Exemplo: python generate_all_reports.py results/sensitivity_analysis/20260119_205540")
        sys.exit(1)
    
    results_dir = Path(sys.argv[1])
    
    if not results_dir.exists():
        print(f"❌ Erro: Diretório não encontrado: {results_dir}")
        sys.exit(1)
    
    print(f"\n🔍 Carregando dados de: {results_dir}")
    
    # Carregar dados
    try:
        complete_data = pd.read_csv(results_dir / 'complete_data.csv')
        descriptive_stats = pd.read_csv(results_dir / 'sensitivity_indices' / 'descriptive_statistics.csv', index_col=0)
        
        # Carregar índices de sensibilidade
        sensitivity_results = {}
        sens_dir = results_dir / 'sensitivity_indices'
        for csv_file in sens_dir.glob('sensitivity_*.csv'):
            var_name = csv_file.stem.replace('sensitivity_', '')
            if var_name != 'descriptive_statistics':
                sensitivity_results[var_name] = pd.read_csv(csv_file, index_col=0)
        
        output_vars = list(sensitivity_results.keys())
        
        print(f"✓ Dados carregados: {len(complete_data)} simulações")
        print(f"✓ Variáveis dependentes: {len(output_vars)}")
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Criar diretório de plots
    plots_dir = results_dir / 'plots'
    plots_dir.mkdir(exist_ok=True)
    
    # Gerar todos os gráficos e relatórios
    try:
        create_distribution_plots(complete_data, output_vars, plots_dir)
        create_temperature_plots(complete_data, plots_dir)
        create_sensitivity_plots(complete_data, sensitivity_results, output_vars, plots_dir)
        generate_text_report(complete_data, sensitivity_results, descriptive_stats, results_dir)
        
        print(f"\n{'='*80}")
        print("✅ TODOS OS RELATÓRIOS E GRÁFICOS GERADOS COM SUCESSO!")
        print(f"{'='*80}")
        print(f"\n📁 Localização: {plots_dir}")
        print(f"\nArquivos gerados:")
        for png_file in sorted(plots_dir.glob('*.png')):
            print(f"  - {png_file.name}")
        print(f"\n{'='*80}\n")
        
    except Exception as e:
        print(f"\n❌ Erro ao gerar relatórios: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

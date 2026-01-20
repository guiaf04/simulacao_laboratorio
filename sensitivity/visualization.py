"""
Visualização de resultados da análise de sensibilidade.

Gera gráficos de barras, scatter plots e análise de variabilidade.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List


# Configuração de estilo
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['font.size'] = 10


class SensitivityVisualizer:
    """Cria visualizações para análise de sensibilidade."""
    
    def __init__(self, data: pd.DataFrame, sensitivity_results: Dict):
        self.data = data
        self.sensitivity_results = sensitivity_results
    
    def plot_sensitivity_bars(self, output_var: str, method: str = 'SRC', 
                             top_n: int = None, save_path: str = None):
        """
        Gráfico de barras dos índices de sensibilidade.
        
        Args:
            output_var: Variável dependente
            method: 'SRC', 'PCC' ou 'Pearson'
            top_n: Mostrar apenas top N parâmetros (None = todos)
            save_path: Caminho para salvar figura
        """
        df = self.sensitivity_results[output_var]
        
        # Ordena por valor absoluto
        df_sorted = df.sort_values(f'{method}_abs', ascending=True)
        
        if top_n:
            df_sorted = df_sorted.tail(top_n)
        
        # Cria figura
        fig, ax = plt.subplots(figsize=(10, max(6, len(df_sorted) * 0.4)))
        
        # Barras horizontais
        colors = ['#d62728' if x < 0 else '#2ca02c' for x in df_sorted[method]]
        ax.barh(df_sorted.index, df_sorted[method], color=colors, alpha=0.7)
        
        # Formatação
        ax.set_xlabel(f'{method} (Índice de Sensibilidade)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Parâmetros', fontsize=12, fontweight='bold')
        ax.set_title(f'Sensibilidade: {output_var}\nMétodo: {method}', 
                    fontsize=14, fontweight='bold')
        ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Salvo: {save_path}")
        
        return fig
    
    def plot_comparison_bars(self, output_var: str, save_path: str = None):
        """
        Compara SRC, PCC e Pearson lado a lado.
        
        Args:
            output_var: Variável dependente
            save_path: Caminho para salvar figura
        """
        df = self.sensitivity_results[output_var]
        
        # Top 8 parâmetros por SRC
        top_params = df.nlargest(8, 'SRC_abs').index
        df_top = df.loc[top_params]
        
        # Cria figura
        fig, axes = plt.subplots(1, 3, figsize=(16, 6), sharey=True)
        
        methods = ['SRC', 'PCC', 'Pearson']
        
        for ax, method in zip(axes, methods):
            df_sorted = df_top.sort_values(f'{method}_abs', ascending=True)
            colors = ['#d62728' if x < 0 else '#2ca02c' for x in df_sorted[method]]
            
            ax.barh(df_sorted.index, df_sorted[method], color=colors, alpha=0.7)
            ax.set_xlabel(method, fontsize=12, fontweight='bold')
            ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
            ax.grid(axis='x', alpha=0.3)
        
        axes[0].set_ylabel('Parâmetros', fontsize=12, fontweight='bold')
        fig.suptitle(f'Comparação de Métodos - {output_var}', 
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Salvo: {save_path}")
        
        return fig
    
    def plot_scatter_matrix(self, output_var: str, top_n: int = 6, save_path: str = None):
        """
        Matriz de scatter plots dos parâmetros mais influentes.
        
        Args:
            output_var: Variável dependente
            top_n: Número de parâmetros a mostrar
            save_path: Caminho para salvar figura
        """
        df = self.sensitivity_results[output_var]
        top_params = df.nlargest(top_n, 'SRC_abs').index.tolist()
        
        # Dados para scatter
        plot_data = self.data[top_params + [output_var]].copy()
        
        # Cria pairplot
        g = sns.pairplot(plot_data, 
                        x_vars=top_params, 
                        y_vars=[output_var],
                        height=3, 
                        aspect=1.2,
                        plot_kws={'alpha': 0.5, 's': 20})
        
        g.fig.suptitle(f'Relação Parâmetros × {output_var}', 
                      fontsize=14, fontweight='bold', y=1.02)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Salvo: {save_path}")
        
        return g
    
    def plot_individual_scatter(self, output_var: str, param: str, save_path: str = None):
        """
        Scatter plot individual de um parâmetro vs saída.
        
        Args:
            output_var: Variável dependente
            param: Parâmetro de entrada
            save_path: Caminho para salvar figura
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        
        x = self.data[param]
        y = self.data[output_var]
        
        # Scatter
        ax.scatter(x, y, alpha=0.5, s=30, color='steelblue')
        
        # Linha de tendência
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        ax.plot(x.sort_values(), p(x.sort_values()), 
               "r--", linewidth=2, label=f'y = {z[0]:.2f}x + {z[1]:.2f}')
        
        # Correlação
        r = np.corrcoef(x, y)[0, 1]
        ax.text(0.05, 0.95, f'r = {r:.3f}', 
               transform=ax.transAxes, 
               fontsize=12, fontweight='bold',
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_xlabel(param, fontsize=12, fontweight='bold')
        ax.set_ylabel(output_var, fontsize=12, fontweight='bold')
        ax.set_title(f'{param} × {output_var}', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Salvo: {save_path}")
        
        return fig
    
    def plot_variability_boxplot(self, output_vars: List[str], save_path: str = None):
        """
        Boxplot da variabilidade das variáveis dependentes.
        
        Args:
            output_vars: Lista de variáveis dependentes
            save_path: Caminho para salvar figura
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Normaliza dados (para comparação)
        data_normalized = self.data[output_vars].copy()
        for col in output_vars:
            data_normalized[col] = (data_normalized[col] - data_normalized[col].mean()) / data_normalized[col].std()
        
        # Boxplot
        data_normalized.boxplot(ax=ax, grid=False, patch_artist=True,
                               boxprops=dict(facecolor='lightblue', alpha=0.7),
                               medianprops=dict(color='red', linewidth=2))
        
        ax.set_ylabel('Valor Normalizado (z-score)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Variáveis Dependentes', fontsize=12, fontweight='bold')
        ax.set_title('Variabilidade das Saídas (Normalizadas)', fontsize=14, fontweight='bold')
        ax.axhline(0, color='black', linewidth=0.8, linestyle='--', alpha=0.5)
        ax.grid(axis='y', alpha=0.3)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Salvo: {save_path}")
        
        return fig
    
    def plot_tornado(self, output_var: str, top_n: int = 10, save_path: str = None):
        """
        Gráfico Tornado mostrando range de variação da saída.
        
        Args:
            output_var: Variável dependente
            top_n: Número de parâmetros a mostrar
            save_path: Caminho para salvar figura
        """
        df = self.sensitivity_results[output_var]
        top_params = df.nlargest(top_n, 'SRC_abs').index.tolist()
        
        ranges = []
        for param in top_params:
            # Calcula range de saída quando param varia
            data_sorted = self.data.sort_values(param)
            
            # 10% inferior e superior
            n = len(data_sorted)
            low_idx = int(n * 0.1)
            high_idx = int(n * 0.9)
            
            low_mean = data_sorted.iloc[:low_idx][output_var].mean()
            high_mean = data_sorted.iloc[high_idx:][output_var].mean()
            
            ranges.append({
                'param': param,
                'low': low_mean,
                'high': high_mean,
                'range': abs(high_mean - low_mean)
            })
        
        ranges_df = pd.DataFrame(ranges).sort_values('range', ascending=True)
        
        # Plota
        fig, ax = plt.subplots(figsize=(10, max(6, len(ranges_df) * 0.4)))
        
        y_pos = range(len(ranges_df))
        
        for i, row in enumerate(ranges_df.itertuples()):
            ax.barh(i, row.high - row.low, left=row.low, 
                   color='steelblue', alpha=0.7, height=0.6)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(ranges_df['param'])
        ax.set_xlabel(output_var, fontsize=12, fontweight='bold')
        ax.set_ylabel('Parâmetros', fontsize=12, fontweight='bold')
        ax.set_title(f'Tornado Diagram - {output_var}', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Salvo: {save_path}")
        
        return fig


def create_all_plots(data: pd.DataFrame, sensitivity_results: Dict, 
                    output_vars: List[str], save_dir: str):
    """
    Gera todos os gráficos da análise.
    
    Args:
        data: DataFrame completo
        sensitivity_results: Resultados da análise de sensibilidade
        output_vars: Lista de variáveis dependentes
        save_dir: Diretório para salvar figuras
    """
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    
    visualizer = SensitivityVisualizer(data, sensitivity_results)
    
    print(f"\n{'='*70}")
    print("GERANDO VISUALIZAÇÕES")
    print(f"{'='*70}\n")
    
    for output_var in output_vars:
        print(f"\nGráficos para: {output_var}")
        
        # 1. Barras de sensibilidade (SRC)
        visualizer.plot_sensitivity_bars(
            output_var, method='SRC',
            save_path=save_path / f"{output_var}_src_bars.png"
        )
        
        # 2. Comparação de métodos
        visualizer.plot_comparison_bars(
            output_var,
            save_path=save_path / f"{output_var}_comparison.png"
        )
        
        # 3. Scatter matrix
        visualizer.plot_scatter_matrix(
            output_var, top_n=6,
            save_path=save_path / f"{output_var}_scatter_matrix.png"
        )
        
        # 4. Tornado diagram
        visualizer.plot_tornado(
            output_var, top_n=10,
            save_path=save_path / f"{output_var}_tornado.png"
        )
        
        plt.close('all')  # Libera memória
    
    # 5. Variabilidade geral
    visualizer.plot_variability_boxplot(
        output_vars,
        save_path=save_path / "variability_boxplot.png"
    )
    
    plt.close('all')
    
    print(f"\n✓ Todas as visualizações salvas em: {save_dir}")


if __name__ == "__main__":
    # Teste com dados simulados
    print("Testando visualizações...")
    
    np.random.seed(42)
    n = 200
    
    data = pd.DataFrame({
        'param_A': np.random.normal(5, 1, n),
        'param_B': np.random.uniform(0, 10, n),
        'param_C': np.random.normal(3, 0.5, n),
    })
    
    data['output'] = 2*data['param_A'] - 0.5*data['param_B'] + 1.5*data['param_C'] + np.random.normal(0, 1, n)
    
    # Simula resultados de sensibilidade
    sens_results = {
        'output': pd.DataFrame({
            'SRC': [2.0, -0.5, 1.5],
            'PCC': [0.9, -0.3, 0.8],
            'Pearson': [0.85, -0.25, 0.75],
            'SRC_abs': [2.0, 0.5, 1.5],
            'PCC_abs': [0.9, 0.3, 0.8],
            'Pearson_abs': [0.85, 0.25, 0.75],
        }, index=['param_A', 'param_B', 'param_C'])
    }
    
    visualizer = SensitivityVisualizer(data, sens_results)
    visualizer.plot_sensitivity_bars('output', method='SRC')
    plt.show()
    
    print("✓ Teste concluído")

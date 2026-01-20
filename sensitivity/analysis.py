"""
Análise de sensibilidade global usando métodos de regressão.

Implementa SRC (Standardized Regression Coefficients) e PCC (Partial Correlation Coefficients).
Baseado no artigo Silva & Ghisi (2013).
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from typing import Dict, Tuple


class SensitivityAnalyzer:
    """Análise de sensibilidade global."""
    
    def __init__(self, data: pd.DataFrame, input_params: list, output_vars: list):
        """
        Args:
            data: DataFrame com inputs e outputs
            input_params: Lista de nomes dos parâmetros de entrada
            output_vars: Lista de nomes das variáveis dependentes
        """
        self.data = data.copy()
        self.input_params = input_params
        self.output_vars = output_vars
        
        # Remove NaN
        self.data = self.data.dropna()
        
        if len(self.data) == 0:
            raise ValueError("Dataset vazio após remover NaN")
    
    def calculate_src(self, output_var: str) -> pd.Series:
        """
        Calcula Standardized Regression Coefficients (SRC).
        
        SRC mede a contribuição linear de cada parâmetro para a variável de saída.
        Valores absolutos maiores = mais influente.
        
        Args:
            output_var: Nome da variável dependente
        
        Returns:
            Series com SRC de cada parâmetro (normalizado)
        """
        X = self.data[self.input_params].values
        y = self.data[output_var].values
        
        # Verifica se output tem variância
        if y.std() == 0:
            print(f"  ⚠️  Variável '{output_var}' tem variância zero (valores constantes). Pulando análise.")
            return pd.Series(np.zeros(len(self.input_params)), index=self.input_params, name='SRC')
        
        # Padroniza inputs e outputs (média=0, std=1)
        X_std = (X - X.mean(axis=0)) / X.std(axis=0)
        y_std = (y - y.mean()) / y.std()
        
        # Regressão linear
        model = LinearRegression(fit_intercept=False)
        model.fit(X_std, y_std)
        
        # Coeficientes já são padronizados (SRC)
        src = pd.Series(model.coef_, index=self.input_params, name='SRC')
        
        return src
    
    def calculate_pcc(self, output_var: str) -> pd.Series:
        """
        Calcula Partial Correlation Coefficients (PCC).
        
        PCC mede a correlação linear entre cada parâmetro e a saída,
        removendo o efeito dos outros parâmetros.
        
        Args:
            output_var: Nome da variável dependente
        
        Returns:
            Series com PCC de cada parâmetro
        """
        y = self.data[output_var].values
        
        # Verifica se output tem variância
        if y.std() == 0:
            return pd.Series(np.zeros(len(self.input_params)), index=self.input_params, name='PCC')
        
        pcc_values = {}
        
        for param in self.input_params:
            # Outros parâmetros (exceto o atual)
            other_params = [p for p in self.input_params if p != param]
            
            # Dados
            X_param = self.data[param].values
            X_others = self.data[other_params].values
            
            # Remove efeito dos outros parâmetros em X_param
            model_x = LinearRegression()
            model_x.fit(X_others, X_param)
            residual_x = X_param - model_x.predict(X_others)
            
            # Remove efeito dos outros parâmetros em y
            model_y = LinearRegression()
            model_y.fit(X_others, y)
            residual_y = y - model_y.predict(X_others)
            
            # Correlação entre resíduos
            pcc = np.corrcoef(residual_x, residual_y)[0, 1]
            pcc_values[param] = pcc
        
        return pd.Series(pcc_values, name='PCC')
    
    def calculate_pearson(self, output_var: str) -> pd.Series:
        """
        Calcula Coeficiente de Correlação de Pearson simples.
        
        Args:
            output_var: Nome da variável dependente
        
        Returns:
            Series com correlação de Pearson de cada parâmetro
        """
        correlations = {}
        
        for param in self.input_params:
            r, p_value = stats.pearsonr(self.data[param], self.data[output_var])
            correlations[param] = r
        
        return pd.Series(correlations, name='Pearson')
    
    def full_analysis(self) -> Dict[str, pd.DataFrame]:
        """
        Executa análise completa para todas as variáveis dependentes.
        
        Returns:
            Dicionário {output_var: DataFrame com SRC, PCC, Pearson}
        """
        results = {}
        
        for output_var in self.output_vars:
            print(f"\nAnalisando: {output_var}")
            
            src = self.calculate_src(output_var)
            pcc = self.calculate_pcc(output_var)
            pearson = self.calculate_pearson(output_var)
            
            # Combina em DataFrame
            df = pd.DataFrame({
                'SRC': src,
                'PCC': pcc,
                'Pearson': pearson,
                'SRC_abs': np.abs(src),
                'PCC_abs': np.abs(pcc),
                'Pearson_abs': np.abs(pearson),
            })
            
            # Ordena por influência (SRC absoluto)
            df = df.sort_values('SRC_abs', ascending=False)
            
            results[output_var] = df
            
            # Imprime top 5
            print("\nTop 5 parâmetros mais influentes (SRC):")
            for i, (param, row) in enumerate(df.head(5).iterrows(), 1):
                print(f"  {i}. {param:30s} | SRC={row['SRC']:+.3f} | PCC={row['PCC']:+.3f}")
        
        return results
    
    def calculate_r2(self, output_var: str) -> float:
        """
        Calcula R² do modelo de regressão linear.
        
        Indica quanto da variabilidade da saída é explicada pelos parâmetros.
        
        Args:
            output_var: Nome da variável dependente
        
        Returns:
            Coeficiente de determinação R²
        """
        X = self.data[self.input_params].values
        y = self.data[output_var].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        return model.score(X, y)
    
    def calculate_descriptive_stats(self, output_var: str) -> Dict[str, float]:
        """
        Calcula estatísticas descritivas da variável dependente.
        
        Args:
            output_var: Nome da variável dependente
        
        Returns:
            Dicionário com média, desvio padrão, min, max, etc.
        """
        y = self.data[output_var].values
        
        return {
            'mean': float(np.mean(y)),
            'std': float(np.std(y)),
            'min': float(np.min(y)),
            'max': float(np.max(y)),
            'median': float(np.median(y)),
            'q25': float(np.percentile(y, 25)),
            'q75': float(np.percentile(y, 75)),
            'cv': float(np.std(y) / np.mean(y) * 100) if np.mean(y) != 0 else 0  # Coeficiente de variação (%)
        }


def run_sensitivity_analysis(data: pd.DataFrame, save_dir: str = None) -> Dict:
    """
    Executa análise de sensibilidade completa.
    
    Args:
        data: DataFrame com inputs e outputs
        save_dir: Diretório para salvar resultados (opcional)
    
    Returns:
        Dicionário com resultados da análise
    """
    from .config import ALL_PARAMETERS, DEPENDENT_VARIABLES
    
    # Identifica colunas
    input_params = [p.name for p in ALL_PARAMETERS]
    output_vars = list(DEPENDENT_VARIABLES.keys())
    
    # Filtra apenas colunas presentes no dataset
    input_params = [p for p in input_params if p in data.columns]
    output_vars = [v for v in output_vars if v in data.columns]
    
    print(f"\n{'='*70}")
    print(f"ANÁLISE DE SENSIBILIDADE GLOBAL")
    print(f"{'='*70}")
    print(f"\nParâmetros de entrada ({len(input_params)}):")
    for param in input_params:
        print(f"  - {param}")
    print(f"\nVariáveis dependentes ({len(output_vars)}):")
    for var in output_vars:
        print(f"  - {var}")
    print(f"\nSimulações válidas: {len(data)}")
    
    # Análise
    analyzer = SensitivityAnalyzer(data, input_params, output_vars)
    results = analyzer.full_analysis()
    
    # Calcula estatísticas descritivas
    print(f"\n{'='*70}")
    print("ESTATÍSTICAS DESCRITIVAS DAS VARIÁVEIS DEPENDENTES:")
    print(f"{'='*70}")
    
    descriptive_stats = {}
    for output_var in output_vars:
        stats = analyzer.calculate_descriptive_stats(output_var)
        descriptive_stats[output_var] = stats
        print(f"\n{output_var}:")
        print(f"  Média:        {stats['mean']:>12.2f}")
        print(f"  Desvio Padrão:{stats['std']:>12.2f}")
        print(f"  Mínimo:       {stats['min']:>12.2f}")
        print(f"  Máximo:       {stats['max']:>12.2f}")
        print(f"  Mediana:      {stats['median']:>12.2f}")
        print(f"  Q25:          {stats['q25']:>12.2f}")
        print(f"  Q75:          {stats['q75']:>12.2f}")
        print(f"  CV (%):       {stats['cv']:>12.2f}")
    
    # Calcula R² para cada variável
    print(f"\n{'='*70}")
    print("QUALIDADE DO AJUSTE LINEAR (R²):")
    print(f"{'='*70}")
    
    r2_values = {}
    for output_var in output_vars:
        r2 = analyzer.calculate_r2(output_var)
        r2_values[output_var] = r2
        print(f"  {output_var:40s} R² = {r2:.3f} ({r2*100:.1f}%)")
    
    # Salva resultados
    if save_dir:
        from pathlib import Path
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        for output_var, df in results.items():
            filename = save_path / f"sensitivity_{output_var}.csv"
            df.to_csv(filename)
            print(f"\n✓ Salvo: {filename}")
        
        # Salva R²
        r2_df = pd.DataFrame.from_dict(r2_values, orient='index', columns=['R2'])
        r2_df.to_csv(save_path / "r2_scores.csv")
        
        # Salva estatísticas descritivas
        stats_df = pd.DataFrame.from_dict(descriptive_stats, orient='index')
        stats_df.to_csv(save_path / "descriptive_statistics.csv")
        print(f"✓ Salvo: {save_path / 'descriptive_statistics.csv'}")
    
    return {
        'sensitivity_indices': results,
        'r2_scores': r2_values,
        'descriptive_stats': descriptive_stats,
        'analyzer': analyzer
    }


if __name__ == "__main__":
    # Teste com dados simulados
    print("Testando análise de sensibilidade com dados simulados...")
    
    np.random.seed(42)
    n = 100
    
    # Cria dados fictícios
    data = pd.DataFrame({
        'param1': np.random.normal(0, 1, n),
        'param2': np.random.uniform(-1, 1, n),
        'param3': np.random.normal(0.5, 0.2, n),
    })
    
    # Output = combinação linear + ruído
    data['output1'] = 2*data['param1'] + 0.5*data['param2'] - 1*data['param3'] + np.random.normal(0, 0.1, n)
    data['output2'] = -data['param1'] + 3*data['param3'] + np.random.normal(0, 0.2, n)
    
    # Análise
    analyzer = SensitivityAnalyzer(
        data=data,
        input_params=['param1', 'param2', 'param3'],
        output_vars=['output1', 'output2']
    )
    
    results = analyzer.full_analysis()
    
    print("\n" + "="*70)
    print("Análise concluída!")

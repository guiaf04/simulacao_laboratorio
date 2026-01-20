"""
Extrator de resultados de simulações EnergyPlus.

Lê arquivos de saída (.csv, .err) e extrai variáveis dependentes.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional
from .config import DEPENDENT_VARIABLES


class ResultsExtractor:
    """Extrai resultados das simulações EnergyPlus."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
    
    def extract_all_variables(self) -> Dict[str, float]:
        """
        Extrai todas as variáveis dependentes.
        
        Returns:
            Dicionário com valores das variáveis dependentes
        """
        results = {}
        
        # Consumo anual de resfriamento
        results['consumo_anual_resfriamento'] = self._extract_cooling_consumption()
        
        # Carga de pico de resfriamento
        results['carga_pico_resfriamento'] = self._extract_peak_cooling()
        
        # Horas de desconforto
        results['horas_desconforto'] = self._extract_discomfort_hours()
        
        # Temperatura das 6 regiões teóricas
        regional_temps = self._extract_regional_temperatures()
        results.update(regional_temps)
        
        return results
    
    def _extract_cooling_consumption(self) -> float:
        """
        Extrai consumo anual de eletricidade para refrigeração (kWh/ano).
        
        Lê do eplusout.csv a coluna de consumo do sistema de resfriamento.
        Usa DistrictCooling:Facility [J] para sistemas ideais.
        """
        csv_file = self.output_dir / 'eplusout.csv'
        
        if not csv_file.exists():
            return np.nan
        
        try:
            df = pd.read_csv(csv_file)
            
            # Procura por colunas de DistrictCooling ou consumo de resfriamento
            cooling_columns = [col for col in df.columns if 
                             'DistrictCooling:Facility' in col or
                             any(x in col.lower() for x in 
                                 ['zone ideal loads zone total cooling energy',
                                  'zone ideal loads supply air total cooling energy'])]
            
            if not cooling_columns:
                return np.nan
            
            # Soma consumo total (converte J para kWh)
            total_j = df[cooling_columns].sum().sum()
            total_kwh = total_j / 3.6e6  # 1 kWh = 3.6e6 J
            
            return float(total_kwh)
        
        except Exception as e:
            print(f"Erro ao extrair consumo em {self.output_dir}: {e}")
            return np.nan
    
    def _extract_peak_cooling(self) -> float:
        """
        Extrai carga de pico de resfriamento (kW).
        
        Calcula a taxa máxima instantânea de resfriamento.
        Para sistemas ideais, usa Zone Ideal Loads Zone Total Cooling Energy [J]
        e calcula a potência dividindo pelo timestep.
        """
        csv_file = self.output_dir / 'eplusout.csv'
        
        if not csv_file.exists():
            return np.nan
        
        try:
            df = pd.read_csv(csv_file)
            
            # Procura por colunas de energia de resfriamento timestep
            cooling_energy_cols = [col for col in df.columns if 
                                  'Zone Ideal Loads Zone Total Cooling Energy' in col or
                                  'DistrictCooling:Facility' in col]
            
            if not cooling_energy_cols:
                return np.nan
            
            # Timestep padrão do EnergyPlus: 15 minutos = 900 segundos
            timestep_seconds = 900.0
            
            # Calcula potência (W) = Energia (J) / tempo (s)
            # Depois converte para kW
            max_w = (df[cooling_energy_cols].max().max()) / timestep_seconds
            max_kw = max_w / 1000.0
            
            return float(max_kw)
        
        except Exception as e:
            print(f"Erro ao extrair pico em {self.output_dir}: {e}")
            return np.nan
    
    def _extract_discomfort_hours(self, threshold: float = 26.0) -> float:
        """
        Extrai horas de desconforto (horas acima do threshold).
        
        Args:
            threshold: Temperatura limite para desconforto (°C)
        
        Returns:
            Número de horas acima do threshold
        """
        csv_file = self.output_dir / 'eplusout.csv'
        
        if not csv_file.exists():
            return np.nan
        
        try:
            df = pd.read_csv(csv_file)
            
            # Procura por temperatura operativa ou do ar da zona
            temp_cols = [col for col in df.columns if 
                        any(x in col.lower() for x in 
                            ['operative temp', 'zone mean air temp', 
                             'zone air temperature'])]
            
            if not temp_cols:
                return np.nan
            
            # Conta horas acima do threshold
            discomfort_hours = 0
            for col in temp_cols:
                discomfort_hours += (df[col] > threshold).sum()
            
            # Média entre as zonas (se houver múltiplas)
            if len(temp_cols) > 1:
                discomfort_hours /= len(temp_cols)
            
            return float(discomfort_hours)
        
        except Exception as e:
            print(f"Erro ao extrair desconforto em {self.output_dir}: {e}")
            return np.nan
    
    def _extract_regional_temperatures(self) -> Dict[str, float]:
        """
        Extrai temperatura média de 6 regiões teóricas do laboratório.
        
        As 6 regiões são divisões conceituais (não zonas físicas):
        - Região 1 (Frente-Esquerda): Próximo janela 1 + lousa
        - Região 2 (Frente-Direita): Próximo porta + lousa
        - Região 3 (Centro-Esquerda): Próximo janela 2
        - Região 4 (Centro-Direita): Centro da sala
        - Região 5 (Fundo-Esquerda): Próximo janelas 3,4 + ACs
        - Região 6 (Fundo-Direita): Próximo ACs
        
        Usa temperatura de superfícies internas próximas para estimar temperatura regional.
        """
        csv_file = self.output_dir / 'eplusout.csv'
        
        if not csv_file.exists():
            return {f'temp_regiao_{i}': np.nan for i in range(1, 7)}
        
        try:
            df = pd.read_csv(csv_file)
            
            # Temperatura média da zona (referência)
            zone_temp_col = [c for c in df.columns if 'Zone Mean Air Temperature' in c]
            zone_temp = df[zone_temp_col[0]].mean() if zone_temp_col else 24.0
            
            # Temperatura de superfícies internas
            wall_front_col = [c for c in df.columns if 'WALL_FRONT_BLACKBOARD' in c and 'Inside Face Temperature' in c]
            wall_back_col = [c for c in df.columns if 'WALL_BACK_AC' in c and 'Inside Face Temperature' in c]
            wall_left_col = [c for c in df.columns if 'WALL_LEFT_WINDOWS' in c and 'Inside Face Temperature' in c]
            wall_right_col = [c for c in df.columns if 'WALL_RIGHT_DOOR' in c and 'Inside Face Temperature' in c]
            
            # Extrai temperaturas médias de paredes
            t_front = df[wall_front_col[0]].mean() if wall_front_col else zone_temp
            t_back = df[wall_back_col[0]].mean() if wall_back_col else zone_temp
            t_left = df[wall_left_col[0]].mean() if wall_left_col else zone_temp
            t_right = df[wall_right_col[0]].mean() if wall_right_col else zone_temp
            
            # Radiação solar através das janelas (W) - indica aquecimento local
            # Quanto mais radiação, mais quente fica a região próxima
            window1_solar = [c for c in df.columns if 'WINDOW_1' in c and 'Transmitted Solar' in c]
            window2_solar = [c for c in df.columns if 'WINDOW_2' in c and 'Transmitted Solar' in c]
            window3_solar = [c for c in df.columns if 'WINDOW_3' in c and 'Transmitted Solar' in c]
            window4_solar = [c for c in df.columns if 'WINDOW_4' in c and 'Transmitted Solar' in c]
            
            # Radiação média (W)
            solar_w1 = df[window1_solar[0]].mean() if window1_solar else 0
            solar_w2 = df[window2_solar[0]].mean() if window2_solar else 0
            solar_w3 = df[window3_solar[0]].mean() if window3_solar else 0
            solar_w4 = df[window4_solar[0]].mean() if window4_solar else 0
            
            # Normaliza radiação para incremento de temperatura (aprox: 100W ~ +0.5°C)
            # Baseado em ganho térmico típico por radiação solar direta
            delta_t_w1 = solar_w1 / 200.0  # °C
            delta_t_w2 = solar_w2 / 200.0
            delta_t_w3 = solar_w3 / 200.0
            delta_t_w4 = solar_w4 / 200.0
            
            # Calcula temperatura regional combinando:
            # 1. Temperatura da zona (base)
            # 2. Temperatura das superfícies adjacentes
            # 3. Incremento por radiação solar nas janelas
            results = {
                'temp_regiao_1': zone_temp + 0.4 * (t_left - zone_temp) + 0.3 * (t_front - zone_temp) + delta_t_w1,  # Frente-Esquerda (janela 1)
                'temp_regiao_2': zone_temp + 0.5 * (t_right - zone_temp) + 0.3 * (t_front - zone_temp),              # Frente-Direita (porta)
                'temp_regiao_3': zone_temp + 0.4 * (t_left - zone_temp) + delta_t_w2,                                # Centro-Esquerda (janela 2)
                'temp_regiao_4': zone_temp + 0.1 * (t_front - zone_temp) + 0.1 * (t_back - zone_temp),               # Centro (longe janelas)
                'temp_regiao_5': zone_temp + 0.3 * (t_back - zone_temp) + 0.3 * (t_left - zone_temp) + 0.5 * (delta_t_w3 + delta_t_w4),  # Fundo-Esquerda (janelas 3,4)
                'temp_regiao_6': zone_temp + 0.5 * (t_back - zone_temp) + 0.2 * (t_right - zone_temp),               # Fundo-Direita (ACs)
            }
            
            return {k: float(v) for k, v in results.items()}
        
        except Exception as e:
            print(f"Erro ao extrair temperaturas regionais em {self.output_dir}: {e}")
            return {f'temp_regiao_{i}': np.nan for i in range(1, 7)}
    
    def get_error_summary(self) -> Dict[str, any]:
        """
        Extrai resumo de erros/warnings do arquivo .err.
        
        Returns:
            Dicionário com contagem de erros
        """
        err_file = self.output_dir / 'eplusout.err'
        
        if not err_file.exists():
            return {'fatal': -1, 'severe': -1, 'warnings': -1}
        
        try:
            with open(err_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {
                'fatal': content.count('**  Fatal  **'),
                'severe': content.count('** Severe  **'),
                'warnings': content.count('** Warning **'),
            }
        
        except Exception as e:
            return {'error': str(e)}


def extract_all_results(sim_results_df: pd.DataFrame, base_output_dir: str) -> pd.DataFrame:
    """
    Extrai resultados de todas as simulações.
    
    Args:
        sim_results_df: DataFrame com status das simulações
        base_output_dir: Diretório base dos outputs
    
    Returns:
        DataFrame com variáveis dependentes de cada simulação
    """
    print("\nExtraindo resultados das simulações...")
    
    results_list = []
    
    for idx, row in sim_results_df.iterrows():
        sim_id = row['sim_id']
        
        if not row['success']:
            # Simulação falhou - valores NaN
            results_list.append({
                'sim_id': sim_id,
                'consumo_anual_resfriamento': np.nan,
                'carga_pico_resfriamento': np.nan,
                'horas_desconforto': np.nan,
                'success': False
            })
            continue
        
        output_dir = Path(base_output_dir) / f"sim_{sim_id:04d}"
        extractor = ResultsExtractor(output_dir)
        
        try:
            results = extractor.extract_all_variables()
            results['sim_id'] = sim_id
            results['success'] = True
            results_list.append(results)
        
        except Exception as e:
            print(f"✗ Erro ao extrair resultados de sim_{sim_id}: {e}")
            results_list.append({
                'sim_id': sim_id,
                'consumo_anual_resfriamento': np.nan,
                'carga_pico_resfriamento': np.nan,
                'horas_desconforto': np.nan,
                'success': False
            })
    
    results_df = pd.DataFrame(results_list)
    
    # Estatísticas
    n_valid = results_df['success'].sum()
    print(f"\n✓ Resultados extraídos: {n_valid}/{len(results_df)} simulações válidas")
    
    return results_df


def merge_inputs_outputs(samples_df: pd.DataFrame, results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Combina inputs (amostras LHS) e outputs (resultados).
    
    Args:
        samples_df: DataFrame com parâmetros de entrada
        results_df: DataFrame com variáveis dependentes
    
    Returns:
        DataFrame completo para análise de sensibilidade
    """
    merged_df = pd.merge(samples_df, results_df, on='sim_id', how='left')
    
    # Remove simulações com resultados inválidos
    merged_df = merged_df[merged_df['success'] == True].copy()
    merged_df.drop(columns=['success'], inplace=True)
    
    print(f"\n✓ Dataset completo: {len(merged_df)} simulações válidas")
    
    return merged_df


if __name__ == "__main__":
    # Teste de extração
    print("Testando extração de resultados...")
    
    test_dir = "results/test_run"
    if Path(test_dir).exists():
        extractor = ResultsExtractor(test_dir)
        results = extractor.extract_all_variables()
        
        print("\nResultados extraídos:")
        for key, value in results.items():
            print(f"  {key}: {value}")
        
        errors = extractor.get_error_summary()
        print(f"\nResumo de erros: {errors}")
    else:
        print(f"Diretório de teste não encontrado: {test_dir}")

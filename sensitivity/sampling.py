"""
Gerador de amostras usando Latin Hypercube Sampling (LHS) com diferentes distribuições.

Implementa amostragem estratificada para análise de sensibilidade global.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import List
from .config import ParameterDistribution, ALL_PARAMETERS, RANDOM_SEED


class LHSSampler:
    """Gera amostras usando Latin Hypercube Sampling."""
    
    def __init__(self, parameters: List[ParameterDistribution], n_samples: int, seed: int = RANDOM_SEED):
        self.parameters = parameters
        self.n_samples = n_samples
        self.seed = seed
        np.random.seed(seed)
    
    def generate_samples(self) -> pd.DataFrame:
        """Gera matriz de amostras LHS com distribuições específicas."""
        samples = {}
        
        for param in self.parameters:
            samples[param.name] = self._sample_parameter(param)
        
        return pd.DataFrame(samples)
    
    def _sample_parameter(self, param: ParameterDistribution) -> np.ndarray:
        """Gera amostras para um parâmetro específico usando LHS."""
        # Gera amostras uniformes estratificadas [0, 1]
        lhs_uniform = self._lhs_uniform()
        
        # Transforma para a distribuição desejada
        if param.distribution == 'uniform':
            return self._transform_uniform(lhs_uniform, param)
        
        elif param.distribution == 'normal':
            return self._transform_normal(lhs_uniform, param)
        
        elif param.distribution == 'triangular':
            return self._transform_triangular(lhs_uniform, param)
        
        elif param.distribution == 'discrete':
            return self._transform_discrete(lhs_uniform, param)
        
        else:
            raise ValueError(f"Distribuição não suportada: {param.distribution}")
    
    def _lhs_uniform(self) -> np.ndarray:
        """Gera amostras uniformes estratificadas usando LHS."""
        # Divide [0,1] em n_samples estratos
        segments = np.linspace(0, 1, self.n_samples + 1)
        
        # Amostra aleatória dentro de cada estrato
        samples = np.random.uniform(segments[:-1], segments[1:])
        
        # Permuta aleatoriamente
        np.random.shuffle(samples)
        
        return samples
    
    def _transform_uniform(self, lhs_samples: np.ndarray, param: ParameterDistribution) -> np.ndarray:
        """Transforma amostras LHS para distribuição uniforme."""
        return lhs_samples * (param.max_value - param.min_value) + param.min_value
    
    def _transform_normal(self, lhs_samples: np.ndarray, param: ParameterDistribution) -> np.ndarray:
        """Transforma amostras LHS para distribuição normal truncada."""
        # Usa função inversa da CDF normal
        samples = stats.norm.ppf(lhs_samples, loc=param.mean, scale=param.std)
        
        # Trunca nos limites
        samples = np.clip(samples, param.min_value, param.max_value)
        
        return samples
    
    def _transform_triangular(self, lhs_samples: np.ndarray, param: ParameterDistribution) -> np.ndarray:
        """Transforma amostras LHS para distribuição triangular."""
        # Calcula parâmetro c da distribuição triangular (localização da moda)
        c = (param.mode - param.min_value) / (param.max_value - param.min_value)
        
        # Usa função inversa da CDF triangular
        samples = np.zeros_like(lhs_samples)
        
        mask_lower = lhs_samples < c
        samples[mask_lower] = param.min_value + np.sqrt(
            lhs_samples[mask_lower] * (param.max_value - param.min_value) * (param.mode - param.min_value)
        )
        
        mask_upper = ~mask_lower
        samples[mask_upper] = param.max_value - np.sqrt(
            (1 - lhs_samples[mask_upper]) * (param.max_value - param.min_value) * (param.max_value - param.mode)
        )
        
        return samples
    
    def _transform_discrete(self, lhs_samples: np.ndarray, param: ParameterDistribution) -> np.ndarray:
        """Transforma amostras LHS para valores discretos."""
        n_values = len(param.discrete_values)
        
        # Divide [0,1] em n_values intervalos iguais
        indices = np.floor(lhs_samples * n_values).astype(int)
        indices = np.clip(indices, 0, n_values - 1)
        
        return np.array([param.discrete_values[i] for i in indices])


def generate_sample_matrix(n_samples: int = 500) -> pd.DataFrame:
    """
    Gera matriz de amostras para todos os parâmetros.
    
    Args:
        n_samples: Número de simulações a gerar
    
    Returns:
        DataFrame com amostras de todos os parâmetros
    """
    sampler = LHSSampler(ALL_PARAMETERS, n_samples)
    samples_df = sampler.generate_samples()
    
    # Adiciona coluna de ID da simulação
    samples_df.insert(0, 'sim_id', range(1, n_samples + 1))
    
    return samples_df


def save_samples(samples_df: pd.DataFrame, output_path: str):
    """Salva matriz de amostras em CSV."""
    samples_df.to_csv(output_path, index=False)
    print(f"✓ Matriz de amostras salva: {output_path}")


def load_samples(input_path: str) -> pd.DataFrame:
    """Carrega matriz de amostras de CSV."""
    return pd.read_csv(input_path)


if __name__ == "__main__":
    # Teste: gera e visualiza amostras
    print("Gerando amostras LHS para análise de sensibilidade...")
    samples = generate_sample_matrix(n_samples=500)
    
    print(f"\nMatriz de amostras: {samples.shape}")
    print(f"\nPrimeiras 5 simulações:")
    print(samples.head())
    
    print(f"\nEstatísticas das amostras:")
    print(samples.describe())
    
    # Salva amostras
    save_samples(samples, "results/lhs_samples.csv")

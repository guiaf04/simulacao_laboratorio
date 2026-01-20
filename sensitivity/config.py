"""
Configuração de parâmetros para análise de sensibilidade do laboratório UFC Quixadá.

Adaptado para análise de incertezas operacionais e construtivas em edifício existente.
Foco: sistema de refrigeração apenas (clima semiárido quente).
"""

from dataclasses import dataclass
from typing import Literal
from pathlib import Path
import os


@dataclass
class ParameterDistribution:
    """Define distribuição de probabilidade para um parâmetro."""
    name: str
    distribution: Literal['normal', 'triangular', 'uniform', 'discrete']
    min_value: float
    max_value: float
    mean: float = None  # Para Normal
    std: float = None   # Para Normal
    mode: float = None  # Para Triangular
    discrete_values: list = None  # Para Discrete
    unit: str = ""
    description: str = ""


# ==================== VARIÁVEIS INDEPENDENTES ====================

# Grupo A: Envelope (Fachada Oeste é crítica em Quixadá)
ABSORTANCIA_PAREDE = ParameterDistribution(
    name='absortancia_parede',
    distribution='normal',
    min_value=0.3,
    max_value=0.9,
    mean=0.6,  # Assumindo cor mediana
    std=0.1,
    unit='adimensional',
    description='Absortância solar da parede externa (desbotamento/sujeira)'
)

FATOR_SOLAR_VIDRO = ParameterDistribution(
    name='fator_solar_vidro',
    distribution='normal',
    min_value=0.77,
    max_value=0.97,
    mean=0.87,  # Vidro simples claro
    std=0.05,
    unit='SHGC',
    description='Fator solar do vidro (incerteza de especificação)'
)

INFILTRACAO_AR = ParameterDistribution(
    name='infiltracao_ar',
    distribution='triangular',
    min_value=0.3,
    max_value=1.0,
    mode=0.5,
    unit='ACH',
    description='Infiltração de ar (frestas em portas/janelas)'
)

USO_CORTINAS = ParameterDistribution(
    name='uso_cortinas',
    distribution='discrete',
    min_value=0,
    max_value=1,
    discrete_values=[0, 1],  # 0=sem cortina, 1=com cortina
    unit='0/1',
    description='Presença de persianas internas'
)

# Grupo B: Cargas Internas (vilão do laboratório)
DENSIDADE_EQUIPAMENTOS = ParameterDistribution(
    name='densidade_equipamentos',
    distribution='triangular',
    min_value=5.0,   # Lab vazio/ocioso
    max_value=25.0,  # Lab lotado, tudo ligado
    mode=15.0,       # Uso típico
    unit='W/m²',
    description='Densidade de potência de equipamentos (PCs, projetores)'
)

OCUPACAO = ParameterDistribution(
    name='ocupacao',
    distribution='triangular',
    min_value=0.10,  # ~10 pessoas em 66m²
    max_value=0.45,  # ~30 pessoas em 66m²
    mode=0.30,       # ~20 pessoas
    unit='pessoas/m²',
    description='Densidade de ocupação (alunos)'
)

# Grupo C: Sistema de Ar Condicionado
SETPOINT_RESFRIAMENTO = ParameterDistribution(
    name='setpoint_resfriamento',
    distribution='uniform',
    min_value=20.0,
    max_value=25.0,
    unit='°C',
    description='Temperatura de setpoint do AC (comportamento do usuário)'
)

COP_AC = ParameterDistribution(
    name='cop_ac',
    distribution='normal',
    min_value=2.4,
    max_value=3.6,
    mean=3.0,
    std=0.3,
    unit='W/W',
    description='Coeficiente de performance (estado de conservação)'
)

CONDUTIVIDADE_PAREDE = ParameterDistribution(
    name='condutividade_parede',
    distribution='normal',
    min_value=0.7,
    max_value=1.3,
    mean=1.0,  # Típico para reboco+tijolo cerâmico
    std=0.15,
    unit='W/(m·K)',
    description='Condutividade térmica da parede (incerteza de material)'
)

# Lista completa de parâmetros
ALL_PARAMETERS = [
    ABSORTANCIA_PAREDE,
    FATOR_SOLAR_VIDRO,
    INFILTRACAO_AR,
    USO_CORTINAS,
    DENSIDADE_EQUIPAMENTOS,
    OCUPACAO,
    SETPOINT_RESFRIAMENTO,
    COP_AC,
    CONDUTIVIDADE_PAREDE,
]

# ==================== VARIÁVEIS DEPENDENTES ====================

DEPENDENT_VARIABLES = {
    'consumo_anual_resfriamento': {
        'output_var': 'Cooling:Electricity',
        'aggregation': 'sum',
        'unit': 'kWh/ano',
        'description': 'Consumo anual de eletricidade para refrigeração'
    },
    'carga_pico_resfriamento': {
        'output_var': 'Zone Air System Sensible Cooling Rate',
        'aggregation': 'max',
        'unit': 'kW',
        'description': 'Carga térmica de pico para dimensionamento'
    },
    'horas_desconforto': {
        'output_var': 'Zone Operative Temperature',
        'aggregation': 'count_above_threshold',
        'threshold': 26.0,
        'unit': 'horas',
        'description': 'Horas acima de 26°C (AC insuficiente)'
    }
}

# ==================== CONFIGURAÇÕES DA SIMULAÇÃO ====================

# Diretório base do projeto (parent do diretório sensitivity)
_BASE_DIR = Path(__file__).parent.parent.resolve()

# Capacidade total dos 2 ACs de 30.000 BTU/h cada
CAPACIDADE_AC_TOTAL = 17600  # W (≈60.000 BTU/h = 17,58 kW)

# Número de simulações para LHS
NUM_SIMULATIONS = 500  # Seguindo o artigo

# Arquivo IDF base
BASE_IDF_PATH = str(_BASE_DIR / 'models' / 'laboratorio_6zonas.idf')

# Diretório de resultados
RESULTS_DIR = str(_BASE_DIR / 'results' / 'sensitivity_analysis')

# Arquivo climático
WEATHER_FILE = str(_BASE_DIR / 'weather' / 'Quixada_UFC.epw')

# Seeds para reprodutibilidade
RANDOM_SEED = 42

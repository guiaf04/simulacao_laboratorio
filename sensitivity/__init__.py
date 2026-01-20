"""
Pacote de análise de sensibilidade para simulação térmica.

Análise de sensibilidade global de parâmetros termofísicos usando:
- Latin Hypercube Sampling (LHS)
- Standardized Regression Coefficients (SRC)
- Partial Correlation Coefficients (PCC)
"""

__version__ = "1.0.0"
__author__ = "Grupo 2 - UFC Quixadá"

from .config import (
    ALL_PARAMETERS,
    DEPENDENT_VARIABLES,
    NUM_SIMULATIONS,
    BASE_IDF_PATH,
    RESULTS_DIR,
    WEATHER_FILE,
)

from .sampling import generate_sample_matrix, LHSSampler
from .idf_modifier import IDFModifier, create_simulation_idf
from .simulation import SimulationRunner, run_sensitivity_simulations
from .results import ResultsExtractor, extract_all_results, merge_inputs_outputs
from .analysis import SensitivityAnalyzer, run_sensitivity_analysis
from .visualization import SensitivityVisualizer, create_all_plots

__all__ = [
    'ALL_PARAMETERS',
    'DEPENDENT_VARIABLES',
    'generate_sample_matrix',
    'run_sensitivity_simulations',
    'extract_all_results',
    'run_sensitivity_analysis',
    'create_all_plots',
]

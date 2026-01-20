"""
Executor de simulações EnergyPlus em lote para análise de sensibilidade.

Gerencia múltiplas simulações com controle de erros e progresso.
"""

import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm


class SimulationRunner:
    """Executa simulações EnergyPlus em paralelo."""
    
    def __init__(self, energyplus_path: Optional[str] = None, weather_file: str = None):
        self.energyplus_path = self._find_energyplus(energyplus_path)
        self.weather_file = weather_file
    
    def _find_energyplus(self, custom_path: Optional[str]) -> str:
        """Localiza executável do EnergyPlus."""
        if custom_path and Path(custom_path).exists():
            return custom_path
        
        # Locais comuns do EnergyPlus
        possible_paths = [
            r"C:\EnergyPlusV25-1-0\energyplus.exe",
            r"C:\EnergyPlusV24-2-0\energyplus.exe",
            r"C:\EnergyPlusV23-2-0\energyplus.exe",
            "/usr/local/EnergyPlus/energyplus",
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        raise FileNotFoundError(
            "EnergyPlus não encontrado. Especifique o caminho manualmente."
        )
    
    def run_simulation(self, idf_path: str, output_dir: str, 
                      weather_file: Optional[str] = None) -> Dict:
        """
        Executa uma simulação EnergyPlus.
        
        Args:
            idf_path: Caminho do arquivo IDF
            output_dir: Diretório de saída
            weather_file: Arquivo climático EPW (opcional)
        
        Returns:
            Dicionário com status e caminhos de resultado
        """
        idf_path = Path(idf_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Validações
        if not idf_path.exists():
            return {
                'success': False,
                'output_dir': str(output_dir),
                'error': f'Arquivo IDF não encontrado: {idf_path}'
            }
        
        weather = weather_file or self.weather_file
        if not weather:
            return {
                'success': False,
                'output_dir': str(output_dir),
                'error': 'Arquivo climático não especificado'
            }
        
        if not Path(weather).exists():
            return {
                'success': False,
                'output_dir': str(output_dir),
                'error': f'Arquivo climático não encontrado: {weather}'
            }
        
        # Comando EnergyPlus
        cmd = [
            str(self.energyplus_path),
            "-w", str(weather),
            "-d", str(output_dir),
            str(idf_path)
        ]
        
        # Executa simulação
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            # Verifica se simulação foi bem-sucedida
            err_file = output_dir / "eplusout.err"
            success = self._check_simulation_success(err_file)
            
            return {
                'success': success,
                'output_dir': str(output_dir),
                'err_file': str(err_file),
                'returncode': result.returncode,
                'stdout': result.stdout[:1000] if not success else '',  # Limita log
                'stderr': result.stderr[:1000] if not success else '',
            }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output_dir': str(output_dir),
                'error': 'Timeout - simulação excedeu 5 minutos'
            }
        
        except Exception as e:
            return {
                'success': False,
                'output_dir': str(output_dir),
                'error': str(e)
            }
    
    def _check_simulation_success(self, err_file: Path) -> bool:
        """Verifica se simulação foi bem-sucedida analisando arquivo .err."""
        if not err_file.exists():
            return False
        
        with open(err_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Procura por indicadores de sucesso/falha
        if "EnergyPlus Completed Successfully" in content:
            return True
        
        if any(x in content for x in ["Fatal", "Severe", "** Severe **"]):
            # Verifica número de erros severos
            severe_count = content.count("** Severe  **")
            if severe_count > 5:  # Mais de 5 erros severos = falha
                return False
        
        # Se chegou ao final sem fatal, considera sucesso
        if "EnergyPlus Completed" in content:
            return True
        
        return False
    
    def run_batch(self, simulations: List[Dict], max_workers: int = 4) -> pd.DataFrame:
        """
        Executa múltiplas simulações em paralelo.
        
        Args:
            simulations: Lista de dicts com {sim_id, idf_path, output_dir}
            max_workers: Número de processos paralelos
        
        Returns:
            DataFrame com resultados de todas as simulações
        """
        results = []
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submete todas as simulações
            futures = {
                executor.submit(
                    self.run_simulation,
                    sim['idf_path'],
                    sim['output_dir'],
                    self.weather_file
                ): sim['sim_id']
                for sim in simulations
            }
            
            # Processa resultados conforme completam
            with tqdm(total=len(simulations), desc="Simulações") as pbar:
                for future in as_completed(futures):
                    sim_id = futures[future]
                    try:
                        result = future.result()
                        result['sim_id'] = sim_id
                        results.append(result)
                    except Exception as e:
                        results.append({
                            'sim_id': sim_id,
                            'success': False,
                            'error': str(e)
                        })
                    pbar.update(1)
        
        return pd.DataFrame(results)


def run_sensitivity_simulations(samples_df: pd.DataFrame, base_idf: str, 
                                output_base_dir: str, weather_file: str,
                                max_workers: int = 4) -> pd.DataFrame:
    """
    Executa todas as simulações da análise de sensibilidade.
    
    Args:
        samples_df: DataFrame com amostras LHS
        base_idf: Caminho do IDF base
        output_base_dir: Diretório base para outputs
        weather_file: Arquivo climático
        max_workers: Processos paralelos
    
    Returns:
        DataFrame com status das simulações
    """
    from .idf_modifier import create_simulation_idf
    
    print(f"\n{'='*60}")
    print(f"Iniciando {len(samples_df)} simulações - {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"{'='*60}\n")
    
    # Validações iniciais
    if not Path(base_idf).exists():
        raise FileNotFoundError(f"Arquivo IDF base não encontrado: {base_idf}")
    
    if not Path(weather_file).exists():
        raise FileNotFoundError(f"Arquivo climático não encontrado: {weather_file}")
    
    print(f"✓ IDF base: {base_idf}")
    print(f"✓ Arquivo climático: {weather_file}")
    
    # Prepara lista de simulações
    simulations = []
    failed_idf_creation = []
    
    print("\nCriando arquivos IDF modificados...")
    for idx, row in tqdm(samples_df.iterrows(), total=len(samples_df), desc="IDF"):
        sim_id = int(row['sim_id'])  # Converte para int
        params = row.drop('sim_id').to_dict()
        
        output_dir = Path(output_base_dir) / f"sim_{sim_id:04d}"
        
        try:
            idf_path = create_simulation_idf(sim_id, params, base_idf, output_base_dir)
            if Path(idf_path).exists():
                simulations.append({
                    'sim_id': sim_id,
                    'idf_path': idf_path,
                    'output_dir': str(output_dir)
                })
            else:
                failed_idf_creation.append(sim_id)
                print(f"✗ IDF {sim_id} não foi criado")
        except Exception as e:
            failed_idf_creation.append(sim_id)
            print(f"✗ Erro ao criar IDF {sim_id}: {e}")
    
    if failed_idf_creation:
        print(f"\n⚠ Atenção: {len(failed_idf_creation)} IDFs não foram criados")
        print(f"  IDs: {failed_idf_creation[:10]}{'...' if len(failed_idf_creation) > 10 else ''}")
    
    if not simulations:
        raise RuntimeError("Nenhum IDF foi criado com sucesso. Verifique o arquivo base e os parâmetros.")
    
    print(f"\n✓ {len(simulations)} IDFs criados com sucesso")
    
    # Executa simulações
    print(f"\nExecutando simulações (paralelo: {max_workers} workers)...")
    runner = SimulationRunner(weather_file=weather_file)
    results_df = runner.run_batch(simulations, max_workers=max_workers)
    
    # Resumo
    n_success = results_df['success'].sum()
    n_failed = len(results_df) - n_success
    
    print(f"\n{'='*60}")
    print(f"Simulações concluídas:")
    print(f"  ✓ Sucesso: {n_success}/{len(results_df)}")
    print(f"  ✗ Falhas: {n_failed}/{len(results_df)}")
    print(f"{'='*60}\n")
    
    return results_df


if __name__ == "__main__":
    # Teste com simulação única
    print("Testando execução de simulação...")
    
    runner = SimulationRunner(weather_file='weather/Quixada_UFC.epw')
    
    result = runner.run_simulation(
        idf_path='models/laboratorio_6zonas.idf',
        output_dir='results/test_run'
    )
    
    print(f"\nResultado: {result}")

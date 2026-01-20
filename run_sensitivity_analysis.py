"""
Script principal para análise de sensibilidade do laboratório UFC Quixadá.

Workflow de SIMULAÇÃO:
1. Gerar amostras LHS
2. Criar IDFs modificados
3. Executar simulações EnergyPlus
4. Extrair resultados
5. Análise de sensibilidade

Para gerar TODOS os gráficos e relatórios, use:
    python generate_all_reports.py results/sensitivity_analysis/[timestamp]

Uso:
    python run_sensitivity_analysis.py --all --n-samples 200 --workers 4
    python run_sensitivity_analysis.py --samples-only --n-samples 500
    python run_sensitivity_analysis.py --analyze results/sensitivity_analysis/complete_data.csv
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Adiciona diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent))

from sensitivity import (
    generate_sample_matrix,
    run_sensitivity_simulations,
    extract_all_results,
    merge_inputs_outputs,
    run_sensitivity_analysis,
    ALL_PARAMETERS,
    DEPENDENT_VARIABLES,
    NUM_SIMULATIONS,
    BASE_IDF_PATH,
    RESULTS_DIR,
    WEATHER_FILE,
)


def run_full_workflow(n_samples: int = NUM_SIMULATIONS, max_workers: int = 4):
    """
    Executa workflow completo de análise de sensibilidade.
    
    Args:
        n_samples: Número de simulações
        max_workers: Processos paralelos
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(RESULTS_DIR) / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*80}")
    print(f"ANÁLISE DE SENSIBILIDADE - LABORATÓRIO UFC QUIXADÁ")
    print(f"{'='*80}")
    print(f"Timestamp: {timestamp}")
    print(f"Simulações: {n_samples}")
    print(f"Diretório: {output_dir}")
    print(f"{'='*80}\n")
    
    # Etapa 1: Gerar amostras LHS
    print("\n[1/6] Gerando amostras Latin Hypercube...")
    samples_df = generate_sample_matrix(n_samples)
    samples_path = output_dir / "lhs_samples.csv"
    samples_df.to_csv(samples_path, index=False)
    print(f"✓ Amostras salvas: {samples_path}")
    print(f"  Shape: {samples_df.shape}")
    
    # Etapa 2 & 3: Criar IDFs e executar simulações
    print("\n[2-3/6] Criando IDFs e executando simulações...")
    sim_results_df = run_sensitivity_simulations(
        samples_df=samples_df,
        base_idf=BASE_IDF_PATH,
        output_base_dir=str(output_dir / "simulations"),
        weather_file=WEATHER_FILE,
        max_workers=max_workers
    )
    
    sim_status_path = output_dir / "simulation_status.csv"
    sim_results_df.to_csv(sim_status_path, index=False)
    print(f"✓ Status das simulações: {sim_status_path}")
    
    # Etapa 4: Extrair resultados
    print("\n[4/6] Extraindo resultados...")
    results_df = extract_all_results(
        sim_results_df=sim_results_df,
        base_output_dir=str(output_dir / "simulations")
    )
    
    results_path = output_dir / "extracted_results.csv"
    results_df.to_csv(results_path, index=False)
    print(f"✓ Resultados extraídos: {results_path}")
    
    # Etapa 5: Merge e preparar dataset completo
    print("\n[5/6] Preparando dataset completo...")
    complete_data = merge_inputs_outputs(samples_df, results_df)
    
    complete_path = output_dir / "complete_data.csv"
    complete_data.to_csv(complete_path, index=False)
    print(f"✓ Dataset completo: {complete_path}")
    print(f"  Simulações válidas: {len(complete_data)}/{n_samples}")
    
    # Etapa 6: Análise de sensibilidade
    print("\n[6/6] Análise de sensibilidade...")
    analysis_results = run_sensitivity_analysis(
        data=complete_data,
        save_dir=str(output_dir / "sensitivity_indices")
    )
    # Nota: descriptive_statistics.csv já foi salvo dentro de run_sensitivity_analysis()
    
    # Resumo final
    print(f"\n{'='*80}")
    print("SIMULAÇÕES CONCLUÍDAS COM SUCESSO!")
    print(f"{'='*80}")
    print(f"\nResultados salvos em: {output_dir}")
    print(f"\nPara gerar TODOS os gráficos e relatórios, execute:")
    print(f"  python generate_all_reports.py {output_dir}")
    print(f"\n{'='*80}\n")
    
    return output_dir


def generate_samples_only(n_samples: int = NUM_SIMULATIONS, output_path: str = None):
    """Gera apenas amostras LHS (sem simulações)."""
    print(f"\nGerando {n_samples} amostras LHS...")
    samples_df = generate_sample_matrix(n_samples)
    
    if output_path is None:
        output_path = Path(RESULTS_DIR) / f"lhs_samples_{n_samples}.csv"
    
    samples_df.to_csv(output_path, index=False)
    print(f"✓ Amostras salvas: {output_path}")
    print(f"\nPrimeiras 5 amostras:")
    print(samples_df.head())
    print(f"\nEstatísticas:")
    print(samples_df.describe())


def analyze_existing_data(data_path: str):
    """Analisa dataset existente (pula simulações)."""
    import pandas as pd
    
    print(f"\nCarregando dataset: {data_path}")
    data = pd.read_csv(data_path)
    print(f"✓ Carregado: {data.shape}")
    
    output_dir = Path(data_path).parent / "analysis_results"
    output_dir.mkdir(exist_ok=True)
    
    # Análise
    print("\nExecutando análise de sensibilidade...")
    analysis_results = run_sensitivity_analysis(
        data=data,
        save_dir=str(output_dir / "sensitivity_indices")
    )
    
    print(f"\n✓ Análise concluída!")
    print(f"\nPara gerar gráficos e relatórios, execute:")
    print(f"  python generate_all_reports.py {output_dir.parent}")


def main():
    """Função principal com interface CLI."""
    parser = argparse.ArgumentParser(
        description="Análise de Sensibilidade - Laboratório UFC Quixadá",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python run_sensitivity_analysis.py --all
  python run_sensitivity_analysis.py --all --n-samples 100 --workers 8
  python run_sensitivity_analysis.py --samples-only --n-samples 500
  python run_sensitivity_analysis.py --analyze results/sensitivity_analysis/20250119_143000/complete_data.csv
        """
    )
    
    parser.add_argument('--all', action='store_true',
                       help='Executa workflow completo (amostras + simulações + análise)')
    parser.add_argument('--samples-only', action='store_true',
                       help='Gera apenas amostras LHS (sem simulações)')
    parser.add_argument('--analyze', type=str, metavar='CSV',
                       help='Analisa dataset existente (pula simulações)')
    
    parser.add_argument('--n-samples', type=int, default=NUM_SIMULATIONS,
                       help=f'Número de simulações (padrão: {NUM_SIMULATIONS})')
    parser.add_argument('--workers', type=int, default=4,
                       help='Processos paralelos para simulações (padrão: 4)')
    parser.add_argument('--output', type=str,
                       help='Caminho de saída customizado')
    
    args = parser.parse_args()
    
    # Validações
    if not any([args.all, args.samples_only, args.analyze]):
        parser.print_help()
        print("\n❌ Erro: Especifique --all, --samples-only ou --analyze")
        sys.exit(1)
    
    try:
        if args.all:
            run_full_workflow(n_samples=args.n_samples, max_workers=args.workers)
        
        elif args.samples_only:
            generate_samples_only(n_samples=args.n_samples, output_path=args.output)
        
        elif args.analyze:
            if not Path(args.analyze).exists():
                print(f"❌ Erro: Arquivo não encontrado: {args.analyze}")
                sys.exit(1)
            analyze_existing_data(args.analyze)
        
        print("\n✅ Processo concluído com sucesso!\n")
    
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

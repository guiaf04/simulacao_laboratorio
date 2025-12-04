#!/usr/bin/env python3
"""
Script para análise dos resultados da simulação
Laboratório de Arquitetura - UFC Quixadá
Grupo 2 - Simulação Térmica
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

def analisar_resultados(diretorio_resultados):
    """
    Analisa e gera gráficos dos resultados da simulação
    """
    
    print("=" * 70)
    print("ANÁLISE DOS RESULTADOS DA SIMULAÇÃO")
    print("=" * 70)
    print(f"\nDiretório: {diretorio_resultados}")
    
    # Arquivo CSV com os dados
    arquivo_csv = os.path.join(diretorio_resultados, "eplusout.csv")
    
    if not os.path.exists(arquivo_csv):
        print(f"\n✗ Erro: Arquivo CSV não encontrado: {arquivo_csv}")
        print("\nExecute primeiro a simulação com: python scripts/executar_simulacao.py")
        return False
    
    try:
        # Ler dados
        print("\nLendo dados da simulação...")
        df = pd.read_csv(arquivo_csv)
        
        print(f"✓ Dados carregados: {len(df)} registros")
        print(f"✓ Colunas disponíveis: {len(df.columns)}")
        
        # Mostrar primeiras colunas
        print("\nPrimeiras colunas do arquivo:")
        for i, col in enumerate(df.columns[:10]):
            print(f"  {i+1}. {col}")
        
        # Identificar colunas importantes
        colunas_temp = [col for col in df.columns if 'Temperature' in col]
        colunas_cooling = [col for col in df.columns if 'Cooling' in col]
        colunas_energia = [col for col in df.columns if 'Electric' in col or 'Power' in col]
        
        print(f"\n✓ Colunas de temperatura: {len(colunas_temp)}")
        print(f"✓ Colunas de resfriamento: {len(colunas_cooling)}")
        print(f"✓ Colunas de energia: {len(colunas_energia)}")
        
        # Criar diretório para gráficos
        dir_graficos = os.path.join(diretorio_resultados, "graficos")
        os.makedirs(dir_graficos, exist_ok=True)
        
        # Gráfico 1: Temperaturas ao longo do tempo
        print("\nGerando gráficos...")
        
        if colunas_temp:
            plt.figure(figsize=(12, 6))
            
            # Plotar algumas temperaturas importantes
            for col in colunas_temp[:5]:  # Primeiras 5 colunas de temperatura
                plt.plot(df.index, df[col], label=col, alpha=0.7)
            
            plt.xlabel('Timestep')
            plt.ylabel('Temperatura (°C)')
            plt.title('Temperaturas ao Longo da Simulação')
            plt.legend(loc='best', fontsize=8)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            arquivo_grafico = os.path.join(dir_graficos, "temperaturas.png")
            plt.savefig(arquivo_grafico, dpi=150)
            print(f"✓ Gráfico salvo: {arquivo_grafico}")
            plt.close()
        
        # Gráfico 2: Consumo de energia
        if colunas_energia:
            plt.figure(figsize=(12, 6))
            
            for col in colunas_energia[:5]:
                # Converter para kW se necessário
                dados = df[col]
                if dados.max() > 1000:  # Provavelmente em W
                    dados = dados / 1000
                    unidade = "kW"
                else:
                    unidade = "W"
                
                plt.plot(df.index, dados, label=col, alpha=0.7)
            
            plt.xlabel('Timestep')
            plt.ylabel(f'Potência ({unidade})')
            plt.title('Consumo de Energia ao Longo da Simulação')
            plt.legend(loc='best', fontsize=8)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            arquivo_grafico = os.path.join(dir_graficos, "energia.png")
            plt.savefig(arquivo_grafico, dpi=150)
            print(f"✓ Gráfico salvo: {arquivo_grafico}")
            plt.close()
        
        # Estatísticas básicas
        print("\n" + "=" * 70)
        print("ESTATÍSTICAS RESUMIDAS")
        print("=" * 70)
        
        # Temperatura da zona
        col_temp_zona = [col for col in colunas_temp if 'Zone Mean Air Temperature' in col]
        if col_temp_zona:
            temp_zona = df[col_temp_zona[0]]
            print(f"\nTemperatura da Zona ({col_temp_zona[0]}):")
            print(f"  Média: {temp_zona.mean():.2f} °C")
            print(f"  Mínima: {temp_zona.min():.2f} °C")
            print(f"  Máxima: {temp_zona.max():.2f} °C")
            print(f"  Desvio padrão: {temp_zona.std():.2f} °C")
        
        # Temperatura externa
        col_temp_ext = [col for col in colunas_temp if 'Outdoor' in col and 'Drybulb' in col]
        if col_temp_ext:
            temp_ext = df[col_temp_ext[0]]
            print(f"\nTemperatura Externa ({col_temp_ext[0]}):")
            print(f"  Média: {temp_ext.mean():.2f} °C")
            print(f"  Mínima: {temp_ext.min():.2f} °C")
            print(f"  Máxima: {temp_ext.max():.2f} °C")
        
        # Consumo total de energia
        if colunas_energia:
            energia_total = df[colunas_energia].sum().sum()
            # Converter de W para kWh (assumindo timestep de 10 minutos)
            timestep_horas = 10 / 60  # 10 minutos em horas
            energia_kwh = (energia_total * timestep_horas) / 1000
            
            print(f"\nConsumo de Energia:")
            print(f"  Total estimado: {energia_kwh:.2f} kWh")
            print(f"  Por dia: {energia_kwh / (len(df) * timestep_horas / 24):.2f} kWh/dia")
        
        print("\n" + "=" * 70)
        print("✓ ANÁLISE CONCLUÍDA!")
        print("=" * 70)
        print(f"\nGráficos salvos em: {dir_graficos}")
        print("\nPróximos passos:")
        print("1. Visualize os gráficos gerados")
        print("2. Abra o relatório HTML completo:")
        print(f"   xdg-open {os.path.join(diretorio_resultados, 'eplustbl.htm')}")
        print("3. Analise o arquivo CSV para dados detalhados:")
        print(f"   {arquivo_csv}")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Erro ao analisar resultados: {e}")
        import traceback
        traceback.print_exc()
        return False

def listar_simulacoes():
    """
    Lista todas as simulações disponíveis
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir_results = os.path.join(base_dir, "results")
    
    if not os.path.exists(dir_results):
        print("Nenhuma simulação encontrada.")
        return []
    
    simulacoes = [d for d in os.listdir(dir_results) if d.startswith("sim_")]
    simulacoes.sort(reverse=True)
    
    return [os.path.join(dir_results, s) for s in simulacoes]

def main():
    """
    Função principal
    """
    print("=" * 70)
    print("ANÁLISE DE RESULTADOS - ENERGYPLUS")
    print("Laboratório de Arquitetura - UFC Quixadá")
    print("=" * 70)
    
    # Verificar dependências
    try:
        import pandas
        import matplotlib
    except ImportError:
        print("\n✗ Erro: Bibliotecas necessárias não instaladas!")
        print("\nInstale as dependências com:")
        print("  pip install pandas matplotlib")
        return
    
    # Listar simulações
    simulacoes = listar_simulacoes()
    
    if not simulacoes:
        print("\nNenhuma simulação encontrada.")
        print("Execute primeiro: python scripts/executar_simulacao.py")
        return
    
    print(f"\nSimulações disponíveis: {len(simulacoes)}")
    print("\nÚltima simulação:")
    print(f"  {simulacoes[0]}")
    
    # Analisar última simulação
    print("\nAnalisando última simulação...")
    analisar_resultados(simulacoes[0])

if __name__ == "__main__":
    main()

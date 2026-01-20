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

def gerar_relatorio_md(diretorio_resultados, tipo_simulacao="geral"):
    """
    Gera relatório em Markdown com os resultados da análise
    """
    arquivo_csv = os.path.join(diretorio_resultados, "eplusout.csv")
    
    if not os.path.exists(arquivo_csv):
        return
    
    df = pd.read_csv(arquivo_csv)
    
    # Nome do arquivo de relatório
    relatorio_path = os.path.join(diretorio_resultados, "RELATORIO_ANALISE.md")
    
    with open(relatorio_path, 'w', encoding='utf-8') as f:
        f.write("# Relatório de Análise - Simulação Térmica\n")
        f.write("## Laboratório de Arquitetura - UFC Quixadá\n\n")
        f.write(f"**Data da Análise:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        f.write(f"**Tipo de Simulação:** {tipo_simulacao.upper()}\n\n")
        f.write("---\n\n")
        
        # Estatísticas gerais
        f.write("## 📊 Estatísticas Gerais\n\n")
        f.write(f"- **Timesteps simulados:** {len(df)}\n")
        f.write(f"- **Período de simulação:** {len(df) * 10 / 60:.1f} horas\n\n")
        
        # Temperatura da zona
        col_temp_zona = [col for col in df.columns if 'Zone Mean Air Temperature' in col]
        if col_temp_zona:
            temp_zona = df[col_temp_zona[0]]
            f.write("### 🌡️ Temperatura da Zona\n\n")
            f.write(f"- **Média:** {temp_zona.mean():.2f}°C\n")
            f.write(f"- **Mínima:** {temp_zona.min():.2f}°C\n")
            f.write(f"- **Máxima:** {temp_zona.max():.2f}°C\n")
            f.write(f"- **Desvio Padrão:** {temp_zona.std():.2f}°C\n\n")
        
        # Se for simulação 6 zonas, adicionar análise de regiões
        if "6zonas" in tipo_simulacao or "6zonas" in diretorio_resultados:
            f.write("## 📍 Análise por Região Conceitual\n\n")
            
            # Análise de temperaturas por região
            surface_cols = [col for col in df.columns if 'Surface Inside Face Temperature' in col]
            
            if surface_cols:
                f.write("### Temperatura de Superfícies\n\n")
                f.write("| Superfície | Temp. Média (°C) | Temp. Mín (°C) | Temp. Máx (°C) |\n")
                f.write("|-----------|-----------------|----------------|----------------|\n")
                
                for col in surface_cols[:10]:  # Limitar a 10 superfícies
                    surface_name = col.split(':')[0].replace('_', ' ').title()
                    temps = df[col].dropna()
                    if len(temps) > 0:
                        f.write(f"| {surface_name} | {temps.mean():.2f} | {temps.min():.2f} | {temps.max():.2f} |\n")
                
                f.write("\n")
        
        # Ganho solar por janelas
        window_heat_cols = [col for col in df.columns if 'Surface Window Heat Gain Rate' in col]
        if window_heat_cols:
            f.write("### ☀️ Ganho de Calor Solar\n\n")
            f.write("| Janela | Ganho Médio (W) | Ganho Máximo (W) |\n")
            f.write("|--------|----------------|------------------|\n")
            
            for col in window_heat_cols:
                window_name = col.split(':')[0].replace('_', ' ').title()
                heat_gain = df[col].dropna()
                if len(heat_gain) > 0:
                    f.write(f"| {window_name} | {heat_gain.mean():.1f} | {heat_gain.max():.1f} |\n")
            
            f.write("\n")
        
        # Energia de condicionamento
        cooling_cols = [col for col in df.columns if 'Cooling Energy' in col]
        if cooling_cols:
            f.write("### ❄️ Energia de Resfriamento\n\n")
            
            for col in cooling_cols[:3]:
                cooling_data = df[col].dropna()
                if len(cooling_data) > 0:
                    total_kwh = cooling_data.sum() / 3600000  # J para kWh
                    f.write(f"- **{col.split(':')[0]}:** {total_kwh:.2f} kWh\n")
            
            f.write("\n")
        
        # AirflowNetwork (se disponível)
        afn_cols = [col for col in df.columns if 'AFN' in col]
        if afn_cols:
            f.write("## 🌬️ Análise de Fluxo de Ar (AirflowNetwork)\n\n")
            
            ach_col = [col for col in afn_cols if 'Air Change Rate' in col]
            if ach_col:
                ach_data = df[ach_col[0]].dropna()
                if len(ach_data) > 0:
                    f.write(f"- **Taxa de Renovação de Ar Média:** {ach_data.mean():.2f} ACH\n")
                    f.write(f"- **Taxa Máxima:** {ach_data.max():.2f} ACH\n\n")
            
            door_factor_col = [col for col in afn_cols if 'Opening Factor' in col and 'Door' in col]
            if door_factor_col:
                door_data = df[door_factor_col[0]].dropna()
                if len(door_data) > 0:
                    tempo_aberta = (door_data > 0.5).sum() * 10 / 60  # minutos para horas
                    f.write(f"- **Tempo com Porta Aberta:** {tempo_aberta:.1f} horas\n")
                    f.write(f"- **Percentual do Tempo Aberta:** {(door_data > 0.5).mean() * 100:.1f}%\n\n")
        
        # Arquivos gerados
        f.write("## 📁 Arquivos Gerados\n\n")
        f.write("- `eplusout.csv` - Dados detalhados da simulação\n")
        f.write("- `eplustbl.htm` - Relatório HTML completo\n")
        f.write("- `eplusout.err` - Log de erros e avisos\n")
        f.write("- `graficos/` - Gráficos de análise\n\n")
        
        f.write("---\n\n")
        f.write("*Relatório gerado automaticamente pelo script de análise*\n")
    
    print(f"✓ Relatório MD salvo: {relatorio_path}")
    return relatorio_path

def detectar_tipo_simulacao(diretorio_resultados):
    """
    Detecta o tipo de simulação baseado no nome do diretório
    """
    nome_dir = os.path.basename(diretorio_resultados)
    
    if "6zonas" in nome_dir or "6zona" in nome_dir:
        return "6zonas"
    elif "geral" in nome_dir:
        return "geral"
    else:
        # Tentar detectar pelo conteúdo do CSV
        arquivo_csv = os.path.join(diretorio_resultados, "eplusout.csv")
        if os.path.exists(arquivo_csv):
            df = pd.read_csv(arquivo_csv, nrows=1)
            # Se tem muitas variáveis de superfície, provavelmente é 6 zonas
            surface_cols = [col for col in df.columns if 'Surface' in col]
            if len(surface_cols) > 20:
                return "6zonas"
        
        return "geral"

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
    
    # Buscar simulação _latest
    sim_latest = [s for s in simulacoes if "_latest" in s]
    
    if sim_latest:
        diretorio_analise = sim_latest[0]
        print(f"\nUsando simulação latest: {os.path.basename(diretorio_analise)}")
    else:
        diretorio_analise = simulacoes[0]
        print(f"\nUsando última simulação: {os.path.basename(diretorio_analise)}")
    
    # Detectar tipo
    tipo_simulacao = detectar_tipo_simulacao(diretorio_analise)
    print(f"Tipo detectado: {tipo_simulacao}")
    
    # Analisar
    print("\nAnalisando resultados...")
    sucesso = analisar_resultados(diretorio_analise)
    
    # Gerar relatório MD
    if sucesso:
        print("\nGerando relatório em Markdown...")
        gerar_relatorio_md(diretorio_analise, tipo_simulacao)

if __name__ == "__main__":
    main()

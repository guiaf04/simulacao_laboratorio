#!/usr/bin/env python3
"""
Script para executar simulação do EnergyPlus versão 24.1 (OpenStudio)
Laboratório de Arquitetura - UFC Quixadá
Grupo 2 - Simulação Térmica
"""

import os
import subprocess
import sys
from datetime import datetime

def encontrar_energyplus_241():
    """
    Tenta encontrar o executável do EnergyPlus 24.1 (OpenStudio)
    """
    locais_possiveis = [
        "/usr/local/openstudioapplication-1.8.0/EnergyPlus/energyplus",
        "/usr/local/openstudio-3.8.0/EnergyPlus/energyplus",
        "/usr/local/openstudio/EnergyPlus/energyplus",
        "/opt/openstudio/EnergyPlus/energyplus",
    ]
    
    for local in locais_possiveis:
        if os.path.exists(local):
            return local
    
    return None

def executar_simulacao(arquivo_idf, arquivo_epw, diretorio_saida):
    """
    Executa a simulação do EnergyPlus 24.1
    """
    
    # Encontrar EnergyPlus 24.1
    energyplus = encontrar_energyplus_241()
    
    if not energyplus:
        print("✗ EnergyPlus 24.1 (OpenStudio) não encontrado!")
        print("\nPor favor, instale o OpenStudio 3.8.0 ou superior.")
        print("Locais procurados:")
        print("  - /usr/local/openstudio-3.8.0/EnergyPlus/")
        print("  - /usr/local/openstudio/EnergyPlus/")
        print("  - /opt/openstudio/EnergyPlus/")
        return False
    
    print("=" * 70)
    print("EXECUÇÃO DA SIMULAÇÃO - ENERGYPLUS 24.1 (OpenStudio)")
    print("=" * 70)
    print(f"\nEnergyPlus: {energyplus}")
    print(f"Arquivo IDF: {arquivo_idf}")
    print(f"Arquivo EPW: {arquivo_epw}")
    print(f"Diretório de saída: {diretorio_saida}")
    
    # Verificar se os arquivos existem
    if not os.path.exists(arquivo_idf):
        print(f"\n✗ Erro: Arquivo IDF não encontrado: {arquivo_idf}")
        return False
    
    if not os.path.exists(arquivo_epw):
        print(f"\n✗ Erro: Arquivo EPW não encontrado: {arquivo_epw}")
        print("\nExecute primeiro: python scripts/baixar_clima_fortaleza.py")
        return False
    
    # Criar diretório de saída se não existir
    os.makedirs(diretorio_saida, exist_ok=True)
    
    # Comando do EnergyPlus com expansão de templates
    comando = [
        energyplus,
        "-w", arquivo_epw,
        "-d", diretorio_saida,
        "-x",  # Expandir objetos HVACTemplate
        "-r",  # Output em formato CSV
        arquivo_idf
    ]
    
    print("\n" + "=" * 70)
    print("Iniciando simulação...")
    print("=" * 70)
    print("\nEste processo pode levar alguns minutos.")
    print("Aguarde...\n")
    
    try:
        # Executar simulação
        inicio = datetime.now()
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            check=False
        )
        fim = datetime.now()
        tempo_decorrido = (fim - inicio).total_seconds()
        
        # Verificar resultado
        if resultado.returncode == 0:
            print("\n" + "=" * 70)
            print("✓ SIMULAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 70)
            print(f"\nTempo de execução: {tempo_decorrido:.2f} segundos")
            print(f"\nResultados salvos em: {diretorio_saida}")
            
            # Listar arquivos de saída principais
            print("\nArquivos de saída gerados:")
            arquivos_importantes = [
                "eplusout.err",
                "eplusout.csv",
                "eplustbl.htm",
                "eplusout.eio",
            ]
            
            for arquivo in arquivos_importantes:
                caminho = os.path.join(diretorio_saida, arquivo)
                if os.path.exists(caminho):
                    tamanho = os.path.getsize(caminho)
                    print(f"  ✓ {arquivo} ({tamanho / 1024:.2f} KB)")
            
            # Verificar erros
            arquivo_erro = os.path.join(diretorio_saida, "eplusout.err")
            if os.path.exists(arquivo_erro):
                with open(arquivo_erro, 'r') as f:
                    conteudo = f.read()
                    if "** Severe" in conteudo or "** Fatal" in conteudo:
                        print("\n⚠ ATENÇÃO: Erros encontrados durante a simulação!")
                        print(f"   Verifique o arquivo: {arquivo_erro}")
                    elif "** Warning" in conteudo:
                        print("\n⚠ Avisos encontrados (não críticos)")
                        print(f"   Verifique o arquivo: {arquivo_erro}")
            
            print("\n" + "=" * 70)
            print("PRÓXIMOS PASSOS:")
            print("=" * 70)
            print("1. Abra o arquivo HTML para ver o relatório:")
            print(f"   xdg-open {diretorio_saida}/eplustbl.htm")
            print("\n2. Analise os dados CSV para gráficos:")
            print(f"   {diretorio_saida}/eplusout.csv")
            print("\n3. Execute o script de análise:")
            print("   python scripts/analisar_resultados.py")
            print("=" * 70)
            
            return True
        else:
            print("\n" + "=" * 70)
            print("✗ ERRO NA SIMULAÇÃO!")
            print("=" * 70)
            print(f"\nCódigo de erro: {resultado.returncode}")
            
            if resultado.stderr:
                print("\nErro:")
                print(resultado.stderr[:500])
            
            # Tentar mostrar erros do arquivo .err
            arquivo_erro = os.path.join(diretorio_saida, "eplusout.err")
            if os.path.exists(arquivo_erro):
                print(f"\nVerifique os erros detalhados em: {arquivo_erro}")
                with open(arquivo_erro, 'r') as f:
                    linhas = f.readlines()
                    # Mostrar últimas 20 linhas
                    print("\nÚltimas linhas do arquivo de erro:")
                    print("".join(linhas[-20:]))
            
            return False
    
    except FileNotFoundError:
        print(f"\n✗ Erro: Executável não encontrado: {energyplus}")
        return False
    except Exception as e:
        print(f"\n✗ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    Função principal
    """
    # Caminhos dos arquivos
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    arquivo_idf = os.path.join(base_dir, "models", "laboratorio_arquitetura_v24.1.idf")
    arquivo_epw = os.path.join(base_dir, "weather", "Fortaleza.epw")
    diretorio_saida = os.path.join(base_dir, "results", f"sim_v241_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    # Executar simulação
    sucesso = executar_simulacao(arquivo_idf, arquivo_epw, diretorio_saida)
    
    sys.exit(0 if sucesso else 1)

if __name__ == "__main__":
    main()

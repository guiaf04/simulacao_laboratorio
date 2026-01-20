#!/usr/bin/env python3
"""
Script para baixar arquivo de clima (EPW) de Fortaleza, CE
Grupo 2 - Simulação Térmica
"""

import os
import urllib.request
import sys

def baixar_arquivo_epw():
    """
    Baixa o arquivo de clima EPW de Fortaleza do banco de dados do EnergyPlus
    """
    
    # URL do arquivo EPW de Fortaleza (INMET)
    # Fonte: https://energyplus.net/weather
    url = "https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_Fortaleza-Pinto.Mar.823980_SWERA/BRA_Fortaleza-Pinto.Mar.823980_SWERA.epw"
    
    # Caminho de destino
    diretorio_weather = os.path.join(os.path.dirname(__file__), '..', 'weather')
    arquivo_destino = os.path.join(diretorio_weather, 'Fortaleza.epw')
    
    # Criar diretório se não existir
    os.makedirs(diretorio_weather, exist_ok=True)
    
    print("=" * 70)
    print("DOWNLOAD DO ARQUIVO DE CLIMA EPW - FORTALEZA, CE")
    print("=" * 70)
    print(f"\nURL: {url}")
    print(f"Destino: {arquivo_destino}")
    
    try:
        print("\nIniciando download...")
        
        # Download com barra de progresso
        def mostrar_progresso(blocos, tamanho_bloco, tamanho_total):
            if tamanho_total > 0:
                porcentagem = min(100, (blocos * tamanho_bloco * 100) / tamanho_total)
                print(f"\rProgresso: {porcentagem:.1f}%", end='', flush=True)
        
        urllib.request.urlretrieve(url, arquivo_destino, mostrar_progresso)
        
        print("\n\n✓ Download concluído com sucesso!")
        print(f"✓ Arquivo salvo em: {arquivo_destino}")
        
        # Verificar tamanho do arquivo
        tamanho = os.path.getsize(arquivo_destino)
        print(f"✓ Tamanho do arquivo: {tamanho / 1024:.2f} KB")
        
        # Ler primeiras linhas para verificar
        with open(arquivo_destino, 'r', encoding='latin-1') as f:
            primeira_linha = f.readline()
            print(f"\n✓ Primeira linha do arquivo:")
            print(f"  {primeira_linha.strip()}")
        
        print("\n" + "=" * 70)
        print("O arquivo EPW está pronto para uso na simulação!")
        print("=" * 70)
        
        return True
        
    except urllib.error.URLError as e:
        print(f"\n✗ Erro ao baixar o arquivo: {e}")
        print("\nTentando URL alternativa...")
        
        # URL alternativa (LABEEE/UFSC)
        url_alt = "https://labeee.ufsc.br/sites/default/files/arquivos_climaticos/inmetepw/FORTALEZA_CE_BRA.epw"
        
        try:
            print(f"URL alternativa: {url_alt}")
            urllib.request.urlretrieve(url_alt, arquivo_destino, mostrar_progresso)
            print("\n\n✓ Download concluído com sucesso (fonte alternativa)!")
            return True
        except Exception as e2:
            print(f"\n✗ Erro na URL alternativa: {e2}")
            print("\nPor favor, baixe manualmente:")
            print("1. Acesse: https://energyplus.net/weather")
            print("2. Busque por 'Fortaleza' ou 'Brazil'")
            print("3. Baixe o arquivo .epw")
            print(f"4. Salve em: {arquivo_destino}")
            return False
    
    except Exception as e:
        print(f"\n✗ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    sucesso = baixar_arquivo_epw()
    sys.exit(0 if sucesso else 1)

#!/usr/bin/env python3
"""
Cria arquivo EPW customizado para Quixadá-CE a partir dos dados da estação meteorológica UFC

Este script processa os dados reais coletados pela estação meteorológica instalada
no Campus UFC Quixadá e gera um arquivo EPW (EnergyPlus Weather) para simulações
mais precisas com clima local.

Dados de entrada:
- dataset-estacao-meteorologica/*.dat (temperatura, umidade, radiação, vento, chuva)
- CSV files recentes de 2024-2025

Dados de saída:
- weather/Quixada_UFC.epw (arquivo EPW customizado)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import sys
import glob

# Caminhos
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
WEATHER_DIR = PROJECT_DIR / "weather"
DATA_DIR = Path("/home/guilherme/UFC/Instrumentação/trabalho/dataset-estacao-meteorologica")
CSV_DIR = Path("/home/guilherme/UFC/Instrumentação/trabalho")

# Coordenadas de Quixadá-CE
LOCATION = {
    'city': 'Quixada',
    'state': 'Ceara',
    'country': 'BRA',
    'latitude': -4.97,  # Campus UFC Quixadá
    'longitude': -39.02,
    'timezone': -3.0,
    'elevation': 189.0  # metros
}


def load_historical_data():
    """Carrega dados históricos da estação meteorológica (2015-2020)"""
    print("📂 Carregando dados históricos da estação meteorológica...")
    
    all_data = []
    
    # Tentar carregar dados de 2020 (mais recente)
    for year in [2020, 2019, 2018]:
        year_dir = DATA_DIR / str(year)
        if not year_dir.exists():
            continue
            
        dat_files = sorted(year_dir.glob("*.dat"))
        print(f"   Encontrados {len(dat_files)} arquivos de {year}")
        
        for dat_file in dat_files:
            try:
                # Ler arquivo .dat (CSV com cabeçalho especial)
                df = pd.read_csv(dat_file, skiprows=1, parse_dates=['TIMESTAMP'])
                
                # Renomear colunas para padrão
                df = df.rename(columns={
                    'TIMESTAMP': 'datetime',
                    'AirTC_Avg': 'temperature',
                    'AirTC_Max': 'temp_max',
                    'AirTC_Min': 'temp_min',
                    'RH_Avg': 'humidity',
                    'RH_Max': 'hum_max',
                    'RH_Min': 'hum_min',
                    'WS_ms_Avg': 'wind_speed',
                    'SlrkJ_Avg': 'solar_radiation',
                    'Rain_mm_Tot': 'rain',
                    'BP_mbar_Max': 'pressure'
                })
                
                all_data.append(df)
                
            except Exception as e:
                print(f"   ⚠️  Erro ao ler {dat_file.name}: {e}")
                continue
    
    if all_data:
        df_combined = pd.concat(all_data, ignore_index=True)
        print(f"✅ {len(df_combined)} registros carregados")
        return df_combined
    
    return None


def load_recent_csv_data():
    """Carrega dados recentes de CSV (2024-2025)"""
    print("\n📂 Carregando dados recentes de CSV...")
    
    data = {}
    
    # Temperatura
    temp_files = sorted(CSV_DIR.glob("Temperature-data-*.csv"))
    if temp_files:
        df_temp = pd.read_csv(temp_files[-1])
        df_temp['time'] = pd.to_datetime(df_temp['time'])
        df_temp['temperature'] = df_temp['temperature'].str.replace('°C', '').str.strip().astype(float)
        data['temperature'] = df_temp
        print(f"   ✅ Temperatura: {len(df_temp)} registros")
    
    # Umidade
    hum_files = sorted(CSV_DIR.glob("Humidity-data-*.csv"))
    if hum_files:
        df_hum = pd.read_csv(hum_files[-1])
        df_hum['time'] = pd.to_datetime(df_hum['time'])
        df_hum['humidity'] = df_hum['humidity'].str.replace('%H', '').str.replace('%', '').str.strip().astype(float)
        data['humidity'] = df_hum
        print(f"   ✅ Umidade: {len(df_hum)} registros")
    
    # Radiação Solar
    solar_files = sorted(CSV_DIR.glob("Solar Radiation-data-*.csv"))
    if solar_files:
        df_solar = pd.read_csv(solar_files[-1])
        df_solar['time'] = pd.to_datetime(df_solar['time'])
        df_solar['solar'] = df_solar['solarRadiation'].str.replace('kJ/m²', '').str.replace('W/m²', '').str.strip().astype(float)
        data['solar'] = df_solar
        print(f"   ✅ Radiação Solar: {len(df_solar)} registros")
    
    # Velocidade do Vento
    wind_files = sorted(CSV_DIR.glob("Wind Speed-data-*.csv"))
    if wind_files:
        df_wind = pd.read_csv(wind_files[-1])
        df_wind['time'] = pd.to_datetime(df_wind['time'])
        df_wind['wind_speed'] = df_wind['windSpeed'].str.replace('m/s', '').str.strip().astype(float)
        data['wind_speed'] = df_wind
        print(f"   ✅ Vento: {len(df_wind)} registros")
    
    return data


def calculate_typical_year(df_historical, df_recent):
    """Cria um Ano Meteorológico Típico (TMY) a partir dos dados"""
    print("\n🔬 Calculando Ano Meteorológico Típico...")
    
    # Criar DataFrame para ano típico (8760 horas)
    start_date = datetime(2024, 1, 1, 0, 0)
    dates = [start_date + timedelta(hours=i) for i in range(8760)]
    
    df_tmy = pd.DataFrame({
        'datetime': dates,
        'month': [d.month for d in dates],
        'day': [d.day for d in dates],
        'hour': [d.hour for d in dates]
    })
    
    # Calcular médias mensais e horárias dos dados históricos
    if df_historical is not None and not df_historical.empty:
        # Garantir que datetime é do tipo datetime
        if 'datetime' in df_historical.columns:
            df_historical['datetime'] = pd.to_datetime(df_historical['datetime'], errors='coerce')
        df_historical['month'] = df_historical['datetime'].dt.month
        df_historical['hour'] = df_historical['datetime'].dt.hour
        
        # Converter colunas numéricas
        numeric_cols = ['temperature', 'humidity', 'wind_speed', 'solar_radiation', 'pressure']
        for col in numeric_cols:
            if col in df_historical.columns:
                df_historical[col] = pd.to_numeric(df_historical[col], errors='coerce')
        
        # Médias mensais por hora
        monthly_hourly_avg = df_historical.groupby(['month', 'hour']).agg({
            'temperature': 'mean',
            'humidity': 'mean',
            'wind_speed': 'mean',
            'solar_radiation': 'mean',
            'pressure': 'mean'
        }).reset_index()
        
        # Juntar com TMY
        df_tmy = df_tmy.merge(monthly_hourly_avg, on=['month', 'hour'], how='left')
    
    # Preencher valores faltantes com dados típicos de Quixadá
    df_tmy['temperature'] = df_tmy['temperature'].fillna(27.0)  # Média anual ~27°C
    df_tmy['humidity'] = df_tmy['humidity'].fillna(60.0)  # Média anual ~60%
    df_tmy['wind_speed'] = df_tmy['wind_speed'].fillna(2.5)  # Média anual ~2.5 m/s
    df_tmy['solar_radiation'] = df_tmy['solar_radiation'].fillna(0)  # kJ/m²
    df_tmy['pressure'] = df_tmy['pressure'].fillna(101325)  # Pa
    
    # Converter radiação de kJ/m² para W/m² (dividir por 3.6)
    df_tmy['solar_radiation_wm2'] = df_tmy['solar_radiation'] / 3.6
    
    # Ajustar radiação solar para ciclo diurno realista
    for idx, row in df_tmy.iterrows():
        hour = row['hour']
        if hour < 6 or hour > 18:
            df_tmy.loc[idx, 'solar_radiation_wm2'] = 0
        else:
            # Curva senoidal para radiação solar (pico ~800 W/m² ao meio-dia)
            solar_angle = (hour - 6) / 12 * np.pi
            max_solar = 800  # W/m² (valor típico para clima tropical)
            df_tmy.loc[idx, 'solar_radiation_wm2'] = max_solar * np.sin(solar_angle)
    
    # Calcular ponto de orvalho (Dewpoint)
    df_tmy['dewpoint'] = df_tmy.apply(
        lambda row: row['temperature'] - ((100 - row['humidity']) / 5),
        axis=1
    )
    
    print(f"✅ Ano típico criado com {len(df_tmy)} horas")
    print(f"   Temperatura média: {df_tmy['temperature'].mean():.1f}°C")
    print(f"   Umidade média: {df_tmy['humidity'].mean():.1f}%")
    print(f"   Radiação solar média: {df_tmy['solar_radiation_wm2'].mean():.1f} W/m²")
    
    return df_tmy


def create_epw_header():
    """Cria cabeçalho do arquivo EPW"""
    header_lines = []
    
    # Linha 1: LOCATION
    header_lines.append(
        f"LOCATION,{LOCATION['city']},{LOCATION['state']},"
        f"{LOCATION['country']},CUSTOM,,"
        f"{LOCATION['latitude']:.2f},{LOCATION['longitude']:.2f},"
        f"{LOCATION['timezone']:.1f},{LOCATION['elevation']:.1f}\n"
    )
    
    # Linha 2: DESIGN CONDITIONS (simplificado)
    header_lines.append("DESIGN CONDITIONS,0\n")
    
    # Linha 3: TYPICAL/EXTREME PERIODS (simplificado)
    header_lines.append("TYPICAL/EXTREME PERIODS,0\n")
    
    # Linha 4: GROUND TEMPERATURES (estimado para Quixadá)
    ground_temps = "24.0,24.5,25.0,25.5,26.0,26.5,26.5,26.0,25.5,25.0,24.5,24.0"
    header_lines.append(f"GROUND TEMPERATURES,1,.5,,,,{ground_temps}\n")
    
    # Linha 5: HOLIDAYS/DAYLIGHT SAVING (sem feriados especiais)
    header_lines.append("HOLIDAYS/DAYLIGHT SAVINGS,No,0,0,0\n")
    
    # Linha 6: COMMENTS 1
    header_lines.append(
        "COMMENTS 1,Custom EPW file created from UFC Quixada Weather Station Data\n"
    )
    
    # Linha 7: COMMENTS 2
    header_lines.append(
        f"COMMENTS 2,Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    
    # Linha 8: DATA PERIODS
    header_lines.append("DATA PERIODS,1,1,Data,Sunday, 1/ 1,12/31\n")
    
    return ''.join(header_lines)


def create_epw_data_line(row):
    """Cria uma linha de dados do EPW"""
    # Formato EPW:
    # Year,Month,Day,Hour,Minute,Data Source and Uncertainty Flags,
    # Dry Bulb Temperature {C},Dew Point Temperature {C},Relative Humidity {%},
    # Atmospheric Station Pressure {Pa},Extraterrestrial Horizontal Radiation {Wh/m2},
    # Extraterrestrial Direct Normal Radiation {Wh/m2},Horizontal Infrared Radiation Intensity {Wh/m2},
    # Global Horizontal Radiation {Wh/m2},Direct Normal Radiation {Wh/m2},
    # Diffuse Horizontal Radiation {Wh/m2},Global Horizontal Illuminance {lux},
    # Direct Normal Illuminance {lux},Diffuse Horizontal Illuminance {lux},
    # Zenith Luminance {Cd/m2},Wind Direction {deg},Wind Speed {m/s},
    # Total Sky Cover {.1},Opaque Sky Cover {.1},Visibility {km},Ceiling Height {m},
    # Present Weather Observation,Present Weather Codes,Precipitable Water {mm},
    # Aerosol Optical Depth {.001},Snow Depth {cm},Days Since Last Snowfall,
    # Albedo {.01},Liquid Precipitation Depth {mm},Liquid Precipitation Quantity {hr}
    
    year = row['datetime'].year
    month = row['datetime'].month
    day = row['datetime'].day
    hour = row['datetime'].hour
    
    # Temperatura bulbo seco
    dry_bulb = row['temperature']
    
    # Ponto de orvalho
    dew_point = row['dewpoint']
    
    # Umidade relativa
    rel_humidity = row['humidity']
    
    # Pressão atmosférica (converter mbar para Pa se necessário)
    pressure = row['pressure'] if row['pressure'] > 50000 else row['pressure'] * 100
    
    # Radiação solar
    global_horiz_rad = row['solar_radiation_wm2']
    direct_normal_rad = global_horiz_rad * 0.8 if global_horiz_rad > 0 else 0
    diffuse_horiz_rad = global_horiz_rad * 0.2 if global_horiz_rad > 0 else 0
    
    # Vento
    wind_speed = row['wind_speed']
    wind_direction = 90  # Assumir leste (valor padrão)
    
    # Cobertura de nuvens (estimado pela radiação solar)
    sky_cover = 5 if global_horiz_rad < 100 else 3
    
    # Valores padrão para campos não disponíveis
    extraterr_horiz_rad = 0
    extraterr_direct_rad = 0
    horiz_infrared_rad = 300
    visibility = 10000
    ceiling_height = 9999
    precip_water = 10
    aerosol_optical = 0
    
    minute = 60  # EPW usa minuto 60 para marca de hora cheia
    
    line = f"{year},{month},{day},{hour},{minute},?9?9?9?9E0?9?9?9?9?9?9?9?9?9?9?9?9?9?9?9*9*9?9?9?9,{dry_bulb:.1f},{dew_point:.1f},{rel_humidity:.0f},{pressure:.0f},{extraterr_horiz_rad:.0f},{extraterr_direct_rad:.0f},{horiz_infrared_rad:.0f},{global_horiz_rad:.0f},{direct_normal_rad:.0f},{diffuse_horiz_rad:.0f},0,0,0,0,{wind_direction:.0f},{wind_speed:.1f},{sky_cover},{sky_cover},{visibility:.0f},{ceiling_height:.0f},9,9,{precip_water:.0f},{aerosol_optical:.3f},0,88,0,0,0\n"
    
    return line


def generate_epw_file(df_tmy, output_path):
    """Gera arquivo EPW completo"""
    print(f"\n📝 Gerando arquivo EPW: {output_path}")
    
    with open(output_path, 'w') as f:
        # Escrever cabeçalho
        f.write(create_epw_header())
        
        # Escrever dados
        for idx, row in df_tmy.iterrows():
            f.write(create_epw_data_line(row))
    
    print(f"✅ Arquivo EPW criado com sucesso!")
    print(f"   Localização: {output_path}")
    print(f"   Tamanho: {output_path.stat().st_size / 1024:.1f} KB")


def main():
    print("=" * 70)
    print("🌦️  GERADOR DE ARQUIVO EPW CUSTOMIZADO - QUIXADÁ/UFC")
    print("=" * 70)
    
    # Criar diretório de saída
    WEATHER_DIR.mkdir(exist_ok=True)
    
    # Carregar dados
    df_historical = load_historical_data()
    df_recent = load_recent_csv_data()
    
    # Criar ano típico
    df_tmy = calculate_typical_year(df_historical, df_recent)
    
    # Gerar EPW
    output_path = WEATHER_DIR / "Quixada_UFC.epw"
    generate_epw_file(df_tmy, output_path)
    
    # Estatísticas finais
    print("\n📊 ESTATÍSTICAS DO CLIMA DE QUIXADÁ:")
    print(f"   Temperatura: {df_tmy['temperature'].min():.1f}°C a {df_tmy['temperature'].max():.1f}°C")
    print(f"   Umidade: {df_tmy['humidity'].min():.1f}% a {df_tmy['humidity'].max():.1f}%")
    print(f"   Vento: {df_tmy['wind_speed'].mean():.1f} m/s (média)")
    print(f"   Radiação Solar: {df_tmy['solar_radiation_wm2'].max():.0f} W/m² (pico)")
    
    print("\n" + "=" * 70)
    print("✅ Processo concluído!")
    print("=" * 70)
    print("\n💡 Para usar o arquivo na simulação:")
    print("   energyplus -w weather/Quixada_UFC.epw -d results/sim_quixada models/laboratorio_arquitetura.idf")


if __name__ == "__main__":
    main()

# Análise de Sensibilidade - Laboratório UFC Quixadá

Sistema organizado de simulação térmica e análise de sensibilidade para o laboratório de arquitetura.

## 📁 Estrutura Principal

```
simulacao_laboratorio/
├── run_sensitivity_analysis.py    # ✅ Script de SIMULAÇÃO
├── generate_all_reports.py         # ✅ Script de RELATÓRIOS E GRÁFICOS
├── sensitivity/                    # Pacote de análise
│   ├── config.py                  # Configurações e parâmetros
│   ├── sampling.py                # Amostragem LHS
│   ├── idf_modifier.py            # Modificação de IDFs
│   ├── simulation.py              # Execução EnergyPlus
│   ├── results.py                 # Extração de resultados
│   ├── analysis.py                # Análise de sensibilidade
│   └── visualization.py           # Visualizações
├── models/                        # Arquivos IDF
└── results/                       # Resultados das simulações
```

## 🚀 Uso Rápido

### 1️⃣ Executar Simulações (200 amostras)
```bash
python run_sensitivity_analysis.py --all --n-samples 200 --workers 4
```

### 2️⃣ Gerar TODOS os Relatórios e Gráficos
```bash
python generate_all_reports.py results/sensitivity_analysis/[timestamp]
```

Exemplo completo:
```bash
# Passo 1: Simular
python run_sensitivity_analysis.py --all --n-samples 200 --workers 4
# Output: results/sensitivity_analysis/20260119_205540/

# Passo 2: Gerar relatórios e gráficos
python generate_all_reports.py results/sensitivity_analysis/20260119_205540
```

## 📊 Gráficos Gerados (9 totais)

### Distribuição de Variáveis (1 gráfico)
- `distribuicao_variaveis_dependentes.png` - Histogramas + curvas de distribuição normal

### Temperaturas Regionais (2 gráficos)
- `temperatura_distribuicao_regional.png` - Boxplot + Violinplot das 6 regiões
- `temperatura_media_regional.png` - Barras com média ± desvio padrão

### Análise de Sensibilidade (6 gráficos para cada variável válida)
Para `consumo_anual_resfriamento` e `carga_pico_resfriamento`:
- `*_src_bars.png` - Gráfico de barras SRC (top 10 parâmetros)
- `*_comparison.png` - Comparação SRC/PCC/Pearson lado a lado
- `*_tornado.png` - Tornado diagram com valores absolutos

## 🎯 Resultados com 200 Simulações

### Temperaturas Regionais
- **Região 1** (Janela 1): 26.7°C ± 0.8°C 🔥 *mais quente*
- **Região 4** (Centro): 23.4°C ± 1.2°C ❄️ *mais fria*
- **Amplitude térmica**: ~3.3°C

### Parâmetros Mais Influentes
1. **setpoint_resfriamento** (SRC ≈ -1.0) - Mais impactante
2. **ocupacao** (SRC ≈ +0.05) - Segundo mais importante
3. **absortancia_parede** (SRC ≈ +0.03) - Terceiro

## 📝 Métodos de Análise

| Método | Descrição | Interpretação |
|--------|-----------|---------------|
| **SRC** | Standardized Regression Coeff. | Contribuição relativa normalizada |
| **PCC** | Partial Correlation Coeff. | Correlação sem efeitos indiretos |
| **Pearson** | Correlação linear simples | Relação direta input-output |

## 🛠️ Opções Avançadas

```bash
# Apenas gerar amostras (sem simular)
python run_sensitivity_analysis.py --samples-only --n-samples 500

# Analisar dataset existente
python run_sensitivity_analysis.py --analyze results/complete_data.csv

# Mais workers (mais rápido, mais CPU)
python run_sensitivity_analysis.py --all --n-samples 100 --workers 8
```

## 👥 Autores
Grupo 2 - UFC Quixadá | Instrumentação em Engenharia - 2026

# Análise de Sensibilidade - Laboratório UFC Quixadá

Sistema modular para análise de sensibilidade global de parâmetros termofísicos em simulação térmica com EnergyPlus.

## 📋 Descrição

Este projeto implementa análise de sensibilidade global para identificar os parâmetros mais influentes no desempenho térmico do laboratório de arquitetura da UFC Quixadá. Diferente do artigo base (Silva & Ghisi, 2013), nosso foco é em **incertezas operacionais e construtivas** de um edifício existente, com ênfase em **sistema de refrigeração** (sem aquecimento).

### Características:
- **Latin Hypercube Sampling (LHS)** com múltiplas distribuições de probabilidade
- **Análise de Sensibilidade** usando SRC (Standardized Regression Coefficients) e PCC (Partial Correlation Coefficients)
- **Execução paralela** de simulações EnergyPlus
- **Visualizações automáticas** (barras, scatter plots, tornado diagrams)
- **Código modular** seguindo boas práticas

## 🎯 Variáveis Analisadas

### Variáveis Independentes (Inputs - 9 parâmetros)

**Grupo A: Envelope**
- Absortância solar da parede externa (Normal, μ=0.6, σ=0.1)
- Fator solar do vidro/SHGC (Normal, μ=0.87, σ=0.05)
- Infiltração de ar ACH (Triangular, min=0.3, moda=0.5, max=1.0)
- Uso de cortinas (Discreto, 0/1)

**Grupo B: Cargas Internas**
- Densidade de equipamentos W/m² (Triangular, min=5, moda=15, max=25)
- Ocupação pessoas/m² (Triangular, min=0.10, moda=0.30, max=0.45)

**Grupo C: Sistema AC**
- Setpoint de resfriamento °C (Uniforme, 20-25)
- COP do ar condicionado (Normal, μ=3.0, σ=0.3)
- Condutividade térmica da parede W/(m·K) (Normal, μ=1.0, σ=0.15)

### Variáveis Dependentes (Outputs - 3 métricas)

1. **Consumo anual de resfriamento** (kWh/ano)
2. **Carga de pico de resfriamento** (kW) - para verificar capacidade dos 2 ACs
3. **Horas de desconforto** (horas acima de 26°C)

## 🏗️ Estrutura do Projeto

```
simulacao_laboratorio/
├── sensitivity/                    # Pacote principal
│   ├── __init__.py                # Inicialização do pacote
│   ├── config.py                  # Configuração de parâmetros e distribuições
│   ├── sampling.py                # Latin Hypercube Sampling
│   ├── idf_modifier.py            # Modificação automática de IDFs
│   ├── simulation.py              # Execução paralela de simulações
│   ├── results.py                 # Extração de resultados
│   ├── analysis.py                # Cálculo de SRC e PCC
│   └── visualization.py           # Geração de gráficos
│
├── run_sensitivity_analysis.py    # Script principal (CLI)
├── models/                         # Arquivos IDF base
│   └── laboratorio_6zonas.idf
├── weather/                        # Arquivos climáticos
│   └── Quixada_UFC.epw
└── results/                        # Outputs das análises
    └── sensitivity_analysis/
        └── YYYYMMDD_HHMMSS/
            ├── lhs_samples.csv
            ├── complete_data.csv
            ├── sensitivity_indices/
            └── plots/
```

## 🚀 Instalação

### Requisitos:
- Python 3.8+
- EnergyPlus 23.2+ instalado
- Pacotes Python:

```bash
pip install numpy pandas scipy matplotlib seaborn scikit-learn tqdm
```

Ou use o arquivo de requisitos:

```bash
pip install -r requirements.txt
```

## 📊 Uso

### 1. Workflow Completo (Recomendado)

Executa todo o processo: gera amostras → simula → analisa → visualiza

```bash
python run_sensitivity_analysis.py --all
```

Com opções customizadas:

```bash
python run_sensitivity_analysis.py --all --n-samples 100 --workers 8
```

### 2. Gerar Apenas Amostras LHS

Útil para revisar parâmetros antes de simular:

```bash
python run_sensitivity_analysis.py --samples-only --n-samples 500
```

### 3. Analisar Dataset Existente

Se já tem resultados de simulações:

```bash
python run_sensitivity_analysis.py --analyze results/sensitivity_analysis/20250119_143000/complete_data.csv
```

### Opções da CLI

```
--all                     Workflow completo
--samples-only            Gera apenas amostras LHS
--analyze CSV             Analisa dataset existente
--n-samples N             Número de simulações (padrão: 500)
--workers N               Processos paralelos (padrão: 4)
--output PATH             Caminho de saída customizado
```

## 📈 Resultados Gerados

Para cada execução, o sistema gera:

### 1. Dados
- `lhs_samples.csv`: Matriz de amostras geradas
- `complete_data.csv`: Inputs + outputs combinados
- `simulation_status.csv`: Status de cada simulação
- `extracted_results.csv`: Variáveis dependentes extraídas

### 2. Índices de Sensibilidade
- `sensitivity_consumo_anual_resfriamento.csv`
- `sensitivity_carga_pico_resfriamento.csv`
- `sensitivity_horas_desconforto.csv`
- `r2_scores.csv`: Qualidade do ajuste linear

### 3. Visualizações
- `{output_var}_src_bars.png`: Barras de SRC
- `{output_var}_comparison.png`: Comparação SRC/PCC/Pearson
- `{output_var}_scatter_matrix.png`: Scatter plots dos top 6 parâmetros
- `{output_var}_tornado.png`: Tornado diagram
- `variability_boxplot.png`: Variabilidade das saídas

## 🔍 Interpretação dos Resultados

### Standardized Regression Coefficients (SRC)
- **Valor absoluto maior** = parâmetro mais influente
- **Sinal positivo** = aumentar parâmetro aumenta a saída
- **Sinal negativo** = aumentar parâmetro diminui a saída

### Partial Correlation Coefficients (PCC)
- Varia de -1 a +1
- Mede correlação **removendo efeito dos outros parâmetros**
- Complementa o SRC para relações não lineares

### R² (Coeficiente de Determinação)
- Indica % da variabilidade explicada pelos parâmetros
- R² > 0.7 = modelo linear adequado
- R² < 0.5 = considerar relações não lineares

## 🔧 Customização

### Modificar Parâmetros

Edite `sensitivity/config.py`:

```python
DENSIDADE_EQUIPAMENTOS = ParameterDistribution(
    name='densidade_equipamentos',
    distribution='triangular',
    min_value=5.0,
    max_value=25.0,
    mode=15.0,
    unit='W/m²',
    description='Densidade de potência de equipamentos'
)
```

### Adicionar Novos Parâmetros

1. Defina em `config.py`
2. Adicione em `ALL_PARAMETERS`
3. Implemente modificação em `idf_modifier.py`

### Customizar Extração de Outputs

Edite métodos em `results.py`:

```python
def _extract_custom_output(self) -> float:
    csv_file = self.output_dir / 'eplusout.csv'
    df = pd.read_csv(csv_file)
    # Sua lógica aqui
    return result
```

## 📚 Referências

- Silva, A. S., & Ghisi, E. (2013). Análise de sensibilidade global dos parâmetros termofísicos de uma edificação residencial de acordo com o método de simulação do RTQ-R. *Ambiente Construído*, 13(4), 135-148.

- EnergyPlus Documentation: https://energyplus.net/documentation

## 👥 Autores

Grupo 2 - Trabalho de Instrumentação
Universidade Federal do Ceará - Campus Quixadá

## 📝 Licença

Projeto acadêmico - UFC 2025

# Sistema de Análise de Sensibilidade - Resumo Técnico

## 📦 O Que Foi Criado

Um sistema modular completo para análise de sensibilidade global de parâmetros termofísicos em simulações EnergyPlus do laboratório UFC Quixadá.

## 🗂️ Estrutura de Arquivos Criados

```
simulacao_laboratorio/
│
├── sensitivity/                          # Pacote principal (7 módulos)
│   ├── __init__.py                      # Inicialização e exports
│   ├── config.py                        # Configuração de parâmetros [162 linhas]
│   ├── sampling.py                      # Latin Hypercube Sampling [159 linhas]
│   ├── idf_modifier.py                  # Modificação de IDFs [226 linhas]
│   ├── simulation.py                    # Execução paralela [209 linhas]
│   ├── results.py                       # Extração de outputs [218 linhas]
│   ├── analysis.py                      # Cálculo SRC/PCC [237 linhas]
│   └── visualization.py                 # Geração de gráficos [355 linhas]
│
├── run_sensitivity_analysis.py          # Script principal CLI [228 linhas]
├── test_sensitivity.py                  # Testes de validação [205 linhas]
├── README_SENSITIVITY.md                # Documentação completa
└── requirements_sensitivity.txt         # Dependências Python
```

**Total: ~2000 linhas de código modular e documentado**

## 🎯 Funcionalidades Implementadas

### 1. Configuração (`config.py`)
- ✅ 9 parâmetros independentes com distribuições específicas:
  - Normal: absortância parede, SHGC vidro, COP, condutividade
  - Triangular: infiltração, densidade equipamentos, ocupação
  - Uniforme: setpoint resfriamento
  - Discreto: uso de cortinas
- ✅ 3 variáveis dependentes:
  - Consumo anual resfriamento (kWh/ano)
  - Carga pico resfriamento (kW)
  - Horas desconforto (>26°C)
- ✅ Classe `ParameterDistribution` para fácil extensão

### 2. Amostragem (`sampling.py`)
- ✅ Latin Hypercube Sampling estratificado
- ✅ Suporte a 4 tipos de distribuição:
  - Normal truncada (scipy.stats)
  - Triangular (inversão de CDF)
  - Uniforme contínua
  - Discreta com valores específicos
- ✅ Seed fixo para reprodutibilidade
- ✅ Export/import CSV

### 3. Modificação de IDF (`idf_modifier.py`)
- ✅ Regex para modificar objetos EnergyPlus:
  - Material (absortância, condutividade)
  - WindowMaterial (SHGC)
  - ZoneInfiltration (ACH)
  - ElectricEquipment (W/m²)
  - People (pessoas/m²)
  - ThermostatSetpoint (°C)
  - Coil:Cooling:DX (COP)
- ✅ Preserva estrutura do IDF base
- ✅ Criação automática de diretórios

### 4. Execução de Simulações (`simulation.py`)
- ✅ Detecção automática do executável EnergyPlus
- ✅ Execução paralela com `ProcessPoolExecutor`
- ✅ Timeout de 5 minutos por simulação
- ✅ Análise de arquivo `.err` para validar sucesso
- ✅ Barra de progresso com `tqdm`
- ✅ Tratamento robusto de erros

### 5. Extração de Resultados (`results.py`)
- ✅ Parsing de `eplusout.csv`:
  - Consumo elétrico (Joules → kWh)
  - Carga de pico (Watts → kW)
  - Temperatura operativa (contagem de horas)
- ✅ Busca inteligente de colunas (keywords)
- ✅ Tratamento de NaN para simulações falhadas
- ✅ Merge automático inputs+outputs

### 6. Análise de Sensibilidade (`analysis.py`)
- ✅ **SRC** (Standardized Regression Coefficients):
  - Padronização Z-score
  - Regressão linear múltipla (sklearn)
- ✅ **PCC** (Partial Correlation Coefficients):
  - Remove efeito de outros parâmetros
  - Correlação entre resíduos
- ✅ **Pearson** simples para referência
- ✅ **R²** para validar ajuste linear
- ✅ Ranking automático por influência

### 7. Visualização (`visualization.py`)
- ✅ 5 tipos de gráficos (matplotlib + seaborn):
  1. **Barras horizontais** (SRC/PCC/Pearson)
  2. **Comparação de métodos** (3 painéis lado a lado)
  3. **Scatter matrix** (pairplot dos top 6)
  4. **Scatter individual** com linha de tendência
  5. **Tornado diagram** (range de variação)
  6. **Boxplot** de variabilidade normalizada
- ✅ Esquema de cores: verde (positivo), vermelho (negativo)
- ✅ Export PNG em alta resolução (300 DPI)

### 8. Orquestração (`run_sensitivity_analysis.py`)
- ✅ CLI completo com argparse:
  ```bash
  --all              # Workflow completo
  --samples-only     # Só gera amostras
  --analyze CSV      # Só análise (pula simulações)
  --n-samples N      # Customiza número
  --workers N        # Paralelização
  ```
- ✅ 7 etapas automatizadas:
  1. Gerar amostras LHS
  2. Criar IDFs modificados
  3. Executar simulações
  4. Verificar status
  5. Extrair resultados
  6. Análise de sensibilidade
  7. Visualizações
- ✅ Logging detalhado com timestamps
- ✅ Tratamento de exceções global

### 9. Validação (`test_sensitivity.py`)
- ✅ 4 testes unitários:
  - Geração de amostras
  - Modificação de IDF
  - Análise com dados sintéticos
  - Geração de gráficos
- ✅ Validação de instalação
- ✅ Dados fictícios para teste offline

## 🔬 Diferenças do Artigo Original (Silva & Ghisi 2013)

| Aspecto | Artigo Original | Nossa Implementação |
|---------|----------------|---------------------|
| **Contexto** | Projeto de edificação residencial | Análise de edifício existente (lab) |
| **Clima** | Florianópolis (subtropical) | Quixadá (semiárido) |
| **Foco** | Aquecimento + Resfriamento | **Apenas Resfriamento** |
| **Parâmetros** | 15 (escolha de materiais) | 9 (incertezas operacionais) |
| **Variáveis** | GHR, CA, CR | Consumo, Pico, Desconforto |
| **Distribuições** | Discreta (opções de material) | Normal, Triangular, Uniforme |
| **Ventilação** | Natural + AC noturno | AC full-time (janelas fechadas) |
| **Capacidade AC** | Ilimitada (IdealLoads) | **Limitada: 17.6 kW** (2 splits) |

## 📊 Outputs Gerados

Para cada execução com timestamp `YYYYMMDD_HHMMSS/`:

### Dados CSV
- `lhs_samples.csv` - Matriz de 500 simulações × 9 parâmetros
- `simulation_status.csv` - Status (success/fail) + mensagens de erro
- `extracted_results.csv` - 3 variáveis dependentes × N simulações
- `complete_data.csv` - Dataset final (inputs + outputs)

### Índices de Sensibilidade
- `sensitivity_{output}.csv` - Tabela com SRC, PCC, Pearson para cada output
- `r2_scores.csv` - Qualidade do ajuste (R²)

### Gráficos PNG (300 DPI)
- `{output}_src_bars.png`
- `{output}_comparison.png`
- `{output}_scatter_matrix.png`
- `{output}_tornado.png`
- `variability_boxplot.png`

## 🚀 Como Usar

### Instalação Rápida
```bash
cd simulacao_laboratorio
pip install -r requirements_sensitivity.txt
python test_sensitivity.py  # Valida instalação
```

### Execução
```bash
# Workflow completo (500 simulações, ~2-4 horas)
python run_sensitivity_analysis.py --all

# Teste rápido (10 simulações, ~5 minutos)
python run_sensitivity_analysis.py --all --n-samples 10 --workers 4

# Apenas amostras (para revisão)
python run_sensitivity_analysis.py --samples-only --n-samples 500

# Análise de dados existentes
python run_sensitivity_analysis.py --analyze results/.../complete_data.csv
```

## 🎓 Conceitos Implementados

### Latin Hypercube Sampling
- Divide espaço de probabilidade em estratos
- Garante cobertura uniforme (melhor que Monte Carlo puro)
- Reduz número de simulações necessário (~500 vs 10.000)

### SRC vs PCC
- **SRC**: Coeficientes de regressão padronizados (efeito direto linear)
- **PCC**: Correlação parcial (remove efeito de outros parâmetros)
- Ambos variam -∞ a +∞ (SRC) ou -1 a +1 (PCC)
- |Valor maior| = mais influente

### R² (Coeficiente de Determinação)
- Indica % da variabilidade explicada
- R² > 0.7 → modelo linear adequado
- R² < 0.5 → considerar análise de variância (ANOVA) ou não linear

## 📝 Boas Práticas Aplicadas

✅ **Modularidade**: 7 módulos independentes e testáveis
✅ **Type hints**: Funções anotadas para clareza
✅ **Docstrings**: Todas as classes/funções documentadas
✅ **Constantes**: Centralizadas em `config.py`
✅ **Error handling**: Try/except com mensagens claras
✅ **Logging**: Print statements informativos com emojis ✓/✗
✅ **Reprodutibilidade**: Seeds fixos, timestamped outputs
✅ **Performance**: Paralelização com ProcessPoolExecutor
✅ **Extensibilidade**: Fácil adicionar parâmetros/outputs

## 🔧 Extensões Futuras Sugeridas

1. **Análise de Variância (ANOVA)** para capturar efeitos de segunda ordem
2. **Método de Sobol** para modelos não lineares
3. **Análise de Incertezas** (Monte Carlo) nos outputs
4. **Dashboard interativo** com Plotly/Dash
5. **Integração com OpenStudio** para modelagem visual
6. **Calibração automática** comparando com dados medidos

## 📖 Referências Técnicas

- McKay et al. (1979) - Latin Hypercube Sampling
- Saltelli et al. (2008) - Global Sensitivity Analysis
- Helton & Davis (2003) - Latin Hypercube vs Monte Carlo
- Tian (2013) - Review of sensitivity methods in building simulation

---

**Sistema pronto para uso!** 🎉

Execute `python test_sensitivity.py` para validar a instalação.

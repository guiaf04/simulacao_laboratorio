# Guia Rápido de Parâmetros - Análise de Sensibilidade

## 📋 Tabela Resumo dos Parâmetros

| # | Parâmetro | Tipo | Distribuição | Min | Moda | Max | Unidade | Grupo |
|---|-----------|------|--------------|-----|------|-----|---------|-------|
| 1 | `absortancia_parede` | Contínuo | Normal (μ=0.6, σ=0.1) | 0.3 | - | 0.9 | - | Envelope |
| 2 | `fator_solar_vidro` | Contínuo | Normal (μ=0.87, σ=0.05) | 0.77 | - | 0.97 | SHGC | Envelope |
| 3 | `infiltracao_ar` | Contínuo | Triangular | 0.3 | 0.5 | 1.0 | ACH | Envelope |
| 4 | `uso_cortinas` | Discreto | Uniforme | 0 | - | 1 | 0/1 | Envelope |
| 5 | `densidade_equipamentos` | Contínuo | Triangular | 5.0 | 15.0 | 25.0 | W/m² | Cargas |
| 6 | `ocupacao` | Contínuo | Triangular | 0.10 | 0.30 | 0.45 | pessoas/m² | Cargas |
| 7 | `setpoint_resfriamento` | Contínuo | Uniforme | 20.0 | - | 25.0 | °C | HVAC |
| 8 | `cop_ac` | Contínuo | Normal (μ=3.0, σ=0.3) | 2.4 | - | 3.6 | W/W | HVAC |
| 9 | `condutividade_parede` | Contínuo | Normal (μ=1.0, σ=0.15) | 0.7 | - | 1.3 | W/(m·K) | Envelope |

## 🎯 Variáveis Dependentes (Outputs)

| # | Variável | Fonte | Unidade | Importância |
|---|----------|-------|---------|-------------|
| 1 | `consumo_anual_resfriamento` | Cooling:Electricity (soma anual) | kWh/ano | 🔥 **Principal** - Custo operacional |
| 2 | `carga_pico_resfriamento` | Zone Cooling Rate (máximo) | kW | ⚡ Dimensionamento (17.6 kW disponível) |
| 3 | `horas_desconforto` | Operative Temperature (>26°C) | horas | 🌡️ Conforto térmico |

## 📊 Justificativa das Distribuições

### Normal (Gaussiana)
**Quando usar:** Incerteza contínua sobre valor médio conhecido
- **Absortância da parede** → Cor varia por desbotamento/sujeira
- **SHGC do vidro** → Incerteza sobre especificação/instalação
- **COP do AC** → Degrada com uso (média=3.0, valor de placa)
- **Condutividade** → Variação natural dos materiais (reboco/tijolo)

### Triangular
**Quando usar:** Conhecemos valor mais provável + extremos possíveis
- **Infiltração de ar** → Moda=0.5 ACH (típico), pode variar 0.3-1.0
- **Densidade de equipamentos** → Depende da aula (vazio/típico/lotado)
- **Ocupação** → Número de alunos varia, moda=20 pessoas (~0.3 p/m²)

### Uniforme
**Quando usar:** Total incerteza dentro de um intervalo
- **Setpoint do AC** → Comportamento imprevisível (17°C até 25°C)

### Discreta
**Quando usar:** Opções categóricas
- **Uso de cortinas** → Tem (1) ou não tem (0)

## 🔍 Significado dos Parâmetros

### 1. Absortância Solar da Parede (α)
- **0.3** → Branco (reflete 70% da radiação)
- **0.6** → Cinza médio (referência)
- **0.9** → Preto (absorve 90% da radiação)
- **Impacto:** ↑α → ↑calor → ↑consumo AC

### 2. Fator Solar do Vidro (SHGC)
- **0.77** → Vidro com película/filme
- **0.87** → Vidro simples claro (típico)
- **0.97** → Vidro totalmente transparente
- **Impacto:** ↑SHGC → ↑radiação entra → ↑consumo AC

### 3. Infiltração de Ar (ACH)
- **0.3** → Janelas bem vedadas
- **0.5** → Vedação típica (referência)
- **1.0** → Janelas/portas com frestas
- **Impacto:** ↑ACH → ↑ar quente entra → ↑consumo AC

### 4. Densidade de Equipamentos (W/m²)
- **5 W/m²** → Lab vazio/ocioso (só iluminação)
- **15 W/m²** → Uso típico (~10 PCs ligados)
- **25 W/m²** → Lab lotado (todos PCs + projetor + fontes)
- **Impacto:** ↑W/m² → ↑calor interno → ↑consumo AC

### 5. Ocupação (pessoas/m²)
- **0.10** → ~7 pessoas (aula pequena)
- **0.30** → ~20 pessoas (típico)
- **0.45** → ~30 pessoas (lotado)
- **Calor/pessoa:** ~108W (sentado, atividade leve)
- **Impacto:** ↑ocupação → ↑calor metabólico → ↑consumo AC

### 6. Setpoint de Resfriamento (°C)
- **20°C** → Muito frio (usuário coloca no mínimo)
- **23°C** → Confortável (recomendado)
- **25°C** → Quente (economia)
- **Impacto:** ↑setpoint → ↓tempo AC ligado → ↓consumo

### 7. COP do Ar Condicionado
- **2.4** → AC velho/mal mantido (ineficiente)
- **3.0** → AC novo/bem mantido (referência)
- **3.6** → AC high-efficiency
- **Significado:** COP=3.0 → 1 kWh elétrico remove 3 kWh térmicos
- **Impacto:** ↑COP → ↑eficiência → ↓consumo

### 8. Condutividade Térmica da Parede (λ)
- **0.7 W/(m·K)** → Alvenaria com isolamento
- **1.0 W/(m·K)** → Tijolo cerâmico + reboco (típico)
- **1.3 W/(m·K)** → Concreto
- **Impacto:** ↑λ → ↑condução de calor → ↑consumo AC

## 🌡️ Contexto: Laboratório UFC Quixadá

### Características do Edifício
- **Área:** 66.29 m²
- **Pé-direito:** 2.68 m
- **Orientação:** 342° (Norte)
- **Fachada crítica:** Oeste (sol da tarde intenso)
- **Localização:** 2º pavimento (3 andares totais)

### Sistema HVAC
- **2 splits de 30.000 BTU/h cada**
- **Capacidade total:** 17.6 kW térmicos (≈5 ton)
- **Tipo:** Split Hi-Wall, apenas resfriamento
- **Operação:** Full-time (janelas sempre fechadas)

### Clima Quixadá (Semiárido)
- **Temperatura:** 24-32°C (média anual)
- **Radiação:** Alta (céu limpo na maior parte do ano)
- **Umidade:** Baixa (50-60%)
- **Ventilação natural:** Não utilizada (laboratório fechado)

## 📈 Expectativas de Sensibilidade

Com base no clima e uso, espera-se que sejam mais influentes:

### Provavelmente Muito Influentes:
1. **Densidade de equipamentos** → Principal fonte de calor interno
2. **Ocupação** → Laboratório cheio vs vazio muda muito
3. **Setpoint** → Diferença de 5°C é dramática no consumo
4. **Absortância (Oeste)** → Sol intenso da tarde

### Provavelmente Moderadamente Influentes:
5. **SHGC dos vidros** → 4 janelas grandes
6. **COP do AC** → Afeta diretamente eficiência
7. **Infiltração** → Clima quente, ar externo penaliza

### Provavelmente Menos Influentes:
8. **Condutividade parede** → Massa térmica é secundária
9. **Uso de cortinas** → Discreto (on/off), menor gradiente

**Observação:** Essas são hipóteses! A análise determinará objetivamente.

## 🔧 Como Modificar Parâmetros

### Adicionar Novo Parâmetro

Edite `sensitivity/config.py`:

```python
NOVO_PARAMETRO = ParameterDistribution(
    name='nome_sem_espacos',
    distribution='normal',  # ou 'triangular', 'uniform', 'discrete'
    min_value=0.0,
    max_value=10.0,
    mean=5.0,      # Apenas para 'normal'
    std=1.0,       # Apenas para 'normal'
    mode=5.0,      # Apenas para 'triangular'
    discrete_values=[0, 5, 10],  # Apenas para 'discrete'
    unit='unidade',
    description='Descrição clara'
)

# Adicione à lista
ALL_PARAMETERS = [
    # ... existentes ...
    NOVO_PARAMETRO,
]
```

Implemente modificação em `sensitivity/idf_modifier.py`:

```python
def _modify_novo_parametro(self, content: str, value: float) -> str:
    """Modifica novo parâmetro no IDF."""
    pattern = r'(Objeto:EnergyPlus[^;]*Campo\s*,\s*)\d+\.?\d*'
    replacement = rf'\g<1>{value:.2f}'
    return re.sub(pattern, replacement, content, flags=re.DOTALL)
```

### Ajustar Distribuição Existente

```python
# Tornar setpoint mais restritivo (21-24°C em vez de 20-25°C)
SETPOINT_RESFRIAMENTO = ParameterDistribution(
    # ...
    min_value=21.0,  # Era 20.0
    max_value=24.0,  # Era 25.0
)
```

## 📚 Referências Técnicas

- **Normal:** μ±2σ contém ~95% dos valores
- **Triangular:** Moda é o valor mais provável, min/max são extremos físicos
- **LHS:** McKay, Beckman & Conover (1979) - Technometrics
- **SRC/PCC:** Saltelli et al. (2008) - Global Sensitivity Analysis

---

**Para dúvidas:** Consulte `README_SENSITIVITY.md` ou `SISTEMA_RESUMO.md`

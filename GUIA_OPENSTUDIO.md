# Guia do OpenStudio para o Modelo do Laboratório

## 📊 Modelos Disponíveis

### `laboratorio_arquitetura.idf` - Modelo Simples (1 Zona)
- Análise geral do laboratório
- Temperatura média da zona
- Melhor para análise rápida

### `laboratorio_6zonas.idf` - Análise de Gradiente Térmico ⭐ RECOMENDADO
- **Análise detalhada de distribuição de temperatura**
- Temperatura de superfícies em 6 regiões conceituais (2 colunas × 3 linhas):
  - **Região 1** (Frente-Esquerda): Próximo janela 1 + lousa
  - **Região 2** (Frente-Direita): Próximo porta + lousa  
  - **Região 3** (Centro-Esquerda): Próximo janela 2
  - **Região 4** (Centro-Direita): Centro da sala
  - **Região 5** (Fundo-Esquerda): Próximo janelas 3,4 + ACs
  - **Região 6** (Fundo-Direita): Próximo ACs
- **Outputs incluem:**
  - Temperatura interna de cada parede (esquerda com janelas, direita com porta, frente com lousa, fundo com ACs)
  - Temperatura de cada janela
  - Fluxo de calor solar por janelas
  - Radiação média da zona

## 📥 Importando o Arquivo IDF

1. Abra o **OpenStudio Application**
2. Vá em **File → Import → IDF**
3. Selecione o arquivo:
   - `models/laboratorio_arquitetura.idf` (modelo simples, 1 zona)
   - `models/laboratorio_6zonas.idf` (modelo detalhado, 6 zonas) ⭐
4. Clique em **Open**

### Objetos que serão importados automaticamente:
- ✅ Geometria (paredes, piso, teto, janelas, porta)
- ✅ Construções e materiais
- ✅ Zonas térmicas
- ✅ Cargas internas (People, Lights, Equipment)
- ✅ Schedules

### Objetos que precisam ser configurados no OpenStudio:
- ❌ Sistema HVAC (ar-condicionado)
- ❌ Termostatos
- ❌ Variáveis de saída

---

## ❄️ Configurando o HVAC no OpenStudio

### Método 1: Ideal Air Loads (Mais Simples)

1. Vá na aba **Thermal Zones**
2. Para cada zona, marque a opção **"Ideal Air Loads"** ✓
3. Configure o termostato:
   - **Cooling Setpoint:** 24°C
   - **Heating Setpoint:** 20°C (não usado em Quixadá)

### Método 2: Sistema HVAC Detalhado

1. Vá na aba **HVAC Systems**
2. Clique em **"+"** para adicionar um novo sistema
3. Selecione **"Packaged Rooftop Air Conditioner"** ou **"Split System"**
4. Arraste as zonas térmicas para o sistema
5. Configure a capacidade:
   - **Cooling Capacity:** 17,600 W (2× 30,000 BTU/h)
   - **COP:** 3.0 (eficiência)

---

## 🌡️ Configurando Termostatos

1. Vá na aba **Thermal Zones**
2. Clique em cada zona
3. Em **"Thermostat"**, selecione ou crie um novo:
   - **Name:** Termostato_24C
   - **Cooling Setpoint Schedule:** Constant 24°C
4. Aplique para todas as zonas

---

## 📊 Configurando Variáveis de Saída

1. Vá na aba **Output Variables**
2. Adicione as seguintes variáveis:

| Variável | Frequência |
|----------|------------|
| Zone Mean Air Temperature | Timestep |
| Zone Air Relative Humidity | Timestep |
| Zone Ideal Loads Zone Total Cooling Energy | Timestep |
| Zone Windows Total Transmitted Solar Radiation Energy | Timestep |
| Site Outdoor Air Drybulb Temperature | Timestep |

---

## ☀️ Configurando Arquivo Climático

1. Vá na aba **Site**
2. Clique em **"Weather File"**
3. Selecione: `weather/Fortaleza.epw`

---

## ▶️ Executando a Simulação

1. Vá na aba **Run Simulation**
2. Clique em **"Run"**
3. Aguarde a simulação (pode levar alguns minutos)
4. Veja os resultados na aba **Results**

---

## 📈 Analisando Resultados

### No OpenStudio:
- Aba **Results** → Gráficos automáticos
- **DView** → Visualização interativa de séries temporais

### Exportar para análise externa:
1. Encontre a pasta de resultados (geralmente em `run/`)
2. Abra `eplusout.csv` no Excel ou Python
3. Use o script `scripts/analisar_resultados.py`

---

## 🗺️ Layout das 6 Zonas (modelo detalhado)

```
    Parede do Fundo (ACs)
    Y = 9.39m
+------------------+------------------+
|                  |                  |
| Zona_Esq_Fundo   | Zona_Dir_Fundo   |
| (janelas 3,4)    |                  |
|                  |                  |
+------------------+------------------+ Y = 6.26m
|                  |                  |
| Zona_Esq_Centro  | Zona_Dir_Centro  |
| (janela 2)       |                  |
|                  |                  |
+------------------+------------------+ Y = 3.13m
|                  |                  |
| Zona_Esq_Frente  | Zona_Dir_Frente  |
| (janela 1)       | (PORTA)          |
|                  |                  |
+------------------+------------------+ Y = 0
X=0              X=3.53            X=7.06
(janelas)                          (porta)

    Parede Frontal (Lousa)
```

### Análise por zona:

| Zona | Localização | Características |
|------|-------------|-----------------|
| Esq_Frente | Canto esquerdo-frente | Janela 1, perto da lousa |
| Dir_Frente | Canto direito-frente | Porta, projetor |
| Esq_Centro | Centro esquerdo | Janela 2 |
| Dir_Centro | Centro direito | Sem aberturas externas |
| Esq_Fundo | Canto esquerdo-fundo | Janelas 3 e 4, perto dos ACs |
| Dir_Fundo | Canto direito-fundo | Perto dos ACs |

### O que analisar:

1. **Influência das janelas:** Comparar zonas Esq vs Dir
2. **Gradiente térmico:** Comparar zonas Frente vs Centro vs Fundo
3. **Radiação solar:** Maior nas zonas com janelas (Esq)
4. **Carga de resfriamento:** Diferença entre zonas
5. **Conforto térmico:** Temperatura em cada região

---

## 🔧 Dicas de Troubleshooting

### Erro: "No weather file"
- Configure o arquivo EPW na aba Site

### Erro: "No HVAC system"
- Ative "Ideal Air Loads" nas zonas ou configure um sistema HVAC

### Aviso: "Unmet hours"
- O sistema HVAC não conseguiu manter a temperatura
- Aumente a capacidade de resfriamento

### Geometria não aparece
- Verifique se as coordenadas estão corretas
- Use a aba "Geometry" → "Editor" para visualizar

---

## 📊 Análise do Modelo de 6 Regiões (`laboratorio_6zonas.idf`)

### Interpretando os Resultados

O modelo `laboratorio_6zonas.idf` é uma **zona única com outputs detalhados** que permitem inferir o comportamento térmico em 6 regiões espaciais distintas. Não são zonas físicas separadas, mas sim análise de temperatura de superfícies e radiação em diferentes locais.

### Variáveis de Output Disponíveis

#### 1. Temperatura de Superfícies por Região

**Região 1, 3, 5 (Lado ESQUERDO - com janelas):**
```
Wall_Left_Windows:Surface Inside Face Temperature
Window_1_Left_Front:Surface Inside Face Temperature (Região 1)
Window_2_Left_Center:Surface Inside Face Temperature (Região 3)
Window_3_Left_Back1:Surface Inside Face Temperature (Região 5)
Window_4_Left_Back2:Surface Inside Face Temperature (Região 5)
```

**Região 2, 4, 6 (Lado DIREITO - com porta):**
```
Wall_Right_Door:Surface Inside Face Temperature
```

**Região 1, 2 (FRENTE - com lousa):**
```
Wall_Front_Blackboard:Surface Inside Face Temperature
```

**Região 5, 6 (FUNDO - com ACs):**
```
Wall_Back_AC:Surface Inside Face Temperature
```

#### 2. Ganho de Calor Solar por Janela

```
Surface Window Transmitted Solar Radiation Rate
Surface Window Heat Gain Rate
Surface Window Heat Loss Rate
```

### Como Analisar o Gradiente Térmico

1. **Compare temperatura das paredes opostas:**
   - `Wall_Left_Windows` (janelas) vs `Wall_Right_Door` (porta)
   - Espera-se maior temperatura na parede com janelas (ganho solar)

2. **Compare frente vs fundo:**
   - `Wall_Front_Blackboard` vs `Wall_Back_AC`
   - Parede com ACs deve ter temperatura mais baixa

3. **Analise radiação solar por janela:**
   - Janelas 1,2 (frente/centro) podem receber mais radiação em certos horários
   - Janelas 3,4 (fundo) têm comportamento diferente devido à orientação

4. **Interprete as 6 regiões:**
   - **Região 1:** Temperatura de Window_1 + Wall_Left + Wall_Front
   - **Região 2:** Temperatura de Wall_Right + Wall_Front
   - **Região 3:** Temperatura de Window_2 + Wall_Left
   - **Região 4:** Temperatura de Wall_Right (centro)
   - **Região 5:** Temperatura de Window_3/4 + Wall_Left + Wall_Back
   - **Região 6:** Temperatura de Wall_Right + Wall_Back

### Exemplo de Análise

**Pergunta:** Qual região fica mais quente durante a tarde?

**Método:**
1. Abra `results/sim_6zonas/eplusout.csv`
2. Filtre horários 14:00-17:00
3. Compare temperaturas:
   - Janelas (representam regiões 1, 3, 5)
   - Paredes laterais
   - Temperatura média da zona
4. Região com maior temperatura de janela + parede = mais quente

**Pergunta:** A porta influencia a temperatura localmente?

**Método:**
1. Compare `Wall_Right_Door` (perto da porta) vs `Wall_Left_Windows`
2. Se houver diferença significativa, a porta pode estar permitindo infiltração

---

## 📚 Recursos

- [OpenStudio Documentation](https://openstudio.net/users/documentation)
- [EnergyPlus Input/Output Reference](https://energyplus.net/documentation)
- [OpenStudio Coalition Tutorials](https://www.youtube.com/@OpenStudioCoalition)
- **Resultados da simulação:** `results/sim_6zonas/eplusout.csv` e `eplusout.html`

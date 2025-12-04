# Simulação Térmica - Laboratório de Arquitetura
## Grupo 2 - Campus UFC Quixadá

## 📋 Visão Geral

Este projeto contém os arquivos e scripts para realizar a simulação térmica do **Laboratório de Arquitetura** da UFC Quixadá usando EnergyPlus e OpenStudio.

### Características do Laboratório:
- 🏢 **2 ar-condicionados** na parede do fundo
- 🪟 **2 janelas grandes** na parede oposta à porta
- 📝 **1 lousa** na parede adjacente à porta
- 📍 **Localização**: Fortaleza, Ceará, Brasil

---

## 📁 Estrutura do Projeto

```
simulacao_laboratorio/
├── models/                                  # Modelos de simulação
│   ├── laboratorio_arquitetura.idf          # ✅ Versão 25.1 (FUNCIONANDO)
│   ├── laboratorio_arquitetura_v24.1.idf    # ⚠️ Versão 24.1 (OpenStudio)
│   └── laboratorio_arquitetura_backup.idf   # 📦 Backup da versão original
├── weather/                                 # Arquivos de clima
│   ├── README_CLIMA.md                      # Instruções para obter arquivo EPW
│   └── Fortaleza.epw                        # Arquivo de clima (baixar)
├── scripts/                                 # Scripts auxiliares
│   ├── baixar_clima_fortaleza.py            # Baixa arquivo EPW
│   ├── executar_simulacao.py                # ✅ Executa simulação v25.1
│   ├── executar_simulacao_v241.py           # Executa simulação v24.1
│   └── analisar_resultados.py               # Analisa e gera gráficos
├── results/                                 # Resultados das simulações
│   ├── sim_YYYYMMDD_HHMMSS/                 # Simulações v25.1
│   └── sim_v241_YYYYMMDD_HHMMSS/            # Simulações v24.1
├── README.md                                # Este arquivo
├── DADOS_NECESSARIOS.md                     # Checklist de dados a coletar
├── CORRECOES_APLICADAS.md                   # Histórico de correções
└── VERSAO_24.1_NOTAS.md                     # Notas sobre versão 24.1
```

## 🔢 Versões Disponíveis

### ✅ Versão 25.1 (Recomendada - Funcionando)
- **Arquivo:** `models/laboratorio_arquitetura.idf`
- **EnergyPlus:** 25.1.0
- **Status:** Totalmente funcional
- **Uso:** `python3 scripts/executar_simulacao.py`

### ⚠️ Versão 24.1 (OpenStudio)
- **Arquivo:** `models/laboratorio_arquitetura_v24.1.idf`
- **EnergyPlus:** 24.1.0 (incluído no OpenStudio 3.8.0)
- **Status:** Necessita importação no OpenStudio para conversão automática
- **Uso:** Importar no OpenStudio Application
- **Detalhes:** Ver `VERSAO_24.1_NOTAS.md`

---

## 🚀 Como Executar a Simulação

### Método 1: EnergyPlus 25.1 Standalone (Recomendado)

#### Passo 1: Baixar Arquivo de Clima

O arquivo de clima (EPW) contém dados meteorológicos de Fortaleza.

```bash
cd "/home/guilherme/UFC/Instrumentação/EnergyPlus/simulacao_laboratorio"
python3 scripts/baixar_clima_fortaleza.py
```

**Alternativa manual:**
1. Acesse: https://energyplus.net/weather
2. Busque por "Fortaleza" ou "Brazil"
3. Baixe o arquivo `BRA_CE_Fortaleza.838990_INMET.epw`
4. Salve em `weather/Fortaleza.epw`

#### Passo 2: Executar Simulação

```bash
python3 scripts/executar_simulacao.py
```

Este comando irá:
- ✅ Verificar se todos os arquivos necessários existem
- ✅ Executar o EnergyPlus com os parâmetros corretos
- ✅ Salvar os resultados em `results/sim_YYYYMMDD_HHMMSS/`

#### Passo 3: Analisar Resultados

```bash
# Instalar dependências (apenas primeira vez)
pip install pandas matplotlib

# Executar análise
python3 scripts/analisar_resultados.py
```

Este comando irá:
- 📊 Gerar gráficos de temperatura
- ⚡ Gerar gráficos de consumo de energia
- 📈 Calcular estatísticas resumidas
- 💾 Salvar visualizações em `results/sim_*/graficos/`

#### Passo 4: Visualizar Relatório HTML

```bash
# No Linux
xdg-open results/sim_*/eplustbl.htm

# Ou navegue manualmente até o arquivo e abra no navegador
```

---

### Método 2: OpenStudio Application (Interface Gráfica)

O OpenStudio fornece uma interface gráfica mais amigável para criar e editar modelos.

#### Passo 1: Importar o Modelo IDF

```bash
# Abrir o OpenStudio
openstudio
```

Ou procure "OpenStudio" no menu de aplicativos.

#### Passo 2: Importar o Arquivo IDF

1. No OpenStudio: **File → Import → IDF File**
2. Selecione: `models/laboratorio_arquitetura.idf`
3. O OpenStudio converterá automaticamente para a versão 24.1
4. Salve como arquivo OSM: **File → Save As...**

#### Passo 3: Editar no OpenStudio (Opcional)

- **Geometry:** Ver e editar a geometria 3D do laboratório
- **Constructions:** Modificar materiais de paredes, janelas, etc.
- **Loads:** Ajustar ocupação, equipamentos, iluminação
- **HVAC Systems:** Configurar sistemas de climatização
- **Output Variables:** Escolher quais dados exportar

#### Passo 4: Executar Simulação no OpenStudio

1. **Run Simulation** (botão verde ▶️)
2. Aguarde a conclusão
3. Visualize resultados na aba **Results**

#### Passo 5: Visualizar Resultados

- **Results Summary:** Relatórios automáticos
- **DView:** Gráficos interativos de dados horários
- **Reports:** Relatórios HTML detalhados

---

## 📊 Dados Necessários para Ajustar o Modelo

### 🔧 **DADOS CRÍTICOS - Precisam ser Atualizados**

Consulte a planta do laboratório e atualize estes valores no arquivo `models/laboratorio_arquitetura.idf`:

#### 1. **Dimensões do Laboratório**
Atualmente configurado como: **10m × 8m × 3m** (comprimento × largura × altura)

```
Localização no arquivo IDF: Seção "ZONE" e coordenadas das superfícies
```

**Como medir:**
- Comprimento (X): Dimensão da parede com porta à parede oposta
- Largura (Y): Dimensão entre as paredes laterais
- Altura (Z): Pé-direito do laboratório

#### 2. **Posição e Tamanho das Janelas**
Atualmente: 2 janelas de 2.5m × 2.0m (largura × altura)

```
Localização no arquivo IDF: Seção "FenestrationSurface:Detailed"
Objetos: Window_1 e Window_2
```

**Dados necessários:**
- Largura de cada janela
- Altura de cada janela
- Posição na parede (distância das extremidades)
- Altura do peitoril (distância do chão)

#### 3. **Especificações dos Ar-Condicionados**
Atualmente: Capacidade em "autosize" (dimensionamento automático)

```
Localização no arquivo IDF: Seção "ZoneHVAC:WindowAirConditioner"
Objetos: AC_Unit_1 e AC_Unit_2
```

**Dados necessários:**
- Marca e modelo dos ar-condicionados
- Capacidade de refrigeração (BTU/h ou kW)
- Eficiência energética (COP ou EER)
- Vazão de ar (m³/s ou CFM)
- Posição exata na parede

#### 4. **Orientação do Edifício**
Atualmente: Norte = 0° (sem rotação)

```
Localização no arquivo IDF: Seção "Building"
Campo: North Axis
```

**Dados necessários:**
- Ângulo de rotação em relação ao Norte geográfico
- Use uma bússola ou Google Earth para determinar

#### 5. **Materiais de Construção**
Atualmente: Valores genéricos

```
Localização no arquivo IDF: Seção "Material" e "Construction"
```

**Dados necessários:**
- **Paredes:** Tipo de alvenaria (tijolo cerâmico, bloco de concreto, etc.)
- **Piso:** Material e espessura
- **Teto/Cobertura:** Tipo de laje, isolamento
- **Janelas:** Tipo de vidro (simples, duplo, baixo-e, etc.)
- **Porta:** Material (madeira, metal, vidro)

#### 6. **Cargas Internas**
Atualmente: Valores estimados

```
Localização no arquivo IDF: Seções "People", "Lights", "ElectricEquipment"
```

**Dados necessários:**
- **Ocupação:** Número típico de pessoas no laboratório
- **Iluminação:** Potência total das lâmpadas (W) ou densidade (W/m²)
- **Equipamentos:** Computadores, projetores, etc. (W total)
- **Horários de uso:** Período de funcionamento do laboratório

#### 7. **Sistema de Ventilação**
Atualmente: Taxa de infiltração genérica

```
Localização no arquivo IDF: Seção "ZoneInfiltration:DesignFlowRate"
```

**Dados necessários:**
- Existe ventilação natural? (janelas abertas)
- Existe ventilação mecânica?
- Taxa de renovação de ar desejada

---

## 📝 Como Editar o Arquivo IDF

### Opção 1: Editor de Texto (Para usuários avançados)

```bash
code models/laboratorio_arquitetura.idf
# ou
nano models/laboratorio_arquitetura.idf
```

**Busque por comentários "*** NOTA:" que indicam valores que precisam ser ajustados.**

### Opção 2: IDF Editor (Recomendado)

O IDF Editor é uma interface gráfica instalada junto com o EnergyPlus:

```bash
# Localização típica no Linux
/usr/local/EnergyPlus-23-2-0/PreProcess/IDFEditor/IDFEditor
```

**Como usar:**
1. Abra o IDF Editor
2. File → Open → Selecione `laboratorio_arquitetura.idf`
3. Navegue pelas classes à esquerda
4. Edite os valores nos campos à direita
5. File → Save

### Opção 3: OpenStudio (Interface completa)

OpenStudio oferece uma interface mais amigável:

```bash
openstudio
```

**Como importar:**
1. Abra OpenStudio
2. File → New
3. File → Import → IDF File
4. Selecione `laboratorio_arquitetura.idf`
5. Edite visualmente no SketchUp Plugin ou na interface

---

## 🌡️ Dados Climáticos de Fortaleza

O arquivo EPW contém dados horários de:
- ☀️ Temperatura de bulbo seco e úmido
- 💧 Umidade relativa
- ☁️ Radiação solar direta e difusa
- 💨 Velocidade e direção do vento
- 🌧️ Precipitação

**Características climáticas:**
- **Latitude:** -3.72°
- **Longitude:** -38.54°
- **Altitude:** 21 m
- **Clima:** Tropical quente e úmido (Aw - Köppen)
- **Temperatura média:** ~27°C
- **Temperatura máxima:** ~32-34°C
- **Temperatura mínima:** ~24-25°C
- **Umidade relativa:** 70-80%

---

## 📈 Resultados da Simulação

Após executar a simulação, você terá:

### Arquivos Gerados:

1. **`eplustbl.htm`** - Relatório HTML completo com tabelas resumidas
   - Consumo anual de energia
   - Temperaturas máximas/mínimas
   - Carga térmica de resfriamento
   - Conforto térmico

2. **`eplusout.csv`** - Dados horários em CSV
   - Temperatura da zona
   - Temperatura externa
   - Consumo instantâneo
   - Carga de resfriamento
   - Pode ser importado no Excel, Python, R

3. **`eplusout.err`** - Arquivo de erros e avisos
   - Verifique sempre este arquivo
   - Erros "Severe" ou "Fatal" indicam problemas

4. **`graficos/`** - Visualizações geradas pelo script de análise
   - `temperaturas.png`
   - `energia.png`

### Análises Possíveis:

- 🌡️ **Conforto térmico:** A temperatura interna está adequada?
- ⚡ **Eficiência energética:** Quanto os ar-condicionados consomem?
- 🔄 **Comparação de cenários:** Testar diferentes configurações
- 💡 **Otimização:** Melhorar isolamento, orientação, etc.

---

## 🛠️ Troubleshooting

### Erro: "EnergyPlus não encontrado"

```bash
# Verifique se o EnergyPlus está instalado
which energyplus

# Se não estiver no PATH, edite o script executar_simulacao.py
# e adicione o caminho correto na função encontrar_energyplus()
```

### Erro: "Arquivo EPW não encontrado"

Execute novamente o download:
```bash
python3 scripts/baixar_clima_fortaleza.py
```

### Erro: "Severe Errors" durante a simulação

Abra o arquivo `eplusout.err` e procure por linhas com `** Severe`:
- Erros de geometria: Verifique coordenadas das superfícies
- Erros de materiais: Verifique propriedades dos materiais
- Erros de HVAC: Verifique configuração dos ar-condicionados

### Warnings (Avisos)

Avisos geralmente não impedem a simulação, mas devem ser revisados:
- Verifique o arquivo `eplusout.err`
- Corrija se possível para melhorar a precisão

---

## 📚 Recursos Adicionais

### Documentação Oficial:
- **EnergyPlus:** https://energyplus.net/documentation
- **OpenStudio:** https://openstudio.net/
- **DesignBuilder:** https://designbuilder.co.uk/

### Tutoriais:
- EnergyPlus Getting Started: https://energyplus.net/quickstart
- Big Ladder Software (tutoriais): https://bigladdersoftware.com/

### Arquivos de Clima:
- EnergyPlus Weather Data: https://energyplus.net/weather
- LABEEE/UFSC: https://labeee.ufsc.br/downloads/arquivos-climaticos

### Comunidade:
- Unmethours (fórum): https://unmethours.com/
- EnergyPlus Support: https://energyplus.helpserve.com/

---

## ✅ Checklist para a Prática

Antes de executar a simulação final, verifique:

- [ ] Dimensões do laboratório medidas e atualizadas
- [ ] Posição e tamanho das janelas corretos
- [ ] Especificações dos ar-condicionados obtidas
- [ ] Orientação do edifício determinada
- [ ] Materiais de construção identificados
- [ ] Cargas internas estimadas (pessoas, equipamentos, iluminação)
- [ ] Horários de uso definidos
- [ ] Arquivo EPW de Fortaleza baixado
- [ ] Simulação executada sem erros severos
- [ ] Resultados analisados e gráficos gerados
- [ ] Relatório HTML visualizado

---

## 🤝 Equipe

**Grupo 2 - Simulação Térmica**
- Campus UFC Quixadá
- Disciplina: Instrumentação

---

## 📞 Suporte

Se tiver dúvidas ou encontrar problemas:

1. Verifique o arquivo `eplusout.err` para erros específicos
2. Consulte a documentação oficial do EnergyPlus
3. Revise este README para instruções detalhadas
4. Consulte o professor ou monitor da disciplina

---

## 🔄 Próximos Passos

1. **Coletar dados reais** do laboratório conforme seção acima
2. **Atualizar o modelo** com os dados coletados
3. **Executar a simulação** e verificar resultados
4. **Analisar conforto térmico** e eficiência energética
5. **Propor melhorias** (isolamento, orientação, ventilação, etc.)
6. **Simular cenários alternativos** e comparar resultados
7. **Preparar relatório final** com conclusões

---

**Boa sorte com a simulação! 🎓🔥❄️**

# Simulação Térmica - Laboratório de Arquitetura
## Grupo 2 - Campus UFC Quixadá

## 📋 Visão Geral

Este projeto contém os arquivos e scripts para realizar a simulação térmica do **Laboratório de Arquitetura** da UFC Quixadá usando EnergyPlus e OpenStudio.

### Características do Laboratório:
- 📐 **Dimensões:** 7.06m × 9.39m × 2.68m (66.29 m²)
- 🧭 **Orientação:** 342° do Norte
- ❄️ **2 ar-condicionados Split** 30.000 BTU/h cada (parede lateral)
- 🪟 **4 janelas de correr** 1.55m × 1.17m (parede lateral)
- 🚪 **1 porta dupla** 1.20m × 2.10m (madeira maciça com visor)
- 💡 **6 luminárias** LED tubular T5 (120W total)
- 📝 **1 lousa** na parede adjacente à porta
- 📍 **Clima:** Fortaleza, Ceará, Brasil

### Materiais (conforme Memorial Descritivo - Edital 90009/2024):
- **Paredes:** Bloco cerâmico furado 9×19×19cm + argamassa 2.5cm
- **Cobertura:** Telha galvalume + isolamento PU 30mm + laje nervurada
- **Janelas:** Alumínio de correr + vidro simples 4mm

---

## 📁 Estrutura do Projeto

```
simulacao_laboratorio/
├── models/                                  # Modelos de simulação
│   ├── laboratorio_arquitetura.idf          # ✅ Modelo principal (EnergyPlus 25.1)
│   └── laboratorio_arquitetura_backup.idf   # 📦 Backup da versão original
├── weather/                                 # Arquivos de clima
│   ├── README_CLIMA.md                      # Instruções para obter arquivo EPW
│   └── Fortaleza.epw                        # Arquivo de clima (baixar)
├── scripts/                                 # Scripts auxiliares
│   ├── baixar_clima_fortaleza.py            # Baixa arquivo EPW
│   ├── executar_simulacao.py                # Executa simulação EnergyPlus
│   └── analisar_resultados.py               # Analisa e gera gráficos
├── results/                                 # Resultados das simulações
│   └── sim_YYYYMMDD_HHMMSS/                 # Pasta por simulação
├── README.md                                # Este arquivo
├── DADOS_NECESSARIOS.md                     # Checklist de dados (template)
├── DADOS_COLETADOS.md                       # ✅ Dados reais coletados
└── CORRECOES_APLICADAS.md                   # Histórico de correções
```

---

## 🚀 Como Executar a Simulação

### Passo 1: Baixar Arquivo de Clima

```bash
cd "/home/guilherme/UFC/Instrumentação/EnergyPlus/simulacao_laboratorio"
python3 scripts/baixar_clima_fortaleza.py
```

### Passo 2: Executar Simulação

```bash
python3 scripts/executar_simulacao.py
```

### Passo 3: Analisar Resultados

```bash
# Instalar dependências (apenas primeira vez)
pip install pandas matplotlib

# Executar análise
python3 scripts/analisar_resultados.py
```

### Passo 4: Visualizar no OpenStudio (Opcional)

Para visualização 3D e edição gráfica:

```bash
# Abrir no OpenStudio Application
openstudio models/laboratorio_arquitetura.idf
```

### Passo 5: Visualizar Relatório HTML

```bash
xdg-open results/sim_*/eplustbl.htm
```

---

## 📊 Dados do Modelo

Os dados do modelo foram coletados in loco e do Memorial Descritivo do Bloco Didático 5 (Edital 90009/2024).

### ✅ Dados Já Configurados no Modelo

| Parâmetro | Valor |
|-----------|-------|
| Dimensões | 7.06m × 9.39m × 2.68m |
| Área | 66.29 m² |
| Orientação | 342° do Norte |
| Janelas | 4× (1.55m × 1.17m) |
| Porta | 1.20m × 2.10m |
| Iluminação | 120W (6 luminárias LED) |
| Parede | Bloco cerâmico 9cm + argamassa |
| Vidro | Simples 4mm |
| Isolamento teto | PU 30mm |

### ⚠️ Dados Pendentes de Confirmação

Consulte [`DADOS_COLETADOS.md`](DADOS_COLETADOS.md) para lista completa.

- [ ] Altura exata do peitoril das janelas
- [ ] Posição dos ar-condicionados na parede
- [ ] Temperatura do termostato
- [ ] Ocupação típica (número de pessoas)
- [ ] Potência exata das lâmpadas (10W ou 20W)

---

## 🔧 Como Ajustar o Modelo

### Editar Dimensões

No arquivo `models/laboratorio_arquitetura.idf`, localize:

```
Zone,
    Laboratorio_Zone,        !- Name
    ...
    2.68,                    !- Ceiling Height {m}
    177.66;                  !- Volume {m3}
```

E as superfícies na seção `BuildingSurface:Detailed`.

### Editar Materiais

Localize a seção `Material` e `Construction` para ajustar:
- Espessuras
- Condutividade térmica
- Densidade

### Editar Cargas Internas

Na seção `People`, `Lights`, `ElectricEquipment`:
- Número de pessoas
- Potência de iluminação (W/m²)
- Potência de equipamentos

### Editar HVAC

Na seção `ZoneHVAC:WindowAirConditioner`:
- Capacidade de refrigeração (autosize ou valor em W)
- Vazão de ar

---

## 📝 Como Editar o Arquivo IDF

### Opção 1: Editor de Texto

```bash
code models/laboratorio_arquitetura.idf
# ou
nano models/laboratorio_arquitetura.idf
```

### Opção 2: OpenStudio (Recomendado)

OpenStudio oferece visualização 3D e edição gráfica:

```bash
# Abrir diretamente o arquivo IDF
/usr/local/openstudioapplication-1.8.0/bin/OpenStudioApp models/laboratorio_arquitetura.idf
```

No OpenStudio você pode:
- 🏗️ **Geometry:** Ver modelo 3D do laboratório
- 🧱 **Constructions:** Editar materiais
- 👥 **Loads:** Ajustar ocupação e equipamentos
- ❄️ **HVAC Systems:** Configurar ar-condicionados

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
- Verifique o arquivo `results/sim_*/eplusout.err`
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

### Dados Coletados ✓
- [x] Dimensões do laboratório medidas (7.06m × 9.39m × 2.68m)
- [x] Janelas medidas (4× 1.55m × 1.17m)
- [x] Porta medida (0.80m × 2.10m)
- [x] Luminárias contadas (6 unidades LED)
- [x] Orientação determinada (342° N)
- [x] Materiais identificados (bloco cerâmico, galvalume)

### Pendente de Confirmação
- [ ] Altura do peitoril das janelas
- [ ] Especificações dos ar-condicionados (BTU)
- [ ] Temperatura do termostato
- [ ] Número típico de ocupantes
- [ ] Potência exata das lâmpadas LED

### Execução
- [ ] Arquivo EPW baixado (`scripts/baixar_clima_fortaleza.py`)
- [ ] Simulação executada sem erros
- [ ] Resultados analisados
- [ ] Relatório HTML visualizado

---

## 🤝 Equipe

**Grupo 2 - Simulação Térmica**
- Campus UFC Quixadá
- Disciplina: Instrumentação

---

## 📞 Suporte

Se tiver dúvidas ou encontrar problemas:

1. Verifique o arquivo `results/sim_*/eplusout.err` para erros específicos
2. Consulte a documentação oficial do EnergyPlus
3. Consulte o arquivo `DADOS_COLETADOS.md` para ver os dados usados
4. Consulte o professor ou monitor da disciplina

---

## 🔄 Próximos Passos

1. ✅ ~~Coletar dados reais~~ (dimensões, janelas, materiais - FEITO)
2. ✅ ~~Atualizar o modelo~~ com dados coletados (FEITO)
3. **Confirmar dados pendentes** (peitoril, BTU ar-condicionados, ocupação)
4. **Executar a simulação** e verificar resultados
5. **Analisar conforto térmico** e consumo energético
6. **Simular cenários alternativos** (diferentes temperaturas, ocupação)
7. **Preparar relatório final** com conclusões

---

**Boa sorte com a simulação! 🎓🔥❄️**

# Guia Rápido: Versão 24.1 vs 25.1

## 🎯 Qual Versão Usar?

### ✅ Use EnergyPlus 25.1 (Standalone) Se:
- Quer executar simulações rapidamente via linha de comando
- Prefere scripts automatizados (Python)
- Não precisa da interface gráfica
- Quer máxima compatibilidade e flexibilidade
- **Arquivo:** `models/laboratorio_arquitetura.idf`
- **Comando:** `python3 scripts/executar_simulacao.py`

### 🖥️ Use OpenStudio (EnergyPlus 24.1) Se:
- Prefere interface gráfica para editar o modelo
- Quer visualizar a geometria 3D
- Precisa criar ou modificar o modelo visualmente
- Quer usar ferramentas de análise integradas do OpenStudio
- **Método:** Importar `laboratorio_arquitetura.idf` no OpenStudio

---

## 📊 Comparação Detalhada

| Característica | EnergyPlus 25.1 | OpenStudio (24.1) |
|---------------|----------------|-------------------|
| **Interface** | Linha de comando | Gráfica (GUI) |
| **Facilidade (iniciantes)** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Velocidade de execução** | ⚡⚡⚡⚡⚡ | ⚡⚡⚡⚡ |
| **Automação** | ✅ Fácil (Python) | ⚠️ Limitada |
| **Edição de geometria** | ⚠️ Manual (texto) | ✅ Visual (3D) |
| **Visualização 3D** | ❌ | ✅ |
| **Análise de resultados** | Script Python | DView integrado |
| **Curva de aprendizado** | Alta (código) | Média (interface) |
| **Documentação** | Extensa | Extensa + Tutoriais |
| **Status atual** | ✅ Funcionando | ⚠️ Requer importação |

---

## 🚀 Fluxo de Trabalho Recomendado

### Para Análises Rápidas:
```mermaid
Baixar EPW → Executar v25.1 → Analisar resultados
```
```bash
python3 scripts/baixar_clima_fortaleza.py
python3 scripts/executar_simulacao.py
python3 scripts/analisar_resultados.py
```

### Para Modificações no Modelo:
```mermaid
Importar IDF → Editar no OpenStudio → Simular → Analisar
```
1. Abrir OpenStudio Application
2. File → Import → IDF → `laboratorio_arquitetura.idf`
3. Editar modelo visualmente
4. Run Simulation
5. Ver resultados no DView

### Workflow Híbrido (Melhor dos Dois Mundos):
```mermaid
Criar/Editar no OpenStudio → Exportar IDF → Automatizar com Python
```
1. Modelar no OpenStudio (interface gráfica)
2. Exportar como IDF
3. Executar múltiplas simulações com scripts Python
4. Analisar resultados em lote

---

## 🔄 Como Converter Entre Versões

### De 25.1 para OpenStudio (24.1):
```bash
# Método 1: Interface Gráfica (RECOMENDADO)
openstudio
# File → Import → IDF → laboratorio_arquitetura.idf

# Método 2: Linha de comando (se disponível)
openstudio translate models/laboratorio_arquitetura.idf
```

### De OpenStudio para IDF:
```bash
# No OpenStudio Application
# File → Export → IDF
# Isso gera um arquivo .idf que pode ser usado no EnergyPlus 25.1
```

---

## 📝 Diferenças Técnicas Principais

### Sintaxe do HVAC

**EnergyPlus 25.1:**
```idf
HVACTemplate:Zone:IdealLoadsAirSystem,
    Laboratorio_Zone,
    ...
    ConstantSupplyHumidityRatio,  !- Aceita string
    ...
```

**EnergyPlus 24.1:**
```idf
HVACTemplate:Zone:IdealLoadsAirSystem,
    Laboratorio_Zone,
    ...
    0.009,  !- Requer valor numérico
    ...
```

### Objetos Suportados

| Objeto | v25.1 | v24.1 |
|--------|-------|-------|
| `HVACTemplate:*` | ✅ Flexível | ⚠️ Restrito |
| `Coil:Cooling:DX` | ✅ Novo formato | ❌ Usa formato antigo |
| `Coil:Cooling:DX:SingleSpeed` | ⚠️ Descontinuado | ✅ Suportado |

---

## 💡 Dicas Práticas

### Para Aprender EnergyPlus:
1. **Comece com OpenStudio** - Interface mais amigável
2. **Depois use v25.1** - Mais controle e flexibilidade
3. **Leia a documentação** - Ambas as ferramentas têm docs excelentes

### Para Trabalhos em Equipe:
- **Decisão:** Escolha UMA versão para todo o projeto
- **Versionamento:** Use Git para controlar mudanças no IDF
- **Comunicação:** Documente qual versão está sendo usada

### Para Apresentações:
- Use **OpenStudio** para gerar imagens 3D bonitas
- Use **Python** para gerar gráficos profissionais
- Exporte relatórios HTML de ambas as ferramentas

---

## 🐛 Troubleshooting Comum

### Erro: "Version mismatch"
- **Solução:** Use o arquivo correto para cada versão
- v25.1 → `laboratorio_arquitetura.idf`
- v24.1 → Importar no OpenStudio

### Erro: "HVACTemplate not supported"
- **Solução EnergyPlus:** Usar flag `-x` para expandir
- **Solução OpenStudio:** Importar o IDF, não abrir diretamente

### Simulação não roda no OpenStudio
- **Verificar:** Arquivo EPW está correto
- **Verificar:** Caminho do arquivo não tem caracteres especiais
- **Solução:** Reimportar o IDF

---

## 📚 Recursos Adicionais

### EnergyPlus 25.1:
- Documentação: https://energyplus.net/documentation
- Exemplos: `/usr/local/EnergyPlus-25-1-0/ExampleFiles/`
- Fórum: https://unmethours.com/

### OpenStudio:
- Site oficial: https://openstudio.net/
- Tutoriais: https://nrel.github.io/OpenStudio-user-documentation/
- Vídeos: YouTube "OpenStudio tutorials"

### Ambos:
- Big Ladder Software: https://bigladdersoftware.com/
- NREL (desenvolvedores): https://www.nrel.gov/buildings/
- Comunidade Unmethours: https://unmethours.com/

---

## ✅ Checklist Final

Antes de começar a simulação, verifique:

- [ ] Escolheu a versão adequada (25.1 ou OpenStudio)
- [ ] Baixou o arquivo EPW de Fortaleza
- [ ] Leu este guia comparativo
- [ ] Conhece os comandos básicos
- [ ] Tem os dados reais do laboratório (ver `DADOS_NECESSARIOS.md`)
- [ ] Sabe onde estão os resultados
- [ ] Conhece as ferramentas de análise disponíveis

---

**Resumo:** Use **EnergyPlus 25.1** para execução rápida e automação, ou **OpenStudio** para edição visual e aprendizado inicial. Ambos produzem resultados equivalentes!

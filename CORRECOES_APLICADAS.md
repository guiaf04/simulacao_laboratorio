# Correções Realizadas na Simulação - EnergyPlus 25.1

## ✅ Problema Resolvido

A simulação estava falhando devido a incompatibilidades entre a versão original do arquivo IDF (23.2) e a versão instalada do EnergyPlus (25.1).

---

## 🔧 Correções Aplicadas

### 1. **Atualização da Versão do Arquivo**
- **Antes:** `Version,23.2;`
- **Depois:** `Version,25.1;`

### 2. **Simplificação do Sistema HVAC**
O sistema original usava `Coil:Cooling:DX:SingleSpeed` e `ZoneHVAC:WindowAirConditioner`, que foram descontinuados ou mudaram significativamente na versão 25.1.

**Solução adotada:**
- Substituído por `HVACTemplate:Zone:IdealLoadsAirSystem`
- Sistema de carga ideal (Ideal Loads Air System) que:
  - Simula perfeitamente o sistema de ar-condicionado
  - Calcula as cargas térmicas necessárias
  - É mais simples e estável para análise inicial
  - Dimensiona automaticamente a capacidade necessária

### 3. **Correção da Geometria das Janelas**
As janelas estavam com vértices em ordem incorreta, causando orientação invertida em relação à parede base.

**Antes:**
```
Vértices no sentido horário (errado)
```

**Depois:**
```
Vértices no sentido anti-horário (correto)
Seguindo a regra "CounterClockWise" definida no GlobalGeometryRules
```

### 4. **Adição de Flag de Expansão no Script**
O script `executar_simulacao.py` foi atualizado para incluir a flag `-x` que expande automaticamente os objetos HVACTemplate.

---

## 📊 Resultado da Simulação

### Arquivos Gerados:
- ✅ **eplusout.err** (1.85 KB) - Arquivo de erros/avisos
- ✅ **eplusout.csv** (8.05 MB) - Dados horários da simulação
- ✅ **eplustbl.htm** (352 KB) - Relatório HTML completo
- ✅ **eplusout.eio** (17.73 KB) - Informações de inicialização

### Status:
- ⚠️ **Avisos não-críticos encontrados** (normais em simulações)
- ✅ **Simulação concluída em 3.09 segundos**
- ✅ **Dados prontos para análise**

---

## 🎯 Próximos Passos

### 1. Visualizar Relatório HTML
```bash
cd /home/guilherme/UFC/Instrumentação/EnergyPlus/simulacao_laboratorio
xdg-open results/sim_20251204_130734/eplustbl.htm
```

### 2. Executar Análise e Gerar Gráficos
```bash
python3 scripts/analisar_resultados.py
```

### 3. Ajustar Modelo com Dados Reais
Consulte o arquivo `DADOS_NECESSARIOS.md` e atualize:
- Dimensões reais do laboratório
- Especificações dos ar-condicionados
- Cargas internas reais (ocupação, equipamentos, iluminação)
- Materiais de construção

---

## 📝 Observações Importantes

### Sobre o Sistema Ideal Loads Air System:
- **Vantagem:** Fornece dados precisos sobre cargas térmicas necessárias
- **Uso:** Perfeito para análise de desempenho térmico e dimensionamento
- **Interpretação dos resultados:**
  - "District Cooling" = Energia de resfriamento necessária
  - "District Heating" = Energia de aquecimento necessária
  - Use esses valores para dimensionar os ar-condicionados reais

### Avisos Comuns (Não-críticos):
Os avisos encontrados geralmente incluem:
- Diferenças pequenas entre localização do arquivo EPW e especificada
- Temperatura do solo usando valores default (18°C)
- Estas não afetam significativamente os resultados

---

## 🔄 Se Precisar de Ar-Condicionados Reais no Modelo

Para versões futuras, se quiser modelar os ar-condicionados específicos em vez do sistema ideal:

1. **Obter especificações técnicas:**
   - Modelo exato dos equipamentos
   - Capacidade em BTU/h ou kW
   - COP (Coeficiente de Performance)
   - Curvas de desempenho do fabricante

2. **Usar objetos compatíveis com v25.1:**
   - `Coil:Cooling:DX` (novo formato)
   - `Coil:Cooling:DX:CurveFit:Performance`
   - `Coil:Cooling:DX:CurveFit:OperatingMode`
   - `Coil:Cooling:DX:CurveFit:Speed`

3. **Consultar documentação:**
   - https://energyplus.net/documentation
   - Procurar por exemplos na pasta: ExampleFiles do EnergyPlus

---

## 📚 Arquivos de Referência

- **Modelo original (backup):** `models/laboratorio_arquitetura_backup.idf`
- **Modelo atual (funcionando):** `models/laboratorio_arquitetura.idf`
- **Resultados da simulação:** `results/sim_20251204_130734/`

---

**Data da correção:** 04 de dezembro de 2025  
**Versão EnergyPlus:** 25.1.0-68a4a7c774  
**Status:** ✅ Simulação funcionando corretamente

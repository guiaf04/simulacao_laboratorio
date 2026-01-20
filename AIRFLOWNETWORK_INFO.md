# Configuração AirflowNetwork - Laboratório de Arquitetura

## Descrição

Ambos os modelos de simulação (`laboratorio_arquitetura.idf` e `laboratorio_6zonas.idf`) foram atualizados com o módulo **AirflowNetwork** do EnergyPlus para simular de forma realista a circulação de ar através da porta principal.

## Objetivo

Simular o impacto da **abertura da porta** durante os intervalos de aula e em momentos de entrada/saída de estudantes, permitindo avaliar:
- Troca de ar com o exterior
- Variação de temperatura devido à ventilação natural
- Taxa de infiltração de ar (ACH - Air Changes per Hour)
- Influência no consumo energético do sistema de climatização

## Padrão de Abertura da Porta

A porta permanece **fechada durante as aulas** e abre nos seguintes horários (dias úteis):

| Horário | Duração | Motivo |
|---------|---------|--------|
| 08:00 - 08:10 | 10 min | Entrada de alunos (manhã) |
| 10:00 - 10:10 | 10 min | Intervalo (manhã) |
| 12:00 - 12:10 | 10 min | Saída/Almoço |
| 13:20 - 13:40 | 20 min | Entrada de alunos (tarde) |
| 15:00 - 15:10 | 10 min | Intervalo (tarde) |
| 17:20 - 17:40 | 20 min | Saída |

**Nota:** Os tempos foram arredondados para múltiplos de 10 minutos devido ao timestep da simulação (Timestep,6 = 10 minutos).

## Componentes Adicionados

### 1. AirflowNetwork:SimulationControl
Controla a simulação da rede de fluxo de ar:
- **Modo:** MultizoneWithoutDistribution (sem sistema HVAC distribuído)
- **Cálculo de pressão:** Baseado na altura da abertura
- **Tipo de edificação:** LOWRISE (baixo perfil)

### 2. AirflowNetwork:MultiZone:Zone
Define a zona térmica como parte da rede de fluxo:
- **Modo de controle:** NoVent (sem ventilação automática, apenas conforme agenda)
- **Disponibilidade:** Sempre ativa

### 3. AirflowNetwork:MultiZone:Surface
Define as superfícies com fluxo de ar:

#### a) Porta Principal (Door_Main)
- **Componente:** Door_Opening (abertura detalhada)
- **Controle:** Agenda `Door_Opening_Schedule`
- **Área:** 1.195m × 2.10m = 2.51 m²

#### b) Parede Lateral Esquerda (Wall_Left_Windows)
- **Componente:** Wall_Crack (fresta)
- **Função:** Permitir infiltração mínima através das frestas
- **Coeficiente:** 0.001 kg/s (muito baixo, apenas para balanço de massa)

### 4. AirflowNetwork:MultiZone:Component:DetailedOpening
Define as características físicas da abertura da porta:
- **Tipo:** NonPivoted (porta de correr)
- **Coeficiente de descarga:** 0.5 (fechada) a 0.6 (aberta)
- **Fatores de abertura:** 0.0 (fechada) e 1.0 (totalmente aberta)

### 5. AirflowNetwork:MultiZone:Surface:Crack
Define infiltração através de frestas nas paredes:
- **Coeficiente de fluxo:** 0.001 kg/s
- **Expoente:** 0.65

## Variáveis de Saída Adicionadas

Para análise do comportamento do fluxo de ar:

```
Output:Variable,*,AFN Zone Infiltration Volume,Timestep;
Output:Variable,*,AFN Zone Infiltration Air Change Rate,Timestep;
Output:Variable,*,AFN Surface Venting Window or Door Opening Factor,Timestep;
```

Estas variáveis permitem avaliar:
- **AFN Zone Infiltration Volume:** Volume de ar trocado (m³)
- **AFN Zone Infiltration Air Change Rate:** Taxa de renovação de ar por hora (ACH)
- **AFN Surface Venting Window or Door Opening Factor:** Fator de abertura (0 a 1)

## Resultados Esperados

### Durante Porta Fechada:
- Infiltração mínima através das frestas (~0.001 kg/s)
- Sistema de climatização mantém temperatura conforme setpoint
- Baixa renovação de ar

### Durante Porta Aberta:
- Fluxo de ar significativo (~1.5 m²/s quando totalmente aberta)
- Troca de ar com exterior (ar quente externo entrando)
- Aumento temporário da temperatura interna
- Sistema de climatização trabalha mais para compensar

## Como Analisar os Resultados

1. **Arquivo CSV de saída:**
   - Procurar por colunas `AFN Zone Infiltration Air Change Rate`
   - Verificar temperatura da zona durante períodos de abertura da porta

2. **Comparação:**
   - Compare períodos com porta aberta vs. fechada
   - Avalie impacto na carga de resfriamento

3. **Script Python:**
   Use `analisar_6regioes.py` (já existente) e adicione análise de fluxo de ar:
   ```python
   afn_data = df['AFN Zone Infiltration Air Change Rate:Zone(Timestep)']
   door_factor = df['AFN Surface Venting Window or Door Opening Factor:Door_Main(Timestep)']
   ```

## Arquivos Modificados

- ✅ `models/laboratorio_arquitetura.idf` - Modelo zona única com AirflowNetwork
- ✅ `models/laboratorio_6zonas.idf` - Modelo 6 regiões com AirflowNetwork
- ✅ `results/teste_airflow/` - Resultado da simulação zona única
- ✅ `results/teste_airflow_6z/` - Resultado da simulação 6 regiões

## Status

✅ **Implementação completa**
- Ambos os modelos simulando com sucesso
- Agenda de abertura da porta configurada
- Variáveis de saída definidas para análise
- Testado com arquivo EPW de Quixadá

## Próximos Passos (Opcional)

1. **Análise dos resultados:**
   - Criar script para plotar taxa de renovação de ar ao longo do dia
   - Correlacionar abertura da porta com variação de temperatura

2. **Refinamento:**
   - Ajustar coeficientes de descarga se necessário
   - Considerar adicionar janelas abertas (se aplicável)

3. **Validação:**
   - Comparar taxa de renovação de ar com medições reais (se disponíveis)
   - Avaliar impacto no consumo energético

---

**Data de Implementação:** 17 de Dezembro de 2025  
**Versão EnergyPlus:** 25.1.0  
**Clima:** Quixadá UFC (EPW customizado)

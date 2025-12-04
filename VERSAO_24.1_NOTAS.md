# Versão 24.1 para OpenStudio

## Status
✅ **Arquivo criado:** `models/laboratorio_arquitetura_v24.1.idf`  
✅ **Script criado:** `scripts/executar_simulacao_v241.py`

## Problema Identificado

A versão 24.1 do EnergyPlus (usada pelo OpenStudio 3.8.0) tem diferenças na sintaxe do objeto `HVACTemplate:Zone:IdealLoadsAirSystem` em relação à versão 25.1.

### Erro específico:
```
** Severe ** <root>[HVACTemplate:Zone:IdealLoadsAirSystem]
[dehumidification_setpoint] - Value type "string" for input 
"ConstantSupplyHumidityRatio" not permitted by 'type' constraint.
```

## Solução Temporária

Use a versão 25.1 do arquivo (já funcionando) que está em:
```
models/laboratorio_arquitetura.idf
```

Para executar:
```bash
python3 scripts/executar_simulacao.py
```

## Para Usar no OpenStudio

### Opção 1: Importar IDF no OpenStudio (Recomendado)
1. Abra o OpenStudio Application
2. File → Import → IDF
3. Selecione: `models/laboratorio_arquitetura.idf`
4. O OpenStudio converterá automaticamente para a versão 24.1
5. Salve como OSM (OpenStudio Model)

### Opção 2: Criar Modelo Direto no OpenStudio
1. Abra o OpenStudio Application
2. Crie um novo modelo
3. Use a interface gráfica para:
   - Desenhar a geometria do laboratório
   - Adicionar janelas e portas
   - Configurar materiais de construção
   - Adicionar cargas internas (pessoas, iluminação, equipamentos)
   - Configurar sistema HVAC

## Diferenças entre Versões 24.1 e 25.1

### EnergyPlus 24.1 (OpenStudio):
- Sintaxe mais restritiva para HVACTemplate
- Campo `dehumidification_setpoint` requer valor numérico
- Alguns enums mudaram de nome

### EnergyPlus 25.1 (Standalone):
- Sintaxe mais flexível
- Aceita nomes de constantes como strings
- Melhor mensagens de erro

## Arquivos Disponíveis

| Arquivo | Versão | Status | Uso |
|---------|--------|--------|-----|
| `laboratorio_arquitetura.idf` | 25.1 | ✅ Funcionando | EnergyPlus standalone |
| `laboratorio_arquitetura_v24.1.idf` | 24.1 | ⚠️ Precisa ajuste | OpenStudio (após conversão) |
| `laboratorio_arquitetura_backup.idf` | 23.2→25.1 | 📦 Backup | Referência |

## Próximos Passos

### Para continuar com versão 24.1:
1. **Importar no OpenStudio** (mais fácil):
   ```bash
   openstudio
   # File → Import → IDF → laboratorio_arquitetura.idf
   ```

2. **Ou criar arquivo compatível manualmente**:
   - Substituir `HVACTemplate:Zone:IdealLoadsAirSystem` por:
     - `ZoneHVAC:IdealLoadsAirSystem` (sem template)
     - Ou usar sistema HVAC completo

### Para usar versão 25.1 (já funcionando):
```bash
python3 scripts/executar_simulacao.py
python3 scripts/analisar_resultados.py
```

## Comandos Úteis

### Verificar versão do EnergyPlus:
```bash
# Versão 25.1 (standalone)
/usr/local/bin/energyplus --version

# Versão 24.1 (OpenStudio)
/usr/local/openstudioapplication-1.8.0/EnergyPlus/energyplus --version
```

### Converter IDF no OpenStudio:
```bash
# Via linha de comando (se suportado)
openstudio translate --idf models/laboratorio_arquitetura.idf
```

---

**Recomendação:** Use o arquivo `laboratorio_arquitetura.idf` (v25.1) que já está funcionando perfeitamente, e se precisar usar no OpenStudio, importe-o pela interface gráfica que fará a conversão automaticamente.

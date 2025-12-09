# Dados Coletados para Simulação Térmica
## Grupo 2 - Laboratório de Arquitetura - UFC Quixadá

**Data da coleta:** 09/12/2024  
**Fonte dos materiais:** Memorial Descritivo - Edital 90009/2024 (Bloco Didático 5 UFC Quixadá)

---

## 📐 1. DIMENSÕES DO LABORATÓRIO

| Parâmetro | Valor | Status |
|-----------|-------|--------|
| Comprimento (X) | 7.06 m | ✅ |
| Largura (Y) | 9.39 m | ✅ |
| Altura (pé-direito) | 2.68 m | ✅ |
| Área útil | 66.29 m² | ✅ |
| Ângulo Norte | 342° | ✅ |

---

## 🪟 2. JANELAS (4 unidades - tipo correr, 2 folhas)

### Dimensões de cada janela:
| Parâmetro | Valor |
|-----------|-------|
| Largura | 1.55 m |
| Altura | 1.17 m |
| Peitoril (do chão) | 1.00 m (estimado) |

### Posicionamento na parede lateral direita (profundidade 9.39m):
| Janela | Posição Y inicial | Posição Y final |
|--------|-------------------|-----------------|
| 1 | 0.36 m | 1.91 m |
| 2 | 2.755 m | 4.305 m |
| 3 | 5.15 m | 6.70 m |
| 4 | 7.48 m | 9.03 m |

- **Distância entre janelas:** 0.845 m (84.5 cm)
- **Distância da parede frontal/traseira:** 0.36 m (36 cm)
- **Localização:** Parede lateral direita (X=7.06m)

### Especificação do vidro (conforme PDF):
- Tipo: Vidro liso comum transparente
- Espessura: 4 mm
- Esquadria: Alumínio de correr com 2 folhas

---

## ❄️ 3. AR-CONDICIONADOS (2 unidades)

| Parâmetro | Valor |
|-----------|-------|
| Marca | Springer |
| Modelo | Carrier Space 42XQM30C5/38KCA030515MC |
| Capacidade | 30.000 BTU/h (8.8 kW) |
| Tipo | Split |
| Selo Procel | C |
| Vazão de ar | 1090 m³/h |
| Funcionamento | Seg-Sex: 07:00-18:00 |

---

## 🚪 4. PORTA (duas folhas desiguais)

| Parâmetro | Valor |
|-----------|-------|
| Largura total | 1.195 m (80 + 39.5 cm) |
| Folha grande | 0.80 m |
| Folha pequena | 0.395 m |
| Altura | 2.10 m |
| Material | Madeira maciça |
| Visor | Sim (20x100 cm, vidro incolor) |

---

## 🧱 5. MATERIAIS DE CONSTRUÇÃO (do PDF)

### 5.1 Paredes Externas

**Composição (de fora para dentro):**

| Camada | Material | Espessura |
|--------|----------|-----------|
| 1 | Pintura texturizada acrílica | - |
| 2 | Emassamento acrílico (2 demãos) | ~1 mm |
| 3 | Fundo selador acrílico | - |
| 4 | Reboco (argamassa cimento/areia 1:3) | ~10 mm |
| 5 | Emboço (argamassa cimento/areia 1:3) | ~15 mm |
| 6 | Chapisco aderente c/ aditivo acrílico | 5 mm |
| 7 | **Bloco cerâmico furado 9x19x19 cm** | **90 mm** |
| 8 | Chapisco (argamassa cimento/areia 1:3) | 5 mm |
| 9 | Emboço (argamassa cimento/areia 1:3) | ~15 mm |
| 10 | Reboco (argamassa cimento/areia 1:3) | ~10 mm |
| 11 | Emassamento massa látex (2 demãos) | ~1 mm |
| 12 | Fundo selador acrílico | - |
| 13 | Pintura látex acrílica (2 demãos) | - |

**Espessura total estimada:** ~16-18 cm

### 5.2 Cobertura/Teto

| Camada | Material | Espessura |
|--------|----------|-----------|
| 1 | Telha galvalume trapezoidal | 0.50 mm |
| 2 | Isolamento espuma rígida PU (35 kg/m³) | 30 mm |
| 3 | Telha galvalume trapezoidal | 0.50 mm |
| 4 | Câmara de ar | variável |
| 5 | Laje nervurada concreto armado (fck=25MPa) | ~250 mm |
| 6 | Forro gesso acartonado ou fibra mineral | 15-16 mm |

### 5.3 Piso

| Camada | Material | Espessura |
|--------|----------|-----------|
| 1 | Solo compactado | - |
| 2 | Piso morto concreto (fck=13,5MPa) | variável |
| 3 | Lona plástica preta | 150 μm |
| 4 | Regularização (argamassa cimento/areia 1:3) | 30 mm |
| 5 | Piso cerâmico esmaltado 45x45cm | ~10 mm |

---

## 💡 6. ILUMINAÇÃO

| Parâmetro | Valor |
|-----------|-------|
| Quantidade de luminárias | 6 |
| Lâmpadas por luminária | 2 LED tubulares T5 |
| Dimensão luminária | 1.19 m × 0.31 m |
| Potência por lâmpada | 10-20 W |
| Temperatura de cor | 5000K (branco) |
| Potência total | 120-240 W |

**Especificação do PDF:**
> "Luminária de embutir/sobrepor retangular corpo em chapa de aço, pintura epóxi branca com refletor em alumínio espelho, para 2 led tubular T5 de 10W, tonalidade 5000k, cor branca, grau de proteção IP20"

---

## 🌬️ 7. VENTILAÇÃO

| Parâmetro | Valor |
|-----------|-------|
| Ventilação natural | Não (janelas fechadas) |
| Ventiladores de teto | Não possui |
| Qualidade de vedação | Boa |

---

## 📊 8. RESUMO PARA O MODELO IDF

### Geometria:
```
Sala: 7.06m (X) × 9.39m (Y) × 2.68m (Z)
Orientação: 342° do Norte
```

### Janelas (4 unidades):
```
Cada janela: 1.55m × 1.17m
Peitoril: 1.00m
Posições X: 0.36, 2.755, 5.15, 7.545 metros
```

### Porta:
```
Dimensão: 1.195m × 2.10m
Posição: Parede oposta às janelas
```

### HVAC:
```
2× Split 30.000 BTU/h = 17.6 kW total
Funcionamento: 07:00-18:00 (Seg-Sex)
```

### Iluminação:
```
6 luminárias × 2 lâmpadas × 10-20W = 120-240W
```

---

## ⚠️ DADOS AINDA PENDENTES

- [ ] Altura exata do peitoril das janelas
- [ ] Posição dos ar-condicionados na parede
- [ ] Temperatura do termostato
- [ ] Ocupação típica (número de pessoas)
- [ ] Horários de ocupação detalhados
- [ ] Potência exata das lâmpadas (10W ou 20W)
- [ ] Quantidade e tipo de equipamentos (computadores, projetores)
- [ ] Existência de cortinas/persianas
- [ ] Fotos do laboratório

---

## 📝 RESPONSÁVEIS

- **Grupo:** 2
- **Disciplina:** Instrumentação
- **Campus:** UFC Quixadá

"""
Modificador de arquivos IDF para análise de sensibilidade.

Atualiza parâmetros específicos do modelo EnergyPlus usando eppy.
"""

import os
from pathlib import Path
from typing import Dict


class IDFModifier:
    """Modifica arquivos IDF com novos valores de parâmetros usando eppy."""
    
    def __init__(self, base_idf_path: str):
        self.base_idf_path = Path(base_idf_path)
        if not self.base_idf_path.exists():
            raise FileNotFoundError(f"Arquivo IDF base não encontrado: {base_idf_path}")
    
    def create_modified_idf(self, parameters: Dict[str, float], output_path: str):
        """
        Cria novo arquivo IDF com parâmetros modificados.
        
        Args:
            parameters: Dicionário com {nome_parametro: valor}
            output_path: Caminho do arquivo IDF modificado
        """
        from eppy.modeleditor import IDF
        
        # Configura eppy com IDD
        eplus_path = r"C:\EnergyPlusV25-1-0"
        idd_path = os.path.join(eplus_path, "Energy+.idd")
        IDF.setiddname(idd_path)
        
        # Carrega IDF base
        idf = IDF(str(self.base_idf_path))
        
        # Aplica modificações
        try:
            if 'absortancia_parede' in parameters:
                self._modify_wall_absorptance(idf, parameters['absortancia_parede'])
            
            if 'fator_solar_vidro' in parameters:
                self._modify_glass_shgc(idf, parameters['fator_solar_vidro'])
            
            if 'infiltracao_ar' in parameters:
                self._modify_infiltration(idf, parameters['infiltracao_ar'])
            
            if 'uso_cortinas' in parameters:
                self._modify_shading(idf, parameters['uso_cortinas'])
            
            if 'densidade_equipamentos' in parameters:
                self._modify_equipment_density(idf, parameters['densidade_equipamentos'])
            
            if 'ocupacao' in parameters:
                self._modify_occupancy(idf, parameters['ocupacao'])
            
            if 'setpoint_resfriamento' in parameters:
                self._modify_cooling_setpoint(idf, parameters['setpoint_resfriamento'])
            
            if 'cop_ac' in parameters:
                self._modify_cop(idf, parameters['cop_ac'])
            
            if 'condutividade_parede' in parameters:
                self._modify_wall_conductivity(idf, parameters['condutividade_parede'])
        except Exception as e:
            print(f"⚠ Aviso ao modificar parâmetro: {e}")
        
        # Salva arquivo modificado
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        idf.saveas(str(output_path))
    
    def _modify_wall_absorptance(self, idf, value: float):
        """Modifica absortância solar das paredes externas (Argamassa)."""
        mat = idf.getobject('MATERIAL', 'Argamassa_2_5cm')
        if mat:
            mat.Solar_Absorptance = value
    
    def _modify_glass_shgc(self, idf, value: float):
        """Modifica fator solar (SHGC) dos vidros."""
        vidro = idf.getobject('WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM', 'Vidro_Simples_4mm')
        if vidro:
            vidro.Solar_Heat_Gain_Coefficient = value
    
    def _modify_infiltration(self, idf, value: float):
        """Modifica taxa de infiltração de ar (ACH)."""
        # Procura por todos os objetos ZoneInfiltration
        for infiltration in idf.idfobjects['ZONEINFILTRATION:DESIGNFLOWRATE']:
            infiltration.Air_Changes_per_Hour = value
    
    def _modify_shading(self, idf, value: float):
        """Ativa/desativa sombreamento interno (cortinas) - NÃO IMPLEMENTADO."""
        # O IDF não possui objetos WindowShadingControl
        # Este parâmetro será ignorado por enquanto
        pass
    
    def _modify_equipment_density(self, idf, value: float):
        """Modifica densidade de potência de equipamentos (W/m²)."""
        # Área do laboratório: 66.29 m²
        area_lab = 66.29
        watts_total = value * area_lab
        
        # Procura pelo equipamento principal (pode ser Projetor ou similar)
        for equip in idf.idfobjects['ELECTRICEQUIPMENT']:
            # Modifica apenas se usar EquipmentLevel
            if hasattr(equip, 'Design_Level_Calculation_Method'):
                if equip.Design_Level_Calculation_Method == 'EquipmentLevel':
                    equip.Design_Level = watts_total
                    break
    
    def _modify_occupancy(self, idf, value: float):
        """Modifica densidade de ocupação (pessoas/m²)."""
        # Área do laboratório: 66.29 m²
        area_lab = 66.29
        num_people = int(value * area_lab)
        
        # Procura pelo objeto People
        for people in idf.idfobjects['PEOPLE']:
            # Modifica apenas se usar método "People"
            if hasattr(people, 'Number_of_People_Calculation_Method'):
                if people.Number_of_People_Calculation_Method == 'People':
                    people.Number_of_People = num_people
                    break
    
    def _modify_cooling_setpoint(self, idf, value: float):
        """Modifica setpoint de temperatura de resfriamento."""
        # Procura pelo schedule de termostato de resfriamento
        for schedule in idf.idfobjects['SCHEDULE:COMPACT']:
            if 'Resfriamento' in schedule.Name or 'Cooling' in schedule.Name:
                # Modifica o último campo (valor da temperatura)
                # Schedule:Compact tem campos variáveis, procura por "Until:"
                for i, field in enumerate(schedule.obj):
                    if isinstance(field, str) and 'Until' in field:
                        # Próximo campo é o valor
                        if i + 1 < len(schedule.obj):
                            try:
                                # Tenta converter para float para confirmar que é um valor
                                float(schedule.obj[i + 1])
                                schedule.obj[i + 1] = value
                            except ValueError:
                                continue
    
    def _modify_cop(self, idf, value: float):
        """Modifica COP do sistema de ar condicionado - NÃO APLICÁVEL."""
        # O sistema usa ZoneHVAC:IdealLoadsAirSystem que não tem COP
        # Este parâmetro será ignorado
        pass
    
    def _modify_wall_conductivity(self, idf, value: float):
        """Modifica condutividade térmica das paredes (bloco cerâmico)."""
        mat = idf.getobject('MATERIAL', 'Bloco_Ceramico_9cm')
        if mat:
            mat.Conductivity = value


def create_simulation_idf(sim_id: int, parameters: Dict[str, float], 
                         base_idf: str, output_dir: str) -> str:
    """
    Cria arquivo IDF para uma simulação específica.
    
    Args:
        sim_id: ID da simulação
        parameters: Dicionário com parâmetros
        base_idf: Caminho do IDF base
        output_dir: Diretório para salvar IDF modificado
    
    Returns:
        Caminho do arquivo IDF criado
    """
    sim_id = int(sim_id)  # Garante que é int
    modifier = IDFModifier(base_idf)
    output_path = Path(output_dir) / f"sim_{sim_id:04d}" / "model.idf"
    modifier.create_modified_idf(parameters, str(output_path))
    
    return str(output_path)


if __name__ == "__main__":
    # Teste: cria IDF modificado
    print("Testando modificação de IDF com eppy...")
    
    test_params = {
        'absortancia_parede': 0.85,
        'fator_solar_vidro': 0.65,
        'infiltracao_ar': 0.8,
        'densidade_equipamentos': 15.0,
        'ocupacao': 0.35,
        'setpoint_resfriamento': 22.5,
        'condutividade_parede': 1.2,
    }
    
    try:
        idf_path = create_simulation_idf(
            sim_id=1,
            parameters=test_params,
            base_idf='models/laboratorio_6zonas.idf',
            output_dir='results/test_sensitivity'
        )
        print(f"✓ IDF de teste criado: {idf_path}")
    except Exception as e:
        print(f"✗ Erro ao criar IDF: {e}")
        import traceback
        traceback.print_exc()

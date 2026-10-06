"""
main.py - Demonstração executável do CRM Dashboard (Padrão MVC).

Instancia o Model, associa ao Controller e simula operações do usuário,
renderizando visões distintas (Tabela Operacional e Painel Executivo de KPIs).
"""

from models.crm_model import CrmModel, LeadStage
from controllers.crm_controller import CrmController


def main() -> None:
    print("=" * 76)
    print("DEMONSTRAÇÃO: Arquitetura MVC (CRM & Analytics Dashboard)")
    print("=" * 76)

    # 1. Instanciação dos componentes MVC
    model = CrmModel()
    controller = CrmController(model)

    # 2. Usuário adiciona oportunidades de negócio
    id_1 = controller.handle_create_lead("Ana Paula", "Fintech Nubox", 45000.0)
    id_2 = controller.handle_create_lead("Rodrigo Costa", "Logística Express", 28000.0)
    id_3 = controller.handle_create_lead("Mariana Rios", "Varejo Global", 95000.0)
    id_4 = controller.handle_create_lead("Felipe Melo", "Indústria Alpha", 15000.0)
    id_5 = controller.handle_create_lead("Carla Dias", "Startup EdTech", 12000.0)

    # 3. Usuário avança os estágios do funil
    controller.handle_advance_lead(id_1, LeadStage.CLOSED_WON)  # Ganho R$ 45k
    controller.handle_advance_lead(id_2, LeadStage.PROPOSAL)
    controller.handle_advance_lead(id_3, LeadStage.CLOSED_WON)  # Ganho R$ 95k
    controller.handle_advance_lead(id_4, LeadStage.QUALIFIED)
    controller.handle_advance_lead(id_5, LeadStage.CLOSED_LOST) # Perdido R$ 12k

    # 4. Renderização da Visão 1: Tabela Operacional de Leads
    controller.display_operational_table()

    # 5. Renderização da Visão 2: Dashboard Executivo com Métricas e Funil
    controller.display_executive_kpis()


if __name__ == "__main__":
    main()

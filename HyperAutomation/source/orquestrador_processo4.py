"""
Orquestrador CLI - Processo 4 (SAC e Atendimento ao Cliente)
Permite a execução autônoma do Processo 4 ou integrado ao BotCity Maestro.
"""
import sys
import argparse
from pathlib import Path
from botcity.maestro import BotMaestroSDK, AutomationTaskFinishStatus

BASE_DIR = Path(__file__).resolve().parent
PATH_ROOT = BASE_DIR.parent

sys.path.append(str(BASE_DIR))
sys.path.append(str(PATH_ROOT / "resources"))

from processo_atendimento.processo_sac import ProcessoSAC, PLANILHA_MESTRA, PLANILHA_SAC


def main():
    try:
        maestro = BotMaestroSDK.from_sys_args()
    except Exception:
        maestro = BotMaestroSDK()

    parser = argparse.ArgumentParser(
        description="Orquestrador HyperAutomation - Processo 4 (SAC e Atendimento)"
    )
    parser.add_argument(
        "-p", "--planilha-mestra",
        type=str,
        default=None,
        help="Caminho personalizado para a Planilha Mestra (opcional)"
    )
    parser.add_argument(
        "-s", "--planilha-sac",
        type=str,
        default=None,
        help="Caminho personalizado para a planilha de atendimentos SAC (opcional)"
    )

    args, _ = parser.parse_known_args()

    planilha_mestra = Path(args.planilha_mestra) if args.planilha_mestra else PLANILHA_MESTRA
    planilha_sac = Path(args.planilha_sac) if args.planilha_sac else PLANILHA_SAC

    task_id = None
    if maestro.is_online:
        execution = maestro.get_execution()
        task_id = execution.task_id
        print(f"[BOTCITY MAESTRO] Task ID identificada: {task_id}")

        params = execution.parameters or {}
        if "planilha_mestra" in params:
            planilha_mestra = Path(params.get("planilha_mestra"))
        if "planilha_sac" in params:
            planilha_sac = Path(params.get("planilha_sac"))

    try:
        processo = ProcessoSAC(
            caminho_planilha_mestra=planilha_mestra,
            caminho_planilha_sac=planilha_sac
        )
        resultado = processo.executar()

        if maestro.is_online and task_id:
            maestro.finish_task(
                task_id=task_id,
                status=AutomationTaskFinishStatus.SUCCESS,
                message=f"Processo 4 (SAC) concluído com sucesso. Total processados: {resultado.get('total_processados', 0)}"
            )
        return resultado

    except Exception as e:
        print(f"[ERRO PROCESSO 4 - SAC] Falha na execução: {e}")
        if maestro.is_online and task_id:
            maestro.finish_task(
                task_id=task_id,
                status=AutomationTaskFinishStatus.FAILED,
                message=f"Falha no Processo 4 (SAC): {e}"
            )
        raise e


if __name__ == "__main__":
    main()

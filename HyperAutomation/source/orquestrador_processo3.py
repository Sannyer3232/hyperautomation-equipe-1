"""
Orquestrador CLI - Processo 3 (Cadastro no Portal Fake via Planilha Mestra)
Permite a execução autônoma do Processo 3 ou integrado ao BotCity Maestro.
"""
import sys
import argparse
from pathlib import Path
from botcity.maestro import BotMaestroSDK, AutomationTaskFinishStatus

BASE_DIR = Path(__file__).resolve().parent
PATH_ROOT = BASE_DIR.parent

sys.path.append(str(BASE_DIR))
sys.path.append(str(PATH_ROOT / "resources"))

from processo_cadastro import executar_processo3


def main():
    maestro = BotMaestroSDK.from_sys_args()

    parser = argparse.ArgumentParser(
        description="Orquestrador HyperAutomation - Processo 3 (Cadastro via Planilha Mestra)"
    )
    parser.add_argument(
        "-p", "--planilha",
        type=str,
        default=None,
        help="Caminho personalizado para a Planilha_Mestra.xlsx (opcional)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=None,
        help="Executar navegador em modo headless"
    )
    parser.add_argument(
        "--no-headless",
        action="store_false",
        dest="headless",
        help="Executar navegador com interface gráfica visível"
    )

    args, _ = parser.parse_known_args()

    headless = args.headless
    planilha_path = Path(args.planilha) if args.planilha else None

    task_id = None
    if maestro.is_online:
        execution = maestro.get_execution()
        task_id = execution.task_id
        print(f"[BOTCITY MAESTRO] Task ID identificada: {task_id}")

        params = execution.parameters or {}
        if "headless" in params:
            headless = str(params.get("headless")).lower() in ("true", "1", "yes")
        if "planilha" in params:
            planilha_path = Path(params.get("planilha"))

    if headless is None:
        headless = True if (maestro and maestro.is_online) else False

    try:
        resultado = executar_processo3(
            caminho_planilha=planilha_path,
            headless=headless,
            maestro=maestro,
            task_id=task_id
        )

        if maestro.is_online and task_id:
            maestro.finish_task(
                task_id=task_id,
                status=AutomationTaskFinishStatus.SUCCESS,
                message=f"Processo 3 concluído. Total processados: {resultado.get('total_processados', 0)}"
            )

    except Exception as e:
        print(f"[ERRO PROCESSO 3] Falha na execução: {e}")
        if maestro.is_online and task_id:
            maestro.finish_task(
                task_id=task_id,
                status=AutomationTaskFinishStatus.FAILED,
                message=f"Falha no Processo 3: {e}"
            )
        raise e


if __name__ == "__main__":
    main()

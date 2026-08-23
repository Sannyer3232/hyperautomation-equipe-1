"""
Orquestrador CLI - Processo 5 (Relatórios e Gerência)
Permite a execução autônoma do Processo 5 ou integrado ao BotCity Maestro.
"""
import sys
import argparse
from pathlib import Path
from botcity.maestro import BotMaestroSDK, AutomationTaskFinishStatus

BASE_DIR = Path(__file__).resolve().parent
PATH_ROOT = BASE_DIR.parent

sys.path.append(str(BASE_DIR))
sys.path.append(str(PATH_ROOT / "resources"))

from processo_relatorios import executar_processo5


def main():
    try:
        maestro = BotMaestroSDK.from_sys_args()
    except Exception:
        maestro = BotMaestroSDK()

    parser = argparse.ArgumentParser(
        description="Orquestrador HyperAutomation - Processo 5 (Relatórios e Gerência)"
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
    parser.add_argument(
        "-o", "--dir-saida",
        type=str,
        default=None,
        help="Diretório de saída para salvar os relatórios (opcional)"
    )

    args, _ = parser.parse_known_args()

    planilha_mestra = Path(args.planilha_mestra) if args.planilha_mestra else None
    planilha_sac = Path(args.planilha_sac) if args.planilha_sac else None
    dir_saida = Path(args.dir_saida) if args.dir_saida else None

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
        if "dir_saida" in params:
            dir_saida = Path(params.get("dir_saida"))

    try:
        resultado = executar_processo5(
            caminho_planilha_mestra=planilha_mestra,
            caminho_planilha_sac=planilha_sac,
            dir_saida=dir_saida
        )

        if maestro.is_online and task_id:
            maestro.finish_task(
                task_id=task_id,
                status=AutomationTaskFinishStatus.SUCCESS if resultado.get("sucesso") else AutomationTaskFinishStatus.FAILED,
                message=f"Processo 5 concluído. Total de clientes consolidados: {resultado.get('total_clientes', 0)}"
            )
        return resultado

    except Exception as e:
        print(f"[ERRO PROCESSO 5 - RELATÓRIOS] Falha na execução: {e}")
        if maestro.is_online and task_id:
            maestro.finish_task(
                task_id=task_id,
                status=AutomationTaskFinishStatus.FAILED,
                message=f"Falha no Processo 5: {e}"
            )
        raise e


if __name__ == "__main__":
    main()

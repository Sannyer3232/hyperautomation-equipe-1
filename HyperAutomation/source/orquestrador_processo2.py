import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PATH_ROOT = BASE_DIR.parent
sys.path.append(str(BASE_DIR))

from processo_atendimento.gestor_arquivos import GestorArquivos
from processo_organizacao.extrator_dados import ExtratorPDF
from processo_organizacao.planilha_mestra import GerenciadorPlanilha

def executar_processo2():
    print("=" * 75)
    print("INICIANDO ORQUESTRAÇÃO HYPERAUTOMATION - PROCESSO 2 (Organização de Dados)")
    print("=" * 75)
    
    gestor = GestorArquivos()
    # Garante que as pastas Sistema_Integrador_Portal_Fake e Arquivados sejam criadas
    gestor.garantir_estrutura_pastas()
    
    planilha_path = gestor.dir_sistema_integrador / "Planilha_Mestra.xlsx"
    gerenciador_planilha = GerenciadorPlanilha(planilha_path)
    
    # Busca os PDFs aprovados na pasta Documentos_OK
    arquivos_aprovados = list(gestor.dir_ok.glob("*.pdf"))

    
    if not arquivos_aprovados:
        print("[PROCESSO 2] Nenhum documento aprovado encontrado.")
        return
        
    print(f"[PROCESSO 2] Encontrados {len(arquivos_aprovados)} documentos aprovados. Iniciando processamento...\n")
    
    for pdf_path in arquivos_aprovados:
        print(f"Processando arquivo: {pdf_path.name}")
        pasta_origem = pdf_path.parent.name
        
        try:
            extrator = ExtratorPDF(pdf_path)
            dados = extrator.extrair_dados()
            
            if dados["cpf"] != "NÃO ENCONTRADO":
                print(f"  -> Dados Extraídos: Nome: {dados['nome_completo']} | CPF: {dados['cpf']} | Email: {dados['email']} | Tel: {dados['telefone']} | Endereço: {dados['endereco']}")
                sucesso = gerenciador_planilha.adicionar_registro(dados)
                
                # Independentemente de ter sido duplicado ou inserido novo, o documento foi processado, então arquivamos.
                gestor.arquivar_documento(pdf_path.name, pasta_origem=pasta_origem)
                
            else:
                print(f"  -> [ALERTA] Não foi possível extrair dados válidos de {pdf_path.name}.")
                
        except Exception as e:
            print(f"  -> [ERRO] Falha ao processar {pdf_path.name}: {str(e)}")
            
    print("\n" + "=" * 75)
    print("ORQUESTRAÇÃO DO PROCESSO 2 FINALIZADA COM SUCESSO!")
    print("=" * 75)

if __name__ == "__main__":
    executar_processo2()

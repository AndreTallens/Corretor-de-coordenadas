import os
from automacao_ibge import enviar_e_obter_ppp
from processador_dxf import gerar_dxf_corrigido

# --- CONFIGURAÇÃO MANUAL (Substitui o arquivo .config) ---
DADOS_EQUIPAMENTO = {
    "modelo_antena": "ESVE300PRONONE", 
    "altura_antena": 2.0, 
    "email_ibge": "andre.chouin.agrosas@gmail.com", # Seu e-mail cadastrado no IBGE
    "raiz_dados": r"C:\SistemaAgrosas_Dados_PY"
}

def executar():
    print("\n🚀 INICIANDO PROCESSAMENTO REAL")
    
    pasta_entrada = os.path.join(DADOS_EQUIPAMENTO['raiz_dados'], "Entrada")
    
    # Busca arquivos reais na pasta
    arquivos = os.listdir(pasta_entrada)
    txt = next((f for f in arquivos if f.endswith(('.txt', '.csv'))), None)
    rinex = next((f for f in arquivos if f.lower().endswith(('.o', '.zip', '.24o'))), None)

    if not txt or not rinex:
        print(f"❌ Erro: Coloque o TXT e o Rinex em: {pasta_entrada}")
        return

    # 1. OBTENÇÃO DOS DADOS REAIS (Site do IBGE)
    # Substitui a simulação de 'app_dxf.py' pela automação real
    coords_ppp = enviar_e_obter_ppp(os.path.join(pasta_entrada, rinex), DADOS_EQUIPAMENTO)

    if coords_ppp:
        # 2. GERAÇÃO DO DXF CORRIGIDO
        gerar_dxf_corrigido(
            caminho_csv_coletora=os.path.join(pasta_entrada, txt),
            coords_ppp=coords_ppp,
            nome_projeto="Levantamento_Final_Corrigido"
        )
        print("\n✅ DXF gerado com coordenadas oficiais do IBGE!")

if __name__ == "__main__":
    executar()
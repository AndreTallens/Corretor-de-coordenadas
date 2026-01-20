import os
import pandas as pd
import ezdxf
import requests

class SistemaAgrosasPython:
    def __init__(self):
        self.raiz = r"C:\SistemaAgrosas_Dados_PY"
        self.pasta_entrada = os.path.join(self.raiz, "Entrada")
        self.pasta_resultados = os.path.join(self.raiz, "Resultados")
        
        self.config_equipamento = {
            "modelo_antena": "ESVE300PRONONE",
            "altura": 2.0
        }
        self.setup_diretorios()

    def setup_diretorios(self):
        pastas = [self.raiz, self.pasta_entrada, self.pasta_resultados, os.path.join(self.raiz, "Logs")]
        for p in pastas:
            os.makedirs(p, exist_ok=True)
        print(f"✅ Estrutura de pastas pronta em: {self.raiz}")

    def processar_ppp_ibge(self, caminho_rinex):
        """
        Simula o processamento do RINEX. 
        No futuro, aqui conectaremos com a API ou Automação do IBGE.
        """
        print(f" Bollinger 🛰️  Processando RINEX: {os.path.basename(caminho_rinex)}")
        # Simulando uma coordenada corrigida (PPP)
        return {"n": 7345120.450, "e": 245130.120, "z": 540.30}

    def corrigir_e_gerar_dxf(self, arquivo_pontos, coord_ppp):
        print(f" 📐 Corrigindo pontos do arquivo: {os.path.basename(arquivo_pontos)}")
        
        # Lê o arquivo (ajuste o separador se o seu TXT usar ';' ou TAB)
        df = pd.read_csv(arquivo_pontos)
        
        # Cálculo do Delta (Base lida vs Base PPP)
        base_original = df.iloc[0] 
        dn = coord_ppp['n'] - base_original['Norte']
        de = coord_ppp['e'] - base_original['Este']
        dz = coord_ppp['z'] - base_original['Z']

        doc = ezdxf.new('R2010')
        msp = doc.modelspace()

        for _, ponto in df.iterrows():
            n_corr, e_corr, z_corr = ponto['Norte'] + dn, ponto['Este'] + de, ponto['Z'] + dz
            camada = str(ponto['Descricao'])

            if camada not in doc.layers:
                doc.layers.new(name=camada)
            
            msp.add_point((e_corr, n_corr, z_corr), dxfattribs={'layer': camada})
            msp.add_text(f"{ponto['Nome']}", 
                         dxfattribs={'layer': camada, 'height': 0.2}).set_placement((e_corr + 0.1, n_corr + 0.1))

        output = os.path.join(self.pasta_resultados, "Levantamento_Final.dxf")
        doc.saveas(output)
        print(f" 💾 Sucesso! DXF gerado: {output}")

# --- AMBIENTE DE TESTE ---
if __name__ == "__main__":
    app = SistemaAgrosasPython()
    
    print("\n--- INICIANDO TESTE ---")
    print(f"👉 Por favor, coloque seu arquivo .txt e o .o (Rinex) em: {app.pasta_entrada}")
    
    # Busca arquivos na pasta de entrada
    arquivos = os.listdir(app.pasta_entrada)
    arquivo_txt = next((f for f in arquivos if f.endswith('.txt') or f.endswith('.csv')), None)
    arquivo_rinex = next((f for f in arquivos if f.lower().endswith(('.zip', '.o', '.23o'))), None)

    if arquivo_txt and arquivo_rinex:
        # 1. Simula envio ao IBGE
        resultado_ppp = app.processar_ppp_ibge(os.path.join(app.pasta_entrada, arquivo_rinex))
        
        # 2. Processa o DXF
        app.corrigir_e_gerar_dxf(os.path.join(app.pasta_entrada, arquivo_txt), resultado_ppp)
    else:
        print("❌ Erro: Certifique-se de que existe um arquivo de pontos (.txt) e um Rinex na pasta de Entrada.")
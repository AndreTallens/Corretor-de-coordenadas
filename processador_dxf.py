import ezdxf
import pandas as pd
import os

def gerar_dxf_corrigido(caminho_csv_coletora, coords_ppp, nome_projeto="Levantamento_Agrosas"):
    """
    Lê o CSV da coletora com Sigmas, aplica a correção do PPP e gera o DXF.
    """
    # 1. Definir o cabeçalho baseado no formato da sua coletora
    colunas = ['Nome', 'Norte', 'Este', 'Z', 'Descricao', 'SigmaN', 'SigmaE', 'SigmaZ']
    
    # Lê o arquivo ignorando colunas extras e usando os nomes acima
    df = pd.read_csv(caminho_csv_coletora, names=colunas, header=0)
    
    # 2. Calcular o Vetor de Correção (Delta)
    # Usamos a primeira linha (Base) para o cálculo
    n_base_campo = df.iloc[0]['Norte']
    e_base_campo = df.iloc[0]['Este']
    z_base_campo = df.iloc[0]['Z']
    
    delta_n = coords_ppp['n_ppp'] - n_base_campo
    delta_e = coords_ppp['e_ppp'] - e_base_campo
    delta_z = coords_ppp['z_ppp'] - z_base_campo
    
    print(f"Vetor de Correção: N:{delta_n:.3f} | E:{delta_e:.3f}")

    # 3. Criar o documento DXF
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # 4. Criar camadas e pontos corrigidos
    for _, linha in df.iterrows():
        # Aplicar translação
        n_corr = linha['Norte'] + delta_n
        e_corr = linha['Este'] + delta_e
        z_corr = linha['Z'] + delta_z
        
        # Camada baseada na descrição
        desc = str(linha['Descricao']).strip().upper() if pd.notna(linha['Descricao']) else "0"
        camada = desc.split()[0] # Pega apenas a primeira palavra (ex: 'REPRESA')

        if camada not in doc.layers:
            doc.layers.new(name=camada)

        # Lógica de cor baseada no Sigma (Alerta visual)
        # Se o erro for maior que 5cm (0.050), o ponto fica vermelho
        cor = 1 if (linha['SigmaN'] > 0.05 or linha['SigmaE'] > 0.05) else 256 # 256 = ByLayer

        # Adicionar Ponto e Texto Técnico
        msp.add_point((e_corr, n_corr, z_corr), dxfattribs={'layer': camada, 'color': cor})
        
        texto_label = f"{linha['Nome']} (sN:{linha['SigmaN']:.3f})"
        msp.add_text(
            texto_label, 
            dxfattribs={'layer': camada, 'height': 0.12, 'color': cor}
        ).set_placement((e_corr + 0.1, n_corr + 0.1, z_corr))

    # 5. Salvar na pasta de Resultados
    diretorio_saida = r"C:\SistemaAgrosas_Dados_PY\Resultados"
    os.makedirs(diretorio_saida, exist_ok=True)
        
    caminho_final = os.path.join(diretorio_saida, f"{nome_projeto}.dxf")
    doc.saveas(caminho_final)
    print(f"✅ DXF Técnico com Sigmas salvo em: {caminho_final}")
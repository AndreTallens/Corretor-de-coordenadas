import ezdxf
import pandas as pd
import os

def gerar_dxf_corrigido(caminho_csv_coletora, coords_ppp, nome_projeto="Levantamento_Agrosas"):
    """
    Lê o CSV da coletora, aplica a correção do PPP e gera um arquivo DXF.
    Baseado nas configurações do Sistema Agrosas.
    """
    # 1. Carregar os dados da coletora
    df = pd.read_csv(caminho_csv_coletora)
    
    # 2. Calcular o Vetor de Correção (Delta)
    # Pegamos a primeira linha do CSV como a base original de campo
    n_base_campo = df.iloc[0]['Norte']
    e_base_campo = df.iloc[0]['Este']
    z_base_campo = df.iloc[0]['Z']
    
    delta_n = coords_ppp['n_ppp'] - n_base_campo
    delta_e = coords_ppp['e_ppp'] - e_base_campo
    delta_z = coords_ppp['z_ppp'] - z_base_campo
    
    print(f"Vetor de Correção: N:{delta_n:.3f} | E:{delta_e:.3f}")

    # 3. Criar o documento DXF (Versão R2010 para alta compatibilidade)
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # 4. Criar camadas e pontos
    for _, linha in df.iterrows():
        # Aplicar correção
        n_corr = linha['Norte'] + delta_n
        e_corr = linha['Este'] + delta_e
        z_corr = linha['Z'] + delta_z
        
        # Camada baseada na descrição (ex: CERCA, ESTRADA)
        camada = str(linha['Descricao']).upper() if pd.notna(linha['Descricao']) else "0"
        
        if camada not in doc.layers:
            doc.layers.new(name=camada)

        # Adicionar Ponto e Nome do Ponto
        msp.add_point((e_corr, n_corr, z_corr), dxfattribs={'layer': camada})
        msp.add_text(
            str(linha['Nome']), 
            dxfattribs={'layer': camada, 'height': 0.15}
        ).set_placement((e_corr + 0.1, n_corr + 0.1, z_corr))

    # 5. Salvar no diretório padrão do Sistema Agrosas
    diretorio_saida = r"C:\SistemaAgrosas_Dados"
    if not os.path.exists(diretorio_saida):
        os.makedirs(diretorio_saida)
        
    caminho_final = os.path.join(diretorio_saida, f"{nome_projeto}.dxf")
    doc.saveas(caminho_final)
    print(f"Arquivo DXF salvo com sucesso em: {caminho_final}")
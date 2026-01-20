from playwright.sync_api import sync_playwright
import time
import re
import os
import requests
import zipfile
import io

def extrair_dados_do_txt(conteudo_txt):
    """Analisa o texto do relatório do IBGE para extrair coordenadas UTM e Altitude"""
    dados = {"n_ppp": 0.0, "e_ppp": 0.0, "z_ppp": 0.0}
    
    # Busca Coordenadas UTM (Procura por sequências numéricas típicas de N e E)
    match_utm = re.findall(r'(\d{6,}\.\d{3})', conteudo_txt)
    if len(match_utm) >= 2:
        dados["n_ppp"] = float(match_utm[0])
        dados["e_ppp"] = float(match_utm[1])

    # Busca Altitude Geométrica (h)
    match_h = re.search(r'(?:Altitude Geometrica|h\(m\))\s+([\d.-]+)', conteudo_txt)
    if match_h:
        dados["z_ppp"] = float(match_h.group(1))
    
    return dados

def enviar_e_obter_ppp(caminho_rinex, config_equipamento):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Acessando o site do IBGE...")
        page.goto("https://www.ibge.gov.br/geociencias/informacoes-sobre-posicionamento-geodesico/servicos-para-posicionamento-geodesico/20165-ppp.html?=&t=processar-os-dados")

        frame = page.frame_locator("iframe[src*='ppp']")

        print(f"Preenchendo formulário para: {config_equipamento['email_ibge']}")
        frame.locator("input[name='arquivo']").set_input_files(caminho_rinex)
        frame.locator("select[name='antena']").select_option(label=config_equipamento['modelo_antena'])
        frame.locator("input[name='altura']").fill(str(config_equipamento['altura_antena']))
        frame.locator("input[name='email']").fill(config_equipamento['email_ibge'])
        frame.locator("input[value='estatico']").check()

        print("Enviando dados para processamento...")
        frame.locator("input[type='submit']").click()

        # --- NOVA PARTE: CAPTURA DO RETORNO ---
        print("Aguardando link de download (isso pode levar alguns minutos)...")
        
        # O IBGE gera um link para um arquivo .zip após o processamento
        try:
            # Espera até 10 minutos pelo link de download aparecer na tela
            link_elemento = frame.locator("a[href*='.zip']").wait_for(timeout=600000)
            url_download = frame.locator("a[href*='.zip']").get_attribute("href")
            
            print(f"Processamento concluído! Baixando: {url_download}")
            
            # Baixa o arquivo ZIP
            resposta = requests.get(url_download)
            with zipfile.ZipFile(io.BytesIO(resposta.content)) as z:
                # Procura o arquivo de texto com as coordenadas (.pos ou .txt)
                for nome_arq in z.namelist():
                    if nome_arq.endswith('.pos') or (nome_arq.endswith('.txt') and 'relatorio' in nome_arq.lower()):
                        with z.open(nome_arq) as f:
                            print(f"Lendo resultados de: {nome_arq}")
                            conteudo = f.read().decode('utf-8')
                            coords = extrair_dados_do_txt(conteudo)
                            print(f"--- COORDENADAS PPP OBTIDAS ---")
                            print(f"NORTE: {coords['n_ppp']} | ESTE: {coords['e_ppp']} | ALTITUDE: {coords['z_ppp']}")
                            return coords

        except Exception as e:
            print(f"Erro ao obter retorno do IBGE: {e}")
        
        browser.close()
        return None

# Para rodar usando seu arquivo de configuração
# config = {
#    "modelo_antena": "ESVE300PRONONE", 
#    "altura_antena": 2.0, 
#    "email_ibge": "andre.chouin.agrosas@gmail.com"
# }
# resultado_final = enviar_e_obter_ppp('sua_base.obs', config)
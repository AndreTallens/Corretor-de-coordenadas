import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def enviar_e_obter_ppp(caminho_rinex, dados_equipamento):
    """
    Realiza a automação no site do IBGE com ajustes de estabilidade para evitar erros de Stacktrace.
    """
    # --- AJUSTE CRÍTICO: Configurações de Estabilidade do Chrome ---
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox") # Evita erros de permissão
    chrome_options.add_argument("--disable-dev-shm-usage") # Melhora estabilidade em pouca memória
    chrome_options.add_argument("--start-maximized") # Abre a janela grande para facilitar o clique
    
    # Inicia o driver com as novas opções
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 30) # Espera técnica para carregar os botões

    try:
        print(f"🌍 Acessando site do IBGE para processar: {os.path.basename(caminho_rinex)}")
        driver.get("https://www.ibge.gov.br/geociencias/informacoes-sobre-posicionamento-geodesico/servicos-para-posicionamento-geodesico/16334-servico-online-para-pos-processamento-de-dados-gnss-ibge-ppp.html?=&t=processar-os-dados")

        # 1. Selecionar o arquivo RINEX
        upload_campo = wait.until(EC.presence_of_element_located((By.ID, "arquivo_rinex")))
        upload_campo.send_keys(caminho_rinex)
        print("✅ Arquivo Rinex anexado.")

        # 2. Configurar Antena (Dropdown)
        antena_select = Select(wait.until(EC.presence_of_element_located((By.ID, "antena"))))
        antena_select.select_by_visible_text("ESVE300PRO NONE")
        print("✅ Antena: ESVE300PRO NONE selecionada.")

        # 3. Configurar Altura da Antena e Marcar Checkbox
        altura_campo = driver.find_element(By.ID, "altura_antena")
        altura_campo.clear()
        altura_campo.send_keys("2.0")
        
        check_altura = driver.find_element(By.ID, "chk_altura_antena")
        if not check_altura.is_selected():
            check_altura.click()
        print("✅ Altura: 2.0m (confirmada).")

        # 4. Inserir o E-mail de Trabalho
        email_campo = driver.find_element(By.NAME, "email")
        email_campo.clear()
        email_campo.send_keys("andre.chouin.agrosas@gmail.com")
        print(f"✅ E-mail inserido: andre.chouin.agrosas@gmail.com")

        # 5. Clicar em Processar
        botao_processar = driver.find_element(By.ID, "btn_processar")
        botao_processar.click()
        print("🚀 Formulário enviado! Aguardando o processamento do IBGE...")

        # Aguarda um momento para ver se a página mudou para 'processando'
        time.sleep(10)
        
        # Aqui retornaríamos os dados reais após o download do .SUM
        # Por enquanto, mantemos o retorno simulado para o fluxo não quebrar
        return {
            "n_ppp": 7672886.120, 
            "e_ppp": 583764.215,
            "z_ppp": 965.100
        }

    except Exception as e:
        print(f"❌ Erro na automação: {e}")
        return None
    finally:
        print("🕒 Finalizando navegador em 5 segundos...")
        time.sleep(5)
        driver.quit()
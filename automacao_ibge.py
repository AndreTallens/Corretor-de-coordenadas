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
    Realiza a automação no site do IBGE-PPP preenchendo os dados conforme padrão Agrosas.
    """
    chrome_options = Options()
    # Descomente a linha abaixo se quiser que o navegador rode escondido (sem interface)
    # chrome_options.add_argument("--headless") 
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 30)

    try:
        print(f"🌍 Acessando site do IBGE para processar: {os.path.basename(caminho_rinex)}")
        driver.get("https://www.ibge.gov.br/geociencias/informacoes-sobre-posicionamento-geodesico/servicos-para-posicionamento-geodesico/16334-servico-online-para-pos-processamento-de-dados-gnss-ibge-ppp.html?=&t=processar-os-dados")

        # 1. Selecionar o arquivo RINEX
        upload_campo = wait.until(EC.presence_of_element_located((By.ID, "arquivo_rinex")))
        upload_campo.send_keys(caminho_rinex)
        print("✅ Arquivo selecionado.")

        # 2. Selecionar Tipo de Antena
        # O valor 'ESVE300PRO NONE' deve ser idêntico ao que aparece no site
        antena_dropdown = Select(driver.find_element(By.ID, "antena"))
        antena_dropdown.select_by_visible_text("ESVE300PRO NONE")
        print("✅ Antena configurada: ESVE300PRO NONE")

        # 3. Inserir Altura da Antena
        altura_campo = driver.find_element(By.ID, "altura_antena")
        altura_campo.clear()
        altura_campo.send_keys("2.0")
        print("✅ Altura da antena definida: 2.0")

        # 4. Marcar Checkbox de confirmação de altura
        check_altura = driver.find_element(By.ID, "chk_altura_antena")
        if not check_altura.is_selected():
            check_altura.click()
        print("✅ Confirmação de alteração de altura marcada.")

        # 5. Inserir E-mail
        email_campo = driver.find_element(By.NAME, "email")
        email_campo.clear()
        email_campo.send_keys("andre.chouin.agrosas@gmail.com")
        print("✅ E-mail inserido.")

        # 6. Clicar em Processar
        botao_processar = driver.find_element(By.ID, "btn_processar")
        botao_processar.click()
        print("🚀 Enviado! Aguardando o processamento do IBGE...")

        # --- Lógica de Espera do Resultado ---
        # Aqui o script deve monitorar a página até que o link de download apareça.
        # Por padrão, o IBGE muda a URL ou exibe um link após alguns minutos.
        
        # Simulação de espera por link de download (Ajustar conforme o site se comportar)
        link_download = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "resultados")))
        url_resultado = link_download.get_attribute("href")
        
        # Para fins de teste, retornamos coordenadas fixas simuladas.
        # Na versão final, este script deve ler o arquivo .sum baixado.
        return {
            "n_ppp": 7672886.120, # Valores de exemplo que seriam lidos do PDF/SUM
            "e_ppp": 583764.215,
            "z_ppp": 965.100
        }

    except Exception as e:
        print(f"❌ Erro na automação: {e}")
        return None
    finally:
        # Mantém aberto por 5 segundos para você ver o resultado antes de fechar
        time.sleep(5)
        driver.quit()
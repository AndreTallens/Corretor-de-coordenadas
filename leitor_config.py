import xml.etree.ElementTree as ET

def carregar_configuracoes_agrosas(caminho_arquivo):
    try:
        # Carrega o XML do arquivo .config
        tree = ET.parse(caminho_arquivo)
        root = tree.getroot()

        # Busca a seção de equipamentos conforme seu arquivo original
        equip = root.find(".//equipmentsSection/Equipment")
        
        config = {
            "tipo_levantamento": equip.get("tipolevantamento"),
            "modelo_antena": equip.get("modeloAntena"),
            "altura_antena": float(equip.get("alturaAntena")),
            "email_ibge": equip.get("email"),
            "raiz_dados": root.find(".//appSettings/add[@key='Raiz']").get("value")
        }

        # Busca a string de conexão do banco de dados
        db_conn = root.find(".//connectionStrings/add[@name='adapt']").get("connectionString")

        return config, db_conn

    except Exception as e:
        print(f"Erro ao ler o arquivo .config: {e}")
        return None, None

# Teste de leitura
config, banco = carregar_configuracoes_agrosas('SistemaAgrosas_.exe.config')

if config:
    print("-" * 30)
    print(f"CONFIGURAÇÃO AGROSAS CARREGADA")
    print(f"E-mail: {config['email_ibge']}")
    print(f"Antena: {config['modelo_antena']} (H={config['altura_antena']}m)")
    print(f"Diretório Raiz: {config['raiz_dados']}")
    print("-" * 30)
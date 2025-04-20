from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import os, time

app = FastAPI()

# Diretório onde os PDFs serão salvos
DOWNLOAD_DIR = os.path.join(os.getcwd(), "certidoes")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Utilitário para configurar o ChromeDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }
    options.add_experimental_option("prefs", prefs)
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(), options=options)

# Função para emitir CND da Receita Federal
def emitir_cnd_receita(cnpj: str) -> str:
    driver = setup_driver()
    try:
        driver.get("https://servicos.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/Emitir")
        time.sleep(3)
        campo = driver.find_element(By.ID, "txtCNPJ")  # ID atualizado após inspeção
        campo.clear()
        campo.send_keys(cnpj)
        driver.find_element(By.ID, "btnConsultar").click()
        time.sleep(3)
        link = driver.find_element(By.LINK_TEXT, "Clique aqui para imprimir")
        link.click()
        time.sleep(5)
        return "CND emitida com sucesso."
    except Exception as e:
        return f"Erro ao emitir CND: {str(e)}"
    finally:
        driver.quit()

# Endpoint principal para emissão da certidão
@app.post("/emitir_certidoes")
def emitir_certidoes(cnpj: str = Form(...), razao_social: str = Form(...)):
    pasta_empresa = os.path.join(DOWNLOAD_DIR, cnpj)
    os.makedirs(pasta_empresa, exist_ok=True)

    status_cnd = emitir_cnd_receita(cnpj)

    return JSONResponse(content={
        "cnpj": cnpj,
        "razao_social": razao_social,
        "status_cnd": status_cnd
    })

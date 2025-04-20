from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
import os, time, subprocess

app = FastAPI()

# Instala o Chrome e o ChromeDriver em diretórios com permissão
CHROMEDRIVER_PATH = "/tmp/chromedriver"
CHROME_BIN_PATH = "/opt/google/chrome/google-chrome"

def instalar_chrome():
    if not os.path.exists(CHROME_BIN_PATH):
        subprocess.call("apt-get update", shell=True)
        subprocess.call("apt-get install -y wget unzip", shell=True)
        subprocess.call("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb", shell=True)
        subprocess.call("apt install -y ./google-chrome-stable_current_amd64.deb", shell=True)
        subprocess.call("wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip", shell=True)
        subprocess.call("unzip /tmp/chromedriver.zip -d /tmp/", shell=True)

# Diretório onde os PDFs serão salvos
DOWNLOAD_DIR = os.path.join(os.getcwd(), "certidoes")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Configura o Selenium para rodar no Render (headless)
def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = CHROME_BIN_PATH
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)

# Função para emitir CND da Receita Federal
def emitir_cnd_receita(cnpj: str) -> str:
    instalar_chrome()
    driver = setup_driver()
    try:
        driver.get("https://servicos.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/Emitir")
        time.sleep(2)
        driver.find_element(By.ID, "CNPJ").send_keys(cnpj)
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

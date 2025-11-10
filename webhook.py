import sys
import requests
import urllib3
import json
import os
from datetime import datetime


UNIFI_HOST = os.getenv('HOST')
UNIFI_PORT = os.getenv('PORT')
SITE_ID = "default"
VERIFY_SSL = False
API_KEY = os.getenv('API_KEY')


PUSH_URL_VIVO = os.getenv('LINK_WAN2')
PUSH_URL_MUNDIVOX = os.getenv('LINK_WAN1')


SLACK_WEBHOOK_URL = os.getenv('SLACK_URL')


STATE_FILE = "wan_status_state.json"

def load_previous_state():
    """Carrega o estado anterior dos links"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_current_state(state):
    """Salva o estado atual dos links"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def send_slack_notification(link_name, is_up, previous_was_up):
    """Envia notificação pro Slack quando há mudança de estado"""

    if is_up == previous_was_up:
        return
    
    agora = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
    
    if is_up:
        emoji = "🟢"
        cor = "#36C5F0"  
        mensagem = f"Serviço Recuperado: O link *{link_name}* está novamente operacional, obrigado."
        status_texto = "ONLINE / ESTÁVEL"
    else:
        emoji = "🔴"
        cor = "#FF0000" 
        mensagem = f"@channel Atenção: O link *{link_name}* está com uma interrupção no momento.\nA conexão pode ficar instável por um tempo. Nossa equipe de TI já foi avisada e está cuidando do problema."
        status_texto = "OFFLINE / INSTÁVEL"
    
    payload = {
        "attachments": [
            {
                "color": cor,
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{emoji} {mensagem}"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Status:*\n{status_texto}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Horário:*\n{agora}"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        if response.status_code == 200:
            print(f"INFO: Notificação Slack enviada para {link_name}")
        else:
            print(f"ERRO: Falha ao enviar notificação Slack. Status: {response.status_code}")
    except Exception as e:
        print(f"ERRO: Falha ao enviar notificação Slack: {e}")

def send_push(url, link_name):
    """Envia heartbeat pro Uptime Kuma"""
    try:
        requests.get(url, timeout=10)
        print(f"INFO: Heartbeat Uptime Kuma enviado para: {link_name}")
    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha ao enviar heartbeat para {link_name}. Erro: {e}")

if not VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = f"https://{UNIFI_HOST}:{UNIFI_PORT}"
DEVICE_LIST_URL = f"{BASE_URL}/proxy/network/api/s/{SITE_ID}/stat/device"

session = requests.Session()
session.verify = VERIFY_SSL
session.headers.update({
    "X-API-KEY": API_KEY,
    "Accept": "application/json"
})

print("INFO: Iniciando script de monitoramento...")

previous_state = load_previous_state()

try:
    print(f"INFO: A buscar a lista de dispositivos em {DEVICE_LIST_URL}...")
    device_response = session.get(DEVICE_LIST_URL, timeout=10)
    device_response.raise_for_status()
    
    print("INFO: Dados dos dispositivos obtidos com SUCESSO.")

    devices_data = device_response.json().get('data', [])
    if not devices_data:
        print("ERRO: A API devolveu uma lista de dispositivos vazia.")
        sys.exit(1)

    gateway_device = None
    for dev in devices_data:
        if dev.get('type') in ('udm'):
            gateway_device = dev
            print(f"INFO: Dispositivo Gateway encontrado: {gateway_device.get('name')}")
            break
    
    if not gateway_device:
        print("ERRO: Nenhum dispositivo Gateway (UDM/USG) foi encontrado no site.")
        sys.exit(1)
    
    current_state = {}
    
    wan1_status = gateway_device.get('wan1', {}).get('up', False)
    current_state['wan1'] = wan1_status
    
    \
    send_slack_notification(
        "MUNDIVOX",
        wan1_status,
        previous_state.get('wan1')
    )
    
    if wan1_status:
        send_push(PUSH_URL_MUNDIVOX, "MUNDIVOX")
    
    wan2_status = gateway_device.get('wan2', {}).get('up', False)
    current_state['wan2'] = wan2_status
    
    send_slack_notification(
        "Link VIVO",
        wan2_status,
        previous_state.get('wan2')
    )
    
    if wan2_status:
        send_push(PUSH_URL_VIVO, "Link VIVO")
    
    save_current_state(current_state)
    print(f"INFO: Estado atual salvo: {current_state}")

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("--- ERRO 401: NÃO AUTORIZADO ---")
        print("ERRO: A API Key foi REJEITADA.")
    else:
        print(f"ERRO: Falha na requisição HTTP. Status: {e.response.status_code}. Resposta: {e.response.text}")
except requests.exceptions.ConnectionError as e:
    print(f"ERRO: Falha de conexão. Não foi possível ligar-se a {UNIFI_HOST}.")
except Exception as e:
    print(f"ERRO: Uma falha inesperada ocorreu: {e}")

print("INFO: Script finalizado.")
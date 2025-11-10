# 🛰️ UniFi Network Monitor — Slack + Uptime Kuma

Script em **Python** para monitoramento de links **WAN** em dispositivos **UniFi**, com:
- 🔔 Notificações automáticas no **Slack** com mensagens personalizadas  
- 💓 Integração direta com **Uptime Kuma** via *Push API*  
- 💾 Persistência de estado para evitar alertas duplicados  

Ideal para automatizar alertas de conectividade (ex: links de internet, WAN redundante, MPLS etc.)  
Executa de forma leve e segura a cada minuto, via **Agendador de Tarefas (Windows)** ou **cron (Linux)**.

---

## ⚙️ Estrutura do Projeto

📁 .
├── .env # Variáveis de ambiente (host, API, webhooks)
├── .env_example # Exemplo de configuração
├── .gitignore # Itens ignorados pelo Git
├── wan_status_state.json # Armazena o estado anterior dos links
└── webhook.py # Script principal

yaml
Copiar código

---

## 🚀 Funcionalidades

✅ Consulta o status atual das interfaces WAN via API UniFi  
✅ Envia *heartbeat* para o Uptime Kuma mantendo a página de status atualizada  
✅ Dispara mensagens no Slack apenas quando há mudança de estado  
✅ Exibe mensagens personalizadas e “humanizadas” (sem jargão técnico)  
✅ Loga resultados e mantém estado entre execuções  

---

## 🔧 Configuração

1. Copie o arquivo `.env_example` para `.env`:

   ```bash
   cp .env_example .env
Edite o .env e adicione suas variáveis:

ini
Copiar código
UNIFI_HOST=172.16.0.1
UNIFI_PORT=443
SITE_ID=default
VERIFY_SSL=False
API_KEY=SEU_API_KEY_UNIFI

PUSH_URL_WAN1=
PUSH_URL_WAN2=

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/SEU/WEBHOOK/AQUI
Instale as dependências:

bash
Copiar código
pip install requests urllib3 python-dotenv
🧠 Como Funciona
O script lê o status das interfaces WAN (wan1, wan2) via API UniFi

Compara o resultado com o último estado salvo em wan_status_state.json

Se houver mudança (ex: link caiu ou voltou):

Envia mensagem formatada para o Slack

Atualiza o Uptime Kuma via push URL

Salva o novo estado no JSON

💬 Exemplo de Notificações
🟥 Quando o link cai:

perl
Copiar código
🔴 Atenção: O link *VIVO* está com uma interrupção no momento.
A conexão pode apresentar instabilidade.
Nossa equipe de TI já foi notificada e está cuidando do problema.
🟩 Quando o link volta:

bash
Copiar código
🟢 Serviço Recuperado: O link *VIVO* está novamente operacional.
🕹️ Execução
Rodando manualmente
bash
Copiar código
python webhook.py
Rodando em background (sem console)
bash
Copiar código
pythonw webhook.py
Execução automática
Windows: Agende via Agendador de Tarefas a cada 1 minuto

Linux/macOS: Adicione ao crontab:

bash
Copiar código
* * * * * /usr/bin/python3 /caminho/para/webhook.py
🧩 Integração com Uptime Kuma
Cada link (Vivo / Mundivox, etc.) deve estar cadastrado no Kuma como monitor tipo “Push”.
O script enviará automaticamente os heartbeats, mantendo o status sincronizado.

Você pode estilizar sua página pública do Kuma com CSS customizado — veja o tema sugerido em /styles/kuma-dark.css.

🗂️ Exemplo de Log
yaml
Copiar código
INFO: Iniciando script de monitoramento...
INFO: Dispositivo Gateway encontrado: UDM-Pro
INFO: Notificação Slack enviada para MUNDIVOX
INFO: Heartbeat Uptime Kuma enviado para: MUNDIVOX
INFO: Estado atual salvo: {'wan1': True, 'wan2': True}


🧑‍💻 Autor
Bruno Tolentino
Infraestrutura e Automação de Monitoramento
📡 Projeto interno de monitoramento WAN — UniFi + Kuma + Slack


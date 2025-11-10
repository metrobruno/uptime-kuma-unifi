Monitoramento Stateful de WAN UniFi com Alertas para Slack

1. Visão Geral
Este projeto implementa um script de monitoramento robusto para gateways UniFi (ex: UDM Pro) que desacopla o histórico de uptime da lógica de alertas.

O Uptime Kuma é usado puramente como um dashboard histórico (através de monitores Push). A lógica de notificação é movida inteiramente para este script Python, que:

Consulta a API oficial do UniFi para obter o status real das portas WAN.

Mantém seu próprio "estado" (wan_status_state.json) para entender quando um link realmente muda (de UP para DOWN, ou vice-versa).

Envia alertas ricos e formatados (via JSON Block Kit) diretamente para o Slack apenas na mudança de estado, eliminando o "spam" de notificações repetitivas.

2. Recursos Principais
Monitoramento Direto via API: Utiliza uma API Key do UniFi para consultar endpoints de forma eficiente, sem dependências de bibliotecas de terceiros como pyunifi.

Notificações "Stateful": O script é ciente do estado anterior. Alertas de "queda" só são enviados na primeira deteção, e alertas de "recuperação" só são enviados na primeira deteção de normalização.

Alertas Ricos no Slack: Envia mensagens JSON attachments formatadas (Block Kit) para o Slack, com cores (vermelho/verde) e formatação profissional, em vez das mensagens de texto simples padrão.

Integração com Uptime Kuma: Envia um heartbeat (push) ao Uptime Kuma sempre que os links estão operacionais, permitindo um dashboard gráfico e um histórico de SLA.

3. Arquitetura do Fluxo de Dados
Este script atua como um "middleware" inteligente entre os seus sistemas.

+---------------------+
| Agendador de        |
| Tarefas (Windows)   |-- (Executa a cada 1 min) --> +---------------+
+---------------------+                                |               |
                                                     |  Script       |
+---------------------+                                |  Python       |
| API do UniFi        |<-- (Consulta status WAN) --- |               |
| (UDM Pro)           |                                +-------+-------+
+---------------------+                                        |
         |                                                     |
         v (Compara estado)                                    |
+---------------------+                                        | (Envia push se UP)
| wan_status_state.json| <--(Lê/Grava estado)                  |
| (Ficheiro de Estado)  |                                        v
+---------------------+                                +---------------+
                                                         | Uptime Kuma   |
                                                         +---------------+
                                                         |
                                                         | (Envia alerta
                                                         |  *se* o estado mudou)
                                                         v
                                                     +----------------+
                                                     | Slack Webhook  |
                                                     +----------------+
4. Configuração
4.1. Pré-requisitos
Python 3.9 ou superior.

A biblioteca requests: pip install requests

4.2. Geração de Chaves e URLs
UniFi Controller (UDM Pro):

Vá para Configurações > Sistema > Integrações (ou Admins & Users > API Keys em algumas versões).

Crie uma nova API Key (Chave de API) com permissões de Super Administrador.

Copie a chave.

Uptime Kuma:

Crie dois (2) monitores do tipo Push (ex: "Link MUNDIVOX (WAN1)" e "Link VIVO (WAN2)").

Desligue todas as notificações nativas do Uptime Kuma para estes monitores (o script irá geri-las).

Copie as URLs de Push de cada monitor.

Slack:

Vá para Configurações e Administração > Gerir Aplicações > Incoming Webhooks.

Crie um novo Webhook de Entrada (Incoming Webhook) para o canal desejado (ex: #alertas-rede).

Copie a Webhook URL.

4.3. Configuração do Script
Edite as variáveis no topo do ficheiro monitor_unifi.py com as chaves e URLs que acabou de gerar.

Python

# ============ CONFIGURAÇÕES UNIFI ============
UNIFI_HOST = "172.16.0.1"
UNIFI_PORT = "443"
SITE_ID = "default"         # Encontre o seu na URL do portal UniFi
VERIFY_SSL = False
API_KEY = "SUA_API_KEY_DO_UNIFI_AQUI"

# ============ CONFIGURAÇÕES UPTIME KUMA ============
PUSH_URL_VIVO = "URL_DE_PUSH_DO_KUMA_PARA_VIVO"
PUSH_URL_MUNDIVOX = "URL_DE_PUSH_DO_KUMA_PARA_MUNDIVOX"

# ============ CONFIGURAÇÕES SLACK ============
SLACK_WEBHOOK_URL = "SUA_WEBHOOK_URL_DO_SLACK_AQUI"
5. Implantação (Agendador de Tarefas do Windows)
Para garantir que o script é executado 24/7, configure uma tarefa no Agendador de Tarefas do Windows.

Abra o Agendador de Tarefas (taskschd.msc).

Crie uma nova Tarefa (não "Tarefa Básica").

Separador: Geral

Nome: Monitor WAN UniFi

Marque "Executar estando o usuário conectado ou não".

Marque "Executar com privilégios mais altos".

Separador: Disparadores

Novo: Iniciar "Num agendamento", "Diariamente".

Em Definições Avançadas, marque "Repetir tarefa a cada" "1 minuto".

Duração: "Indefinidamente".

Verifique se está "Activado".

Separador: Ações

Novo: Ação "Iniciar um programa".

Programa/script: (Caminho completo para o seu Python. Use aspas se houver espaços).

"C:\Users\Bruno Tolentino\AppData\Local\Programs\Python\Python313\python.exe"

Adicione argumentos (opcional): (Caminho completo para o script. Use aspas).

"C:\Users\Bruno Tolentino\Documents\uptime-unifi-market4u\monitor_unifi.py"

Iniciar em (opcional): (Caminho completo para a pasta do script. Use aspas).

"C:\Users\Bruno Tolentino\Documents\uptime-unifi-market4u"

Separador: Condições

Desmarque "Iniciar a tarefa apenas se o computador estiver ligado à corrente alternada".

Separador: Definições

Verifique se "Se a tarefa já estiver em execução..." está definido como "Não iniciar uma nova instância".

Clique em OK para salvar. A tarefa será executada automaticamente a cada minuto.

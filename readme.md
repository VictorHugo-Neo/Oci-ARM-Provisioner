# OCI ARM Instance Provisioner 

Um script em Python projetado para automatizar o provisionamento de instâncias ARM (VM.Standard.A1.Flex) no nível gratuito (*Always Free*) da Oracle Cloud Infrastructure (OCI). 

Devido à alta concorrência por recursos gratuitos, tentar criar essas instâncias manualmente pelo painel web frequentemente resulta no erro **"Out of capacity"**. Este bot resolve o problema rodando em segundo plano, fazendo requisições dinâmicas à API da Oracle e utilizando *Jitter* (intervalos aleatórios) para evitar bloqueios de rede (*Rate Limits*), até conseguir capturar uma vaga na nuvem.

Excelente para garantir um servidor robusto (4 OCPUs e 24GB de RAM) para hospedar aplicações em FastAPI, bancos de dados PostgreSQL e containers Docker.

## Funcionalidades

* **Busca Dinâmica:** Localiza automaticamente o prefixo correto do *Availability Domain* e o OCID da imagem mais recente do Ubuntu ARM, evitando erros `400 (CannotParseRequest)` e `404 (NotFound)`.
* **Tratamento de Exceções:** Lida com quedas de conexão forçadas pelo firewall da Oracle.
* **Jitter Integrado:** Tempos de espera randomizados entre as tentativas para disfarçar o comportamento do bot.
* **Segurança Padrão da Indústria:** Utiliza arquivos `.env` para que seus OCIDs não fiquem expostos no código.

## Pré-requisitos

1. **Conta na Oracle Cloud:** Com uma rede virtual (VCN) e uma **Sub-rede Pública** já criadas.
2. **OCI CLI Configurada:** Você precisa ter a chave de API da Oracle configurada na sua máquina local (geralmente em `~/.oci/config`).
3. **Python 3.11+** instalado no seu sistema.
O_REPOSITORIO.git)
   cd NOME_DO_REPOSITORIO
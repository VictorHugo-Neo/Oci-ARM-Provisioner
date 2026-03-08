#!/run/media/victorhugo-neo/LinWind/arqlinux/pj/portifolio/Oracle/oci_env/bin/python3

import oci
import os
import logging
from dotenv import load_dotenv

load_dotenv()

LOG_FILE = "oci_erro_404.log"
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE) 

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

print(f"Iniciando diagnóstico profundo. Gravando dados em: {LOG_FILE}")


I_ID = os.getenv("I_ID_IMAGE")
C_ID = os.getenv("OCI_COMPARTMENT_ID")
S_ID = os.getenv("OCI_SUBNET_ID")
PUB_KEY_PATH = os.path.expanduser(os.getenv("OCI_SSH_KEY_PATH", "~/.ssh/id_rsa.pub"))

try:
    with open(PUB_KEY_PATH, 'r') as f:
        ssh_key = f.read().strip()
except FileNotFoundError:
    print(f"ERRO: Chave SSH não encontrada em {PUB_KEY_PATH}")
    exit(1)

config = oci.config.from_file()


identity_client = oci.identity.IdentityClient(config)
try:
    ads = identity_client.list_availability_domains(compartment_id=C_ID).data
    AD_NAME = ads[0].name
    logging.info(f"Availability Domain encontrado: {AD_NAME}")
except Exception as e:
    logging.error(f"Falha ao buscar AD: {e}")
    exit(1)

compute_client = oci.core.ComputeClient(config)


vnic = oci.core.models.CreateVnicDetails(subnet_id=S_ID, assign_public_ip=True)
shape_cfg = oci.core.models.LaunchInstanceShapeConfigDetails(ocpus=4.0, memory_in_gbs=24.0)
source = oci.core.models.InstanceSourceViaImageDetails(image_id=I_ID)

launch_details = oci.core.models.LaunchInstanceDetails(
    compartment_id=C_ID,
    availability_domain=AD_NAME,
    shape="VM.Standard.A1.Flex",
    shape_config=shape_cfg,
    source_details=source,
    create_vnic_details=vnic,
    metadata={"ssh_authorized_keys": ssh_key}
)


print("Enviando requisição (isso pode levar alguns segundos)...")
try:
    compute_client.launch_instance(launch_details)
    print("\nSUCESSO! A instância foi criada e não houve erro 404.")
except oci.exceptions.ServiceError as e:
    print("\n[!] O Erro ocorreu. Os detalhes foram salvos no log.")
    logging.error("=== RESUMO DO ERRO DA API ===")
    logging.error(f"Status: {e.status}")
    logging.error(f"Code: {e.code}")
    logging.error(f"Message: {e.message}")
    logging.error(f"Request ID: {e.request_id}")
    logging.error("=============================")


#!/run/media/victorhugo-neo/LinWind/arqlinux/pj/portifolio/Oracle/oci_env/bin/python3

import oci
import os
import logging
import http.client as http_client
from dotenv import load_dotenv

load_dotenv()

http_client.HTTPConnection.debuglevel = 1
logging.basicConfig(level=logging.DEBUG)
oci_logger = logging.getLogger('oci')
oci_logger.setLevel(logging.DEBUG)


I_ID = os.getenv("I_ID_IMAGE")
C_ID = os.getenv("OCI_COMPARTMENT_ID")
S_ID = os.getenv("OCI_SUBNET_ID")
PUB_KEY_PATH = os.path.expanduser(os.getenv("OCI_SSH_KEY_PATH", "~/.ssh/id_rsa.pub"))


config = oci.config.from_file()
compute_client = oci.core.ComputeClient(config)

print("Iniciando requisição de diagnóstico...")

try:
    with open(PUB_KEY_PATH, 'r') as f:
        ssh_key = f.read().strip()
except FileNotFoundError:
    print("ERRO: Chave SSH não encontrada.")
    exit(1)


vnic = oci.core.models.CreateVnicDetails(
    subnet_id=S_ID,
    assign_public_ip=True
)

shape_cfg = oci.core.models.LaunchInstanceShapeConfigDetails(
    ocpus=4.0, 
    memory_in_gbs=24.0
)

source = oci.core.models.InstanceSourceViaImageDetails(
    image_id=I_ID,
    source_type="image" 
)

launch_details = oci.core.models.LaunchInstanceDetails(
    compartment_id=C_ID,
    availability_domain="sa-saopaulo-1-AD-1",
    shape="VM.Standard.A1.Flex",
    shape_config=shape_cfg,
    source_details=source,
    create_vnic_details=vnic,
    metadata={"ssh_authorized_keys": ssh_key}
)

try:
    print("Enviando payload para a Oracle...")
    compute_client.launch_instance(launch_details)
    print("\nSUCESSO! O erro 400 sumiu e a máquina foi criada.")
except oci.exceptions.ServiceError as e:
    print("\n" + "="*50)
    print("RESULTADO DO DIAGNÓSTICO:")
    print("="*50)
    print(f"Status HTTP: {e.status}")
    print(f"Código do Erro: {e.code}")
    print(f"Mensagem da Oracle: {e.message}")
    print("="*50)
    print("Se o erro for 500 (Out of capacity), o script original pode ser usado!")
    print("Se continuar 400, copie o log acima desta caixa para analisarmos o JSON.")

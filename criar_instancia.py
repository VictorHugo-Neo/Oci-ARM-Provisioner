#!/run/media/victorhugo-neo/LinWind/arqlinux/pj/portifolio/Oracle/oci_env/bin/python3

import oci
import os
import time
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

C_ID = os.getenv("OCI_COMPARTMENT_ID")
S_ID = os.getenv("OCI_SUBNET_ID")
PUB_KEY_PATH = os.path.expanduser(os.getenv("OCI_SSH_KEY_PATH", "~/.ssh/id_rsa.pub"))

if not C_ID or not S_ID:
    print("ERRO: Variáveis de ambiente OCI_COMPARTMENT_ID e OCI_SUBNET_ID não configuradas no .env")
    exit(1)

config = oci.config.from_file()
identity_client = oci.identity.IdentityClient(config)
compute_client = oci.core.ComputeClient(config)

print("=== COLETANDO DADOS DINÂMICOS ===")


try:
    ads = identity_client.list_availability_domains(compartment_id=C_ID).data
    AD_NAME = ads[0].name
    print(f"[*] AD: {AD_NAME}")
except Exception as e:
    print(f"Erro ao buscar AD: {e}")
    exit(1)


try:
    images = compute_client.list_images(
        compartment_id=C_ID,
        operating_system="Canonical Ubuntu",
        operating_system_version="20.04",
        shape="VM.Standard.A1.Flex",
        sort_by="TIMECREATED",
        sort_order="DESC"
    ).data
    
    if not images:
        print("Erro: Nenhuma imagem compatível encontrada para esta região.")
        exit(1)
        
    I_ID = images[0].id
    print(f"[*] Imagem: {I_ID}")
except Exception as e:
    print(f"Erro ao buscar Imagem: {e}")
    exit(1)

print("=================================\n")


def try_launch():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Tentando alocar recursos ARM...")
    
    try:
        with open(PUB_KEY_PATH, 'r') as f:
            ssh_key = f.read().strip()
    except FileNotFoundError:
        print(f"ERRO: Chave SSH não encontrada em {PUB_KEY_PATH}")
        return True

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
        availability_domain=AD_NAME,
        shape="VM.Standard.A1.Flex",
        shape_config=shape_cfg,
        source_details=source,
        create_vnic_details=vnic,
        metadata={"ssh_authorized_keys": ssh_key}
    )

    try:
        compute_client.launch_instance(launch_details)
        print("\nSUCESSO ABSOLUTO! Sua instância foi criada.")
        return True
        
    except oci.exceptions.ServiceError as e:
        if e.status == 500 or "capacity" in str(e).lower():
            print("STATUS: Sem capacidade em SP. Aguardando a fila...")
            return False
        else:
            print(f"ERRO DE API ({e.status}): {e.message}")
            return False
            
    
    except oci.exceptions.RequestException as e:
        print("ALERTA DE REDE: A conexão foi cortada pela Oracle (Possível Rate Limit).")
        return False
        
    except Exception as e:
        print(f"ERRO INESPERADO: {e}")
        return False


while not try_launch():
    
    tempo_espera = random.randint(40, 90)
    print(f"Disfarçando o script: esperando {tempo_espera} segundos antes da próxima tentativa...\n")
    time.sleep(tempo_espera)
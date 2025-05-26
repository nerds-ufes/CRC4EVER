#!/usr/bin/python

import os
import sys
from scapy.all import *

# Verifica se o script está sendo executado como root
if os.getuid() != 0:
    print("""
ERROR: This script requires root privileges.
       Use 'sudo' to run it.
""")
    quit()

# Coleta os argumentos da linha de comando
try:
    ip_dst = sys.argv[1]  # Endereço IP de destino
    inter = sys.argv[2]   # Interface de rede
    ttl_val = sys.argv[3] # Valor do TTL
    tos_val = sys.argv[4] # Valor do ToS
except:
    ip_dst = "10.0.0.20"
    inter = "enp2s0f0.1920"
    ttl_val = 1
    tos_val = 23

# Determina o caminho baseado no ToS
if int(tos_val) == 21:
    path = "path1"
elif int(tos_val) == 22:
    path = "path2"
else:
    path = "path3"

# Exibir os valores configurados
print(f"Enviando pacote para {ip_dst}")
print(f"Interface: {inter}")
print(f"ToS: {tos_val} ({path})")

# Construção do pacote
p = (Ether() /
     IP(ttl=int(ttl_val), dst=ip_dst, tos=int(tos_val)) /
     UDP(sport=7, dport=7) /
     "This is a test")

# Enviar o pacote pela interface especificada
sendp(p, iface=inter)

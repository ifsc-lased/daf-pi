from daf_virtual_rasp.com.enquadramento import Enquadramento
from daf_virtual_rasp.com.arq import Arq
from daf_virtual_rasp.com.poller import Poller
from daf_virtual_rasp.com.enq_enum import TIPO_t
from daf_virtual_rasp.daf.daf import DAF
import sys, time, os
import serial
import argparse


# Definindo argumentos de linha de comando
parser = argparse.ArgumentParser(description='DAF-pi')
parser.add_argument('-p', '--port', type=str, default='/dev/ttyGS0', help='Porta serial de comunicação (default: /dev/ttyGS0)')
parser.add_argument('-P', '--port_socat', type=int, help='Porta serial de comunicação usando socat (sobrescreve o argumento -p)')
parser.add_argument('-t', '--timeout_arq', type=float, default=2, help='Tempo de timeout da camada de arq (default: 2 segundos)')
args = parser.parse_args()

# Recebendo argumentos de linha de comando
port = f'/dev/pts/{args.port_socat}' if args.port_socat else args.port
timeout_arq = args.timeout_arq

# define parametros das camadas ARQ e Enquadramento
max_tentativas_arq = 3
timeout_enq = 0.5

# obtém porta serial 
ser = serial.Serial(
            port=port,
            baudrate = 115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout= None
        )

ser.flush()


# cria os objetos das camadas ARQ, Enquadramento e DAF
e = Enquadramento(ser, timeout_enq)
a = Arq(max_tentativas_arq, timeout_arq)
daf = DAF()

# define organização das subcamadas
daf.set_inferior(a)
a.set_superior(daf)
a.set_inferior(e)
e.set_superior(a)

# despacha as camadas
pol = Poller()
pol.adiciona(daf)
pol.adiciona(e)
pol.adiciona(a)
pol.despache()
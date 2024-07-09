from daf_virtual_rasp.imagem import ImagemSB
from daf_virtual_rasp.utils.cripto_daf import ChaveCripto, CriptoDAF

import sys
import secrets
import argparse
import logging

def gera_imagem_atual():

    nome_arquivo = 'imagem_atual.bin'
    path_atual = 'daf_virtual_rasp/resources/imagem/sb'

    logging.debug(f"Carregando informações da imagem atual armazenada em {path_atual}")

    imagem_atual = ImagemSB(path_arquivos=path_atual)

    versao_sb = imagem_atual.get_versao_SB()
    max_dfe_sef = imagem_atual.get_maxdfe()
    sb = imagem_atual.get_codigo()

    tam_sig_fab = imagem_atual.get_tam_assinatura_ateste()
    sig_fab = imagem_atual.get_assinatura_ateste()
    tam_sig_sef = imagem_atual.get_tam_assinatura_sef()
    sig_sef = imagem_atual.get_assinatura()

    firmware = versao_sb + max_dfe_sef + sb
    imagem_bin = firmware + tam_sig_fab + sig_fab + tam_sig_sef + sig_sef

    logging.debug(f"Salvando binário da imagem em {nome_arquivo}")
    with open(nome_arquivo, "wb") as arquivo:
        arquivo.write(imagem_bin)
        
    return imagem_atual

def gera_imagem_nova(vsb, mxd_sef, priv_key, sef_key):

    nome_arquivo = 'imagem_nova.bin'
    path_nova = 'daf_virtual_rasp/resources/imagem-nova/sb'
    logging.debug("Gerando imagem com informações passadas como argumento")
   
    versao_sb = vsb.to_bytes(2, byteorder='big')
    max_dfe_sef = mxd_sef.to_bytes(2, byteorder='big')
    sb = secrets.token_bytes(2048)
    firmware = versao_sb + max_dfe_sef + sb

    hash_firmware = CriptoDAF.gera_resumo_SHA256(firmware)
    sig_fab = CriptoDAF.gera_assinatura_EC_p384(hash_firmware, priv_key)
    tam_sig_fab = len(sig_fab)

    hash_sig_fab= CriptoDAF.gera_resumo_SHA256(sig_fab)
    sig_sef = CriptoDAF.gera_assinatura_EC_p384(hash_sig_fab, sef_key)
    tam_sig_sef = len(sig_sef)

    imagem_bin = firmware + tam_sig_fab.to_bytes(2, byteorder='big') + sig_fab + tam_sig_sef.to_bytes(2, byteorder='big') + sig_sef
    if(args.debug):
        logging.debug(f"Tamanho assinatura ateste = {tam_sig_fab}")
        logging.debug(f"Tamanho assinatura sef = {tam_sig_sef} \n")
    
    imagem_nova = ImagemSB(raw_binario=imagem_bin, path_arquivos=path_nova)

    logging.debug(f"Salvando binário da imagem em {nome_arquivo}")
    with open(nome_arquivo, "wb") as arquivo:
        arquivo.write(imagem_bin)

    return imagem_nova


parser = argparse.ArgumentParser(description='Gerar arquivo binario com "imagem" do firmware do DAF-pi. Caso não seja passado nenhum argumento, gera imagem com firmware atual instalado no daf-pi.')

parser.add_argument('-n', '--novo',action="store_true",
                    help='Gerar imagem com firmware contendo informações passadas como argumento')

parser.add_argument('-d', '--debug', action="store_true",
                    help='Imprimir informações da geração de imagem')

parser.add_argument('-v', '--vsb', required='-n' in sys.argv, type=int,
                    help='Versão do SB')

parser.add_argument('-m','--mxd_sef', required='-n' in sys.argv, type=int,
                    help='Valor do Max Dfe SEF')

parser.add_argument('-a','--ateste_priv', required='-n' in sys.argv, type=str,
                    help='Chave de ateste (PEM) para assinatura do fabricante sobre o firmware')

parser.add_argument('-s','--sef_priv', required='-n' in sys.argv, type=str,
                    help='Chave privada SEF (PEM) para assinatura SEF do firmware')

args = parser.parse_args()

imagem = None
if(args.novo):
    ateste_priv_file = args.ateste_priv
    sef_priv_file = args.sef_priv
    versao_sb = args.vsb
    max_dfe_sef = args.mxd_sef

    with open(ateste_priv_file) as file:
        ateste_priv = ChaveCripto(file.read())

    with open(sef_priv_file) as file:
        sef_priv = ChaveCripto(file.read())

    imagem = gera_imagem_nova(versao_sb, max_dfe_sef, ateste_priv, sef_priv)    

else:
    
    imagem = gera_imagem_atual()

if(args.debug):
    logging.debug("------------------------------")
    logging.debug("Informações da Imagem")
    logging.debug("------------------------------")
    logging.debug(f"vsb = {int.from_bytes(imagem.get_versao_SB(),byteorder='big')}")
    logging.debug(f"mxd = {int.from_bytes(imagem.get_maxdfe(),byteorder='big')}")
    


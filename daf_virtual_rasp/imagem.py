import typing
import os
import logging

from daf_virtual_rasp.utils.cripto_daf import ChaveCripto, CriptoDAF
from daf_virtual_rasp.daf.daf_enums import Artefatos
from daf_virtual_rasp.utils.base64URL_daf import Base64URLDAF

### ATENÇÃO ###

# Este código serve somente para ilustrar uma maneira de validar o binário contendo a imagem recebida
# Cada fabricante é resposável por montar e validar a imagem de acordo com a especificação do DAF vigente.


#### Composição da imagem para o daf-pi ####

# Firmware = VSB + MXD_SEF + SB (codigo)
# Imagem = Firmware + tamanho_assinatura_ateste + assinatura_ateste + tamanho_assinatura_sef + assinatura (SEF)
class ImagemSB: 

    # todos tamanhos em bytes
    VERSAO_TAMANHO = 2
    MAXDFE_TAMANHO = 2
    CODIGO_TAMANHO = 2048
    FIRMWARE_TAMANHO = VERSAO_TAMANHO + MAXDFE_TAMANHO + CODIGO_TAMANHO
    # qtd de bytes que indicam o tamanho das assinaturas
    TAMANHO_ASSINATURA_ATESTE = 2
    TAMANHO_ASSINATURA = 2
     

    def __init__(self, raw_binario: bytes = b'', path_arquivos: str = './daf_virtual_rasp/resources/imagem/sb'):
        """Inicialização da imagem do SB.

        Args:
            raw_binario (bytes, optional): Preencher com a imagem caso deseja-se inserir uma nova imagem na partição do SB. Defaults to b''.
            path_arquivos (str, optional): Local da partição, isto é, onde a imagem será salva. Defaults to './daf_virtual_rasp/resources/imagem/sb'.

        Raises:
            ValueError: Se a partição do SB estiver vazia e o parâmetro raw_binario não for especificado. Teoricamente, essa partição não deve estar vazia em nenhuma situação, pois o SB é inserido em tempo de manufatura e depois disso essa partição ou é apenas atualizada/sobreescrita.
        """

        self.path_arquivos = path_arquivos

        # cria pasta se nao existe ainda
        if not os.path.isdir(self.path_arquivos):
            os.makedirs(self.path_arquivos)

        if len(raw_binario) == 0:
            # então a imagem já foi adicionada anteriormente
            
            if self.particao_vazia() == True:
                raise ValueError(
                    "Partição está vazia e parâmetro raw_binario está vázio.")

        else:
            # imagem sendo adicionada agora

            versao = self._extrai_versao(raw_binario)
            logging.debug(f"Versão recebida: {int.from_bytes(versao,byteorder='big')}")
            maxdfe = self._extrai_maxdfe(raw_binario)
            codigo = self._extrai_codigo(raw_binario) # SB
            firmware = versao + maxdfe + codigo

            tamanho_assinatura_ateste = self._extrai_tam_assinatura_ateste(raw_binario)
            self._tam_assinatura_ateste = int.from_bytes(tamanho_assinatura_ateste, byteorder='big')
            assinatura_ateste = self._extrai_assinatura_ateste(raw_binario)
            
            tamanho_assinatura_sef = self._extrai_tam_assinatura_sef(raw_binario) 
            self._tam_assinatura_sef = int.from_bytes(tamanho_assinatura_sef, byteorder='big')
            assinatura = self._extrai_assinatura(raw_binario)
                       
            self._set_versao(versao)
            self._set_maxdfe(maxdfe)
            self._set_codigo(codigo)
            self._set_firmware(firmware)
            self._set_tam_assinatura_ateste(tamanho_assinatura_ateste)
            self._set_assinatura_ateste(assinatura_ateste)
            self._set_tam_assinatura_sef(tamanho_assinatura_sef)
            self._set_assinatura(assinatura)
            

    # extração de campos da imagem cru

    def _extrai_versao(self, raw_binario: bytes) -> bytes:
        offset = 0
        return raw_binario[offset: offset + self.VERSAO_TAMANHO]

    def _extrai_maxdfe(self, raw_binario: bytes) -> bytes:
        offset = self.VERSAO_TAMANHO
        return raw_binario[offset: offset + self.MAXDFE_TAMANHO]
    
    def _extrai_codigo(self, raw_binario: bytes) -> bytes:
        offset = self.VERSAO_TAMANHO + self.MAXDFE_TAMANHO 
        return raw_binario[offset: offset + self.CODIGO_TAMANHO]
    
    def _extrai_tam_assinatura_ateste(self, raw_binario: bytes) -> bytes:
        offset = self.FIRMWARE_TAMANHO
        return raw_binario[offset: offset + self.TAMANHO_ASSINATURA_ATESTE]

    def _extrai_assinatura_ateste(self, raw_binario: bytes) -> bytes:
        offset = self.FIRMWARE_TAMANHO + self.TAMANHO_ASSINATURA_ATESTE
        return raw_binario[offset: offset + self._tam_assinatura_ateste]
    
    def _extrai_tam_assinatura_sef(self, raw_binario: bytes) -> bytes:
        offset = self.FIRMWARE_TAMANHO + self.TAMANHO_ASSINATURA_ATESTE + self._tam_assinatura_ateste
        return raw_binario[offset: offset + self.TAMANHO_ASSINATURA]
    
    def _extrai_assinatura(self, raw_binario: bytes) -> bytes:
        offset = self.FIRMWARE_TAMANHO + self.TAMANHO_ASSINATURA_ATESTE + self._tam_assinatura_ateste + self.TAMANHO_ASSINATURA
        return raw_binario[offset: offset + self._tam_assinatura_sef]

    # get/set versao

    def _arquivo_versao(self) -> str:
        return f"{self.path_arquivos}/versao.str"

    def _set_versao(self, versao: bytes) -> None:
        with open(self._arquivo_versao(), "wb") as arquivo:
            arquivo.write(versao)

    def get_versao_SB(self) -> bytes:
        with open(self._arquivo_versao(), "rb") as arquivo:
            versao = arquivo.read()
        return versao

    # get/set maxfde

    def _arquivo_maxdfe(self) -> str:
        return f"{self.path_arquivos}/maxdfe.str"

    def _set_maxdfe(self, maxdfe: bytes) -> None:
        with open(self._arquivo_maxdfe(), "wb") as arquivo:
            arquivo.write(maxdfe)

    def get_maxdfe(self) -> bytes:
        with open(self._arquivo_maxdfe(), "rb") as arquivo:
            maxdfe = arquivo.read()
        return maxdfe  

     # get/set codigo

    def _arquivo_codigo(self) -> str:
        return f"{self.path_arquivos}/codigo.bin"

    def _set_codigo(self, codigo: bytes) -> None:
        with open(self._arquivo_codigo(), "wb") as arquivo:
            arquivo.write(codigo)

    def get_codigo(self) -> bytes:
        
        with open(self._arquivo_codigo(), "rb") as arquivo:
            codigo = arquivo.read()
        
        return codigo      

    # get/set firmware

    def _arquivo_firmware(self) -> str:
        return f"{self.path_arquivos}/firmware.bin"

    def _set_firmware(self, firmware: bytes) -> None:
        with open(self._arquivo_firmware(), "wb") as arquivo:
            arquivo.write(firmware)

    def get_firmware(self) -> bytes:
        with open(self._arquivo_firmware(), "rb") as arquivo:
            firmware = arquivo.read()
        return firmware

    # get/set tam_assinatura_ateste

    def _arquivo_tam_assinatura_ateste(self) -> str:
        return f"{self.path_arquivos}/tam_assinatura_ateste.str"

    def _set_tam_assinatura_ateste(self, tam_assinatura_ateste: bytes) -> None:
        with open(self._arquivo_tam_assinatura_ateste(), "wb") as arquivo:
            arquivo.write(tam_assinatura_ateste)

    def get_tam_assinatura_ateste(self) -> bytes:
        with open(self._arquivo_tam_assinatura_ateste(), "rb") as arquivo:
            tam_assinatura_ateste = arquivo.read()
        return tam_assinatura_ateste

    # get/set assinatura_ateste

    def _arquivo_assinatura_ateste(self)-> str:
        return f"{self.path_arquivos}/assinatura_ateste.bin"

    def _set_assinatura_ateste(self, assinatura_ateste: bytes)-> None:
        with open(self._arquivo_assinatura_ateste(), "wb") as arquivo:
            arquivo.write(assinatura_ateste)
    
    def get_assinatura_ateste(self)->bytes:
        with open(self._arquivo_assinatura_ateste(), "rb") as arquivo:
            assinatura_ateste = arquivo.read()
        return assinatura_ateste
    
    # get/set tam_assinatura_sef

    def _arquivo_tam_assinatura_sef(self) -> str:
        return f"{self.path_arquivos}/tam_assinatura_sef.str"

    def _set_tam_assinatura_sef(self, tam_assinatura_sef: bytes) -> None:
        with open(self._arquivo_tam_assinatura_sef(), "wb") as arquivo:
            arquivo.write(tam_assinatura_sef)

    def get_tam_assinatura_sef(self) -> bytes:
        with open(self._arquivo_tam_assinatura_sef(), "rb") as arquivo:
            tam_assinatura_sef = arquivo.read()
        return tam_assinatura_sef

    # get/set assinatura

    def _arquivo_assinatura(self) -> str:
        return f"{self.path_arquivos}/assinatura.bin"

    def _set_assinatura(self, assinatura: bytes) -> None:
        with open(self._arquivo_assinatura(), "wb") as arquivo:
            arquivo.write(assinatura)

    def get_assinatura(self) -> bytes:
        with open(self._arquivo_assinatura(), "rb") as arquivo:
            assinatura = arquivo.read()
        return assinatura

    # particao

    def remove_particao(self) -> None:
        os.remove(self._arquivo_codigo())

    def particao_vazia(self) -> bool:
        particaoExiste = os.path.isfile(self._arquivo_codigo())
        return not particaoExiste

    # verificacoes

    def esta_integro(self) -> bool:
        res = (self.get_versao_SB() +self.get_maxdfe() +self.get_codigo()) == self.get_firmware()
        return res

    def esta_autentico(self, certificado) -> bool:
        msg = self.get_assinatura_ateste()
        hashed = CriptoDAF.gera_resumo_SHA256(msg)
        return CriptoDAF.verifica_assinatura_EC_P384(hashed, self.get_assinatura(), certificado.chave_publica)

    def esta_autentico_ateste(self, chave) ->bool:       
        msg = self.get_firmware()
        hashed = CriptoDAF.gera_resumo_SHA256(msg)
        return CriptoDAF.verifica_assinatura_EC_P384(hashed, self.get_assinatura_ateste(), chave)

    # ---
    # Este processo de atualização serve somente para ilustrar uma maneira de validar o binário recebido.

    def atualizar(self, novaImagem: 'ImagemSB', certificado, ateste) -> int:
      
        if not novaImagem.esta_integro() or not novaImagem.esta_autentico(certificado):
            return 3

        if not novaImagem.esta_autentico_ateste(ateste):
            return 9
     
        elif novaImagem.get_versao_SB() <= self.get_versao_SB():
            return 8


        self._set_versao(novaImagem.get_versao_SB())
        self._set_maxdfe(novaImagem.get_maxdfe())
        self._set_codigo(novaImagem.get_codigo())
        self._set_firmware(novaImagem.get_firmware())
        self._set_tam_assinatura_ateste(novaImagem.get_tam_assinatura_ateste())
        self._set_assinatura_ateste(novaImagem.get_assinatura_ateste())
        self._set_tam_assinatura_sef(novaImagem.get_tam_assinatura_sef())
        self._set_assinatura(novaImagem.get_assinatura())

        return 0


class ImagemSBCandidato(ImagemSB):

    def __init__(self, raw_binario: bytes = b'', pathArquivos: str = './daf_virtual_rasp/resources/outra-imagem/sb'):

        super().__init__(raw_binario, pathArquivos)

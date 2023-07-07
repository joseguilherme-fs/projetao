import getpass
import socket
import os 
import ast
import sys

class GNSClient:
  def __init__(self,host,porta):
    self._host = host
    self._porta = porta
    self.socket = None
    self.nome = None
    self.cpf = None

  def INICIAR(self):
    """
    Estabelece a conexão com o servidor de venda de ingressos.
    """
    print('Servidor:', self._host + ':' + str(self._porta))
    serv = (self._host, self._porta)
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.connect(serv)
    self.ENTRAR()

  
  def ENTRAR(self):
    """
    Função inicial do programa depois da conexão.
    """
    
    while True:
      print('\nDigite seu CPF ou SAIR para encerrar o programa:\n ')
      cpf = input('GNS> ').upper()
      self.socket.send(str.encode(cpf))
      conf = self.socket.recv(1024).decode('utf-8').split(':')
      
      if conf[0] == '+OK':
        self.cpf = cpf
        self.nome = input('\nNome: ')
        senha = getpass.getpass('Senha: ')
        limparTerminal()
        self.MENU()
        break
      elif conf[0] == '-ERROR':
        print('\nCPF inválido.')
        print('\nVerifique se você digitou seu CPF ou o comando SAIR corretamente.')
      elif conf[0] == 'SAIR':
        print(f'{conf[1]}!')
        break

  def MENU(self):
    """
    Exibe o menu principal para o cliente, onde ele pode escolher entre opções como comprar ingressos
    """
    print(f'\nBem-vindo(a) {self.nome}!\n')
    
    comandos = ['COMPRAR', 'INGRESSOS', 'REEMBOLSAR']
    
    while True:
      comando = input('\nDigite uma das opções abaixo:\n( comprar ) Comprar ingressos\n( ingressos ) Meus ingressos\n( reembolsar ) Reembolsar ingresso\n( sair ) Encerrar o programa\n\nGNS> ').upper()
      
      if comando in comandos:
        self.socket.send(str.encode(comando))
        funcao = getattr(self, comando)
        if not funcao():
          continue
      elif comando == 'SAIR':
        break
      else:
        print('Comando indefinido:', comando)
    
    self.socket.shutdown(socket.SHUT_RDWR)
    self.socket.close()
    print('ADEUS!')
        

  def COMPRAR(self):
    """
    Recebe do servidor sobre as disponibilidades dos ingressos, solicita ao usuário a quantidade desejada para cada tipo de ingresso, envia essas informações para o servidor e recebe a confirmação da compra.
    """
    quantidade = self.socket.recv(1024).decode('utf-8').split(':')
    vip = int((quantidade[0]))
    camarote = int((quantidade[1]))
    pista = int((quantidade[2]))
    
    if camarote == 0 and pista == 0 and vip == 0:
      print('\nDesculpe, não há ingressos disponíveis no momento')
    else:
      limparTerminal()
      print(f'\nIngressos disponíveis\nVIP: {vip} - R$100,00\nCAMAROTE: {camarote} - R$60,00\nPISTA: {pista} - R$30,00\n\n*Caso não queira comprar ingressos de alguma categoria, digite 0 (zero) no campo correspondente.\n')

  
      qntVIP = int(input('\nIngressos VIP: '))
      self.socket.send(str.encode(str(f'OK+:{qntVIP}')))
      resposta = self.socket.recv(1024).decode('utf-8').split(':')
      if resposta[1] == 'NONEVIP':
        print('\nNão há ingressos VIP suficientes no momento.')
        self.MENU()
        return False


      qntCAM = int(input('\nIngressos CAMAROTE: '))
      self.socket.send(str.encode(str(f'OK+:{qntCAM}')))
      resposta = self.socket.recv(1024).decode('utf-8').split(':')
      if resposta[1] == 'NONECAM':
        print('\nNão há ingressos CAMAROTE suficientes no momento.')
        self.MENU()
        return False
      

      qntPST = int(input('\nIngressos PISTA: '))
      self.socket.send(str.encode(str(f'OK+:{qntPST}')))
      resposta = self.socket.recv(1024).decode('utf-8').split(':')
      if resposta[1] == 'NONEPST':
        print('\nNão há ingressos PISTA suficientes no momento.')
        self.MENU()
        return False

        
      valorFinal = (qntVIP*100) + (qntCAM*60) + (qntPST*30)
      
      while True:
            comando = input(f'\nValor final: R${valorFinal},00\n\nDeseja confirmar a compra? Digite S  ou N.\n> ').upper()
            if comando == 'S':
                self.socket.send(str.encode(f'OK+:SIM:{qntVIP}:{qntCAM}:{qntPST}'))
                break
            elif comando == 'N':
                self.socket.send(str.encode(f'ERROR-:NAO:{qntVIP}:{qntCAM}:{qntPST}'))
                break
            else:
                print('Opção inválida.')

      confirmados = self.socket.recv(1024).decode('utf-8').split(':')
      if confirmados[0] == '+OK':
        limparTerminal()
        print(f'+OK Você comprou {confirmados[1]} ingressos. VIP: {confirmados[2]}, CAMAROTE: {confirmados[3]}, PISTA: {confirmados[4]}.\nBom show!\n')
      elif confirmados[1] == 'CANCELADO':
        print(confirmados[0],confirmados[1])
        print('Compra cancelada.\n')
      elif confirmados[1] == 'TIME':
        print('Tente novamente.')
      else:
        print('Não foi possível efetuar a compra. Há erros nas suas seleções.')

        
  def INGRESSOS(self):
    """
    Responsável por exibir os ingressos adquiridos pelo cliente. Ele recebe as informações dos ingressos do servidor e exibe uma representação visual dos ingressos na saída do terminal.
    """
    limparTerminal()
    ingressos = self.socket.recv(1024).decode('utf-8')
  
    if '-ERROR' in ingressos:
      print('-ERROR Você ainda não comprou ingressos.')
    else:
      ing1 = ingressos.replace('+OK[','')
      ing2 = ing1.replace(']', '')
      ing3 = ing2.replace("'", '')
      ing3 = ing2.replace('"', '')
      array = ast.literal_eval('[' + ing3 + ']')
      self.exibirIng(array)

    return False


  def REEMBOLSAR(self):
    """
    Permite que o cliente solicite o reembolso de um ingresso específico. Ele solicita ao usuário o ID do ingresso que deseja reembolsar e envia essa informação para o servidor.
    """
    print('\nDigite o ID do ingresso que deseja solicitar o reembolso ou CANCELAR para voltar.\n')
    idInform = input('> ').upper()
    
    if idInform == 'CANCELAR':
      print('Reembolso cancelado.')
      
    elif idInform.isnumeric():
      confirmar = input('\nDeseja realmente confirmar? Digite S ou N.\n> ').upper()
      if confirmar == 'S':
        self.socket.send(str.encode(idInform))
        devolvido = self.socket.recv(1024).decode('utf-8').split(':')
        if devolvido[0] == '+OK':
          limparTerminal()
          print(f'{devolvido[0]}:{devolvido[1]}. Você receberá o reembolso dentro de 30 dias')
        else:
          print('\tID incorreto. Digite o ID correspondente ao ingresso que deseja devolver.\n')
      elif confirmar == 'N':
        print('\nReembolso cancelado.')
      else: 
        print('\nComando errado.')
    else:
      print('ID inválido.')
    
    return False


  def exibirIng(self, array):
    """
    Função auxiliar para exibir visualmente os ingressos adquiridos pelo cliente.
    """
    for i in range(len(array)):
      id = array[i][0]
      categoria = array[i][1]
      
      print(f'''       _____________________ _________________________
      |                     |                         |
      |      B A N D A      |   Data: 06/07/2023      |
      |   E N C A N T U S   |   ID: {id:04d}              |
      |      reecontro      |   Categoria: {categoria:<8}   |
      |_____________________|_________________________|
      \n''')


def limparTerminal():
  """
  É uma função auxiliar que utiliza o módulo os para limpar a saída do terminal, exibindo comandos específicos do sistema operacional.
  """
  os.system('cls' if os.name=='nt' else 'clear')


if __name__ == '__main__':
  """
  Começa a execução do programa principal.
  """
  host = 'localhost'
  port = 8000
  if len(sys.argv) > 1:
    host = sys.argv[1]
  cliente = GNSClient(host, port)

  cliente.INICIAR()
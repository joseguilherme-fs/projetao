import socket
import sys
import random
from threading import Thread, Semaphore, Lock
from classesIngresso import IngressosComprados
from tabelaHash import TabelaHash

 
class GNSServer:
    """
    Representa o servidor de venda de ingressos, onde na tabela hash são armazenados os ingressos comprados, um bloqueio lock para garantir a exclusão mútua e o uso de semáforos (vip, camarote, pista) para controlar a disponibilidade de ingressos.
    """
    def __init__(self, host, porta, th: 'TabelaHash'):
      self._host = host
      self._porta = porta
      self.tabela = th
      self.lock = Lock()
      self.vip = Semaphore(th.vip)
      self.camarote = Semaphore(th.camarote)
      self.pista = Semaphore(th.pista)

  
    def INICIAR(self): 
      """
      Responsável por iniciar o servidor, aceitar os clientes e tratar o CPF.
      """
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)  
      serv = (self._host, self._porta)
      sock.bind(serv)
      sock.listen(50)
		  
      while True:
          con, cliente = sock.accept()
        
          while True:
              cpf = con.recv(1024).decode('utf-8')
            
              if cpf.isnumeric() and len(cpf) == 11: # Tratando o CPF
                  con.send(str.encode('+OK:CPF\n'))
                  Thread(target=self.PROCESSAR_CLIENTE, args=(con, cliente, cpf)).start() # Criando threads.
                  break
              elif cpf == 'SAIR':
                  print('Cliente', cliente, 'enviou', cpf)
                  self.SAIR(con, cpf, cliente)
                  break
              else:
                  con.send(str.encode('-ERROR:CPF\n'))

  
    def PROCESSAR_CLIENTE(self, con, cliente, cpf):
      """
      Responsável por escutar os comandos dos cliente
      """
    
      print('Cliente conectado', cliente)
      while True:
          msg = con.recv(1024).decode()
          if not msg:
              break
          if not self.PROCESSAR_MSG(msg, con, cliente, cpf): # Redireciona para o PROCESSAR_MSG
              break
      print('Cliente desconectado', cliente)

    
    def PROCESSAR_MSG(self, msg, con, cliente, cpf): 
      """
      Reponsável por receber os comandos e chamar as funções.
      """
      comandos = ['COMPRAR', 'INGRESSOS', 'REEMBOLSAR', 'SAIR']
      print('Cliente', cliente, 'enviou', msg)
 
      if msg in comandos:
        funcao = getattr(self, msg)
        confirm = funcao(con, cpf, cliente)
        return confirm
      else:
        con.send(str.encode('-ERROR\n'))
 
    def COMPRAR(self, con, cpf, cliente):
      """
      Responsável pelo método de compra de ingressos. Ele envia informações sobre a disponibilidade de ingressos para o cliente, reserva os ingressos solicitados e registra a compra na tabela hash.  
      """
      disp = f'{int(self.tabela.vip)}:{int(self.tabela.camarote)}:{int(self.tabela.pista)}' # Envia para o servidor os ingressos disponíveis
      print(disp)
      con.send(str.encode(disp))

    
      if self.RESERVAR(con):
        conf = con.recv(1024).decode('utf-8').split(':')
  
        if self.lock.locked(): # Semáforos
          con.send(str.encode('-ERROR:TIME\n'))
        else:
          with self.lock:
            if conf[1] == 'NAO':
              if conf[2] != '0':
                self.vip.release(int(conf[2]))
              if conf[3] != '0':
                self.camarote.release(int(conf[3]))
              if conf[4] != '0':
                self.pista.release(int(conf[4]))
              con.send(str.encode('-ERROR:CANCELADO\n'))
            else:
              bool, total = self.REGISTRARCOMPRAS(int(conf[2]), int(conf[3]), int(conf[4]), disp, cpf)
      
              if bool:
                con.send(str.encode(f'+OK:{total[0]}:{total[1]}:{total[2]}:{total[3]}\n'))
                print(f'{int(self.tabela.vip)}:{int(self.tabela.camarote)}:{int(self.tabela.pista)}')
  
              else:
                con.send(str.encode('-ERROR:SELECAO\n'))
        
        return True
      
      return True
      
    
    def INGRESSOS(self, con, cpf, cliente):
      """"
      Responsável pelo método de visualizar os ingressos e seus IDs.
      """
      ingressos = self.tabela.mostrarIngressos(cpf)

      if len(ingressos) == 0:
        con.send(str.encode("-ERROR:INGRESSOS\n"))
      else:
        con.send(str.encode(f"+OK{ingressos}\n"))

      return True

   
    def REEMBOLSAR(self, con, cpf, cliente):
      """
      Responsável por processar o reembolso de ingressos. Recebe o ID do ingresso e remove da tabela hash.
      """
      idRecebido = con.recv(1024).decode('utf-8')
      id = self.idReal(idRecebido)
      lista = self.tabela.encontrarLista(int(id))
      if lista.registrado(id):
        self.tabela.excluir(int(id))
        con.send(str.encode('+OK:DEVOLVIDO\n'))
      else:
        con.send(str.encode('-ERROR:NAOENCONTRADO\n'))
      
      return True

  
    def SAIR(self, con, cpf, cliente):
      """
      Responsável por finalizar a conexão com um cliente.
      """
      con.send(str.encode('+OK:ADEUS\n'))
      con.close()
      return False

 
    def RESERVAR(self, con):
      """
      Responsável por reservar os ingressos solicitados pelo cliente. Recebe a quantidade desejada de ingressos para cada categoria (VIP, Camarote, Pista) e utiliza semáforos para controlar a disponibilidade desses ingressos.
      """
      qntVIP = con.recv(1024).decode('utf-8').split(':')
      for i in range(int(qntVIP[1])):
        if self.vip.acquire(blocking=False):
          continue
        else:
          con.send(str.encode('-ERROR:NONEVIP\n'))
          return False
      con.send(str.encode('+OK:VIP\n'))

      qntCAM = con.recv(1024).decode('utf-8').split(':')
      for i in range(int(qntCAM[1])):
        if self.camarote.acquire(blocking=False):
          continue
        else:
          con.send(str.encode('-ERROR:NONECAM\n'))
          return False
      con.send(str.encode('+OK:CAM\n'))

      qntPST = con.recv(1024).decode('utf-8').split(':')
      for i in range(int(qntPST[1])):
        if self.pista.acquire(blocking=False):
          continue
        else:
          con.send(str.encode('-ERROR:NONEPST\n'))
          return False
      con.send(str.encode('+OK:PST\n'))

      return True
   
    def REGISTRARCOMPRAS(self, qntVIP, qntCAM, qntPST, qntDisp, cpf):
      """
      Responsável por registrar as compras de ingressos na tabela hash. 
      Ele recebe a quantidade de ingressos comprados para cada categoria, a quantidade disponível de ingressos para cada categoria e o CPF do cliente.
      """
      confirmar = [0,0,0,0]
      disp = qntDisp.split(':')
      categoria = ['vip', 'camarote', 'pista']

      #O método verifica se há ingressos disponíveis, gera IDs aleatórios para os ingressos comprados e registra esses ingressos na tabela hash.
      if int(qntVIP) > 0:
        if int(disp[0]) > 0:
          for i in range(int(qntVIP)):
            id = random.randint(0, 1000)
            lista = th.encontrarLista(id)
            if lista.registrado(id):
              novoid = self.novoID(lista, id)
              if self.tabela.cadastrar(novoid, categoria[0], cpf):
                confirmar[0] += 1
                confirmar[1] += 1
                continue
              else:
                break
            else:
              if self.tabela.cadastrar(id, categoria[0], cpf):
                confirmar[0] += 1
                confirmar[1] += 1
                continue
              else:
                break

      if int(qntCAM) > 0:
        if int(disp[1]) > 0:
          for i in range(int(qntCAM)):
            id = random.randint(0, 1000)
            lista = th.encontrarLista(id)
            if lista.registrado(id):
              novoid = self.novoID(lista, id)
              if self.tabela.cadastrar(novoid, categoria[1], cpf):
                confirmar[0] += 1
                confirmar[2] += 1
                continue
              else:
                break
            else:
              if self.tabela.cadastrar(id, categoria[1], cpf):
                confirmar[0] += 1
                confirmar[2] += 1
                continue
              else:
                break

      if int(qntPST) > 0:
        if int(disp[2]) > 0:
          for i in range(int(qntPST)):
            id = random.randint(0, 1000)
            lista = th.encontrarLista(id)
            if lista.registrado(id):
              novoid = self.novoID(lista, id)
              if self.tabela.cadastrar(novoid, categoria[2], cpf):
                confirmar[0] += 1
                confirmar[3] += 1
                continue
              else:
                break
            else:
              if self.tabela.cadastrar(id, categoria[2], cpf):
                confirmar[0] += 1
                confirmar[3] += 1
                continue
              else:
                break
              
      if confirmar[0] > 0:
        return True, confirmar
      else:
        return False, confirmar

    
    def novoID(self, lista:'IngressosComprados', id):
      """
      Função auxiliar que gera um novo ID aleatório para um ingresso se o ID já estiver registrado na lista de ingressos comprados.
      """
      if not lista.registrado(id):
        return id
      else:
        id = random.randint(0, 1000)
        return self.novoID(lista, id)
        
    
    def idReal(self, id):
      """
      Função auxiliar que remove os zeros à esquerda de um ID e retorna o ID como um número inteiro.
      """
      if id[0] != '0':
        return int(id)
      else:
        return self.idReal(id[1:])

#começa a execução do programa principal. 
if __name__ == '__main__':
  host = '127.0.0.1'
  port = 8000
  if len(sys.argv) > 1:
    host = sys.argv[1]

  ingressos = int(input('Quantidade de ingressos: '))
  th = TabelaHash(ingressos)

  server = GNSServer(host, port, th)
  server.INICIAR()
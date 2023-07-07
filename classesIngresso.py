class Ingresso:
    """
    Representa um ingresso individual.
    """
    def __init__(self, id:int, categoria:str, cpf):
        self.cpf = cpf
        self.categoria = categoria
        self.id = id
        self.prox = None
      

class IngressosComprados:
    """
    Representa a coleção de ingressos comprados.
    """
    def __init__(self, ingressos:int):
        self.__capacidade = ingressos/10
        self.__ocupados = 0
        self.__inicio = None
    
    @property
    def capacidade(self):
        return self.__capacidade
    
    @property
    def ocupados(self):
        return self.__ocupados
    
    @property
    def inicio(self)->'Ingresso':
        return self.__inicio

    """
    estaVazia e estaCheia: responsáveis por verificar se a coleção de ingressos está vazia ou cheia, com base no número de ingressos ocupados e na capacidade total.
    """
    def estaVazia(self):
        
        if self.__ocupados == 0:
            return True
        else:
            return False

    def estaCheia(self):
        if self.__ocupados == self.__capacidade:
          return True
        else:
          return False
          
    #responsável por verificar se existem ingressos comprados pelo CPF fornecido. Ele percorre a lista encadeada de ingressos e adiciona os ingressos correspondentes à lista ingressos. Retornando None se não houver ingressos encontrados.
    def encontrarIngressos(self, cpfProp):
        ingressos = []
        if self.estaVazia():
          return None
        else:
          ingresso = self.__inicio
          while ingresso is not None:
            if ingresso.cpf == cpfProp:
              ingressos.append(f'{(ingresso.id, ingresso.categoria)}')
            ingresso = ingresso.prox

        if len(ingressos) > 0:
          return ingressos
        else:
          return None

    #responsável por retornar a categoria de um ingresso específico com base no ID fornecido. 
    def retornarCategoria(self, id):
      ingresso = self.__inicio
      while ingresso is not None:
        if ingresso.id == id:
          return ingresso.categoria
        ingresso = ingresso.prox

    #responsável por verificar se um ingresso com o ID fornecido está registrado na lista encadeada.
    def registrado(self, id):
        cursor = self.__inicio
        while( cursor != None ):
            if cursor.id == id:
                return True
            else:
                cursor = cursor.prox
        else:
            return False

    #responsável por adicionar um ingresso à lista encadeada.
    def inserir(self, ingresso:'Ingresso'):
        if self.estaVazia():
            self.__inicio = ingresso
            self.__ocupados += 1
        else:
            cursor = self.__inicio
            while cursor.prox is not None:
                cursor = cursor.prox
            cursor.prox = ingresso
            self.__ocupados += 1

    #responsável por remover um ingresso da lista encadeada com base no ID fornecido. 
    def remover(self, id):
        while self.__inicio is not None and self.__inicio.id == id:
            self.__inicio = self.__inicio.prox
            self.__ocupados -= 1

        atual = self.__inicio
        while atual is not None:
            if atual.prox is not None and (atual.prox).id == id:
                atual.prox = (atual.prox).prox
                self.__ocupados -= 1
            else:
                atual = atual.prox

    #responsável por retornar o número de ingressos ocupados.
    def __len__(self):
      return self.__ocupados

    #responsável por percorre a lista encadeada de ingressos e retornar uma string formatada contendo o ID e a categoria de cada ingresso na lista.
    def __str__(self):
        cursor = self.__inicio
        display = '['
        while cursor != None:
            display += f'({cursor.id}, {cursor.categoria}), '
            cursor = cursor.prox
        display = display[:-2] + ']'

        return display
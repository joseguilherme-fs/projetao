from classesIngresso import IngressosComprados, Ingresso

class TabelaException(Exception):
  def __init__(self, msg):
    super().__init__(msg)

class TabelaHash:
    """
    A tabela hash é responsável por armazenar os ingressos comprados.
    """
    def __init__(self, ingressos:int):
        self.table = [IngressosComprados(ingressos) for i in range(10)]
        self.total = ingressos
        self.vip = 0.2*ingressos
        self.camarote = 0.3*ingressos
        self.pista = 0.5*ingressos


    def __len__(self):
      """
      Retorna o tamanho da tabela, que é igual ao número de listas de ingressos na tabela.
      """
      return len(self.table)


    def encontrarLista(self, idIngresso:int)->'IngressosComprados':
        """
        Recebe um ID de ingresso e retorna a lista de ingressos correspondente com base no cálculo do slot usando o operador % e o tamanho da tabela.
        """
        slot = idIngresso % 10
        lista = self.table[slot]
        
        return lista
      

    def mostrarIngressos(self, cpf):
      """
      Recebe um CPF e retorna uma lista contendo todos os ingressos comprados pelo CPF fornecido.
      """
      todos = []
      for lista in self.table:
        ingressos = lista.encontrarIngressos(cpf)
        if ingressos is None:
          continue
        for i in range(len(ingressos)):
          todos.append(ingressos[i])
          
      return todos


    def cadastrar(self, id, categoria, cpf):
        """
        Responsável por cadastrar um novo ingresso na tabela hash.
        """
        idIngresso = id
        slot = self.__hash(idIngresso)
        lista = self.table[slot]
        cadastrado = False

        while True:
          if not lista.estaCheia():
            if getattr(self, f'{categoria}') > 0:
              ingresso = Ingresso(idIngresso, categoria, cpf)
              lista.inserir(ingresso)
              setattr(self, f'{categoria}', getattr(self, f'{categoria}') - 1)
              cadastrado = True
              break
            else:
              break
          else:
            idIngresso += 1
            slot = self.__rh(slot)
            lista = self.table[slot]

        return cadastrado
          

    def excluir(self, idIngresso:int):
        """
        Recebe o ID de um ingresso como parâmetro e remove o ingresso correspondente da tabela hash.
        """
        slot = self.__hash(idIngresso)
        lista = self.table[slot]

        cursor = lista.inicio
        while cursor.id != idIngresso:
            cursor = cursor.prox
        
        categoria = cursor.categoria
        lista.remover(idIngresso)
        if categoria == 'vip':
            self.vip += 1
        if categoria == 'camarote':
            self.camarote += 1
        if categoria == 'pista':
            self.pista += 1   


    def __hash(self, key:any):
        """
        Método interno que recebe uma chave e retorna o valor do hash da chave modulado por 10.
        """
        return hash(key) % 10


    def __rh(self, slot):
      """
      Método interno que recebe um slot e retorna o próximo slot na tabela hash. Ele é usado quando ocorre uma colisão durante a inserção de um ingresso e é necessário encontrar um novo slot disponível.
      """
      return (slot+1) % 10


    def __str__(self):
        """
        Retorna uma representação em string da tabela hash. Ele percorre cada lista de ingressos na tabela e as concatena em uma única string.
        """
        s = '[ '
        for i in range(10):
            s += f'{self.table[i]}, '
        s = s[:-2] + ' ]'
        return s
# coding=utf-8


class Player: # Representa um jogador de futebol.

    def __init__(self, key):
        self.id = key  # Identificador único do jogador.
        # Dicionário que armazena os jogadores aos quais ele está conectado
        # e a força dessa conexão (similaridade).
        self.connectedTo = {}
        # Dicionário que armazena as habilidades do jogador (ID da habilidade: valor).
        self.abilities = {}
        self.position = None  # Posição do jogador em campo.
        self.salary = 0  # Salário do jogador.

    def add_neighbor(self, nbr, weight=0): # Adiciona um vizinho (outro jogador) à lista de conexões.
        self.connectedTo[nbr] = weight

    def __str__(self):
        return str(self.id) + ' connectedTo : ' + str([x.id for x in self.connectedTo])

    # Métodos de acesso aos atributos do jogador.
    def get_connection(self):  # get the neighbors
        return self.connectedTo.keys()

    def get_id(self):
        return self.id

    def get_abilities(self):
        return self.abilities

    def get_position(self):
        return self.position

    def get_salary(self):
        return self.salary

    def get_weight(self, nbr):  # get the weight of a neighbor
        return self.connectedTo[nbr]

class Goalkeeper:

    def __init__(self, g_id):
        self.id = g_id # Identificador único do goleiro.
        self.ability = [] # Lista de habilidades do goleiro (provavelmente específica para goleiros).
        self.rating = 0 # Classificação geral do goleiro.
        self.salary = 0 # Salário do goleiro.

    #  Métodos de acesso aos atributos do goleiro.
    def get_id(self):
        return self.id

    def get_ability(self):
        return self.ability

    def get_rating(self):
        return self.rating

    def get_salary(self):
        return self.salary


class CutPlayer:
    """
    The player to be pruning
    """

    def __init__(self, key):
        self.id = key #  Identificador único do jogador.
        self.cut_pos = None  # Indica se o jogador é de ataque/meio-campo ou ou defesa
        self.cut_position = ""  # Posição específica do jogador a ser removido.
        self.cut_salary = 0  # Salário do jogador a ser removido.

    # Métodos de acesso aos atributos do jogador a ser removido.
    def get_id(self):
        return self.id

    def get_cut_pos(self):
        return self.cut_pos

    def get_cut_position(self):
        return self.cut_position

    def get_cut_salary(self):
        return self.cut_salary


class Graph:

    def __init__(self):
        self.vertexList = {} # Dicionário que armazena os jogadores (vértices do grafo) e suas conexões.
        self.numVertices = 0 # Número total de vértices no grafo.

    def add_vertex(self, key): # Adiciona um jogador (vértice) ao grafo.
        self.numVertices = self.numVertices + 1
        newVertex = Player(key)
        self.vertexList[key] = newVertex
        return newVertex

    def get_vertex(self, key): # Retorna um jogador (vértice) do grafo, se existir.
        if key in self.vertexList:
            return self.vertexList[key]
        else:
            return None

    def __contains__(self, key):
        return key in self.vertexList

    def add_edge(self, f, t, cost=0): # Adiciona uma conexão (aresta) entre dois jogadores no grafo.
        # se f e t não estiverem no gráfico, adicione esses dois nós
        if f not in self.vertexList:
            nv = self.add_vertex(f)

        if t not in self.vertexList:
            nv = self.add_vertex(t)

        self.vertexList[f].add_neighbor(self.vertexList[t], cost)

    def get_vertices(self):  # Retorna uma lista com todos os jogadores (vértices) do grafo.
        return self.vertexList.keys()

    def __iter__(self):
        return iter(self.vertexList.values())
	

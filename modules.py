# coding=utf-8

import numpy as np


"""
  :params player_attributes --> dict()
  player id : [team, nationality]

- Calcula a matriz de similaridade entre jogadores (similarity).
Recebe:
--> network_name: Nome da rede (Back ou Forward) para fins de exibição.
--> player_attributes: Dicionário com os atributos de cada jogador (time e nacionalidade).
- Para cada par de jogadores, calcula a similaridade Jaccard
    (jaccard(attr_i, attr_j)), que mede a proporção de atributos em comum entre dois jogadores.
- Preenche a matriz similarity com as similaridades calculadas
    (simétrica, pois sim(i, j) = sim(j, i)).
- Calcula e exibe a densidade da matriz de adjacência, que indica
    a proporção de conexões existentes em relação ao total possível.
"""

def cal_similarity(network_name, player_attributes):

    no = len(player_attributes)
    similarity = np.zeros((no, no))
    edge = 0

    for i in range(0, no-1):
        attr_i = player_attributes[i]
        for j in range(i, no-1):
            attr_j = player_attributes[j]
            sim = jaccard(attr_i, attr_j)  # calculate the similarity
            if sim > 0:
                edge += 1
            similarity[i][j] = sim
            similarity[j][i] = sim  # sim(i,j) = sim(j,i)

    density = (edge*2) / (no*no)  # the density of the players' adjacent matrix
    edge = edge - no

    print("The %s network includes %d vertex and %d edges, the density is %f"
          % (network_name, no, edge, density)
         )

    return similarity

"""
- Função auxiliar que calcula a similaridade Jaccard entre dois arrays de atributos.
- Encontra a interseção e a união dos arrays.
- Retorna a razão entre o tamanho da interseção e o tamanho da união.
"""
def jaccard(array_1, array_2):
    inter = [val for val in array_1 if val in array_2]
    union = list(set(array_1).union(set(array_2)))
    ja = len(inter) / len(union)
    return ja


"""
- Calcula a média das habilidades (ability_avg) de cada jogador para cada habilidade presente em player_abilities_name.
Recebe:
--> player_abilities_name: Dicionário com as habilidades de cada jogador.

- Para cada habilidade:
--> Soma os valores da habilidade para todos os jogadores.
--> Divide a soma pelo número de jogadores para obter a média.
"""
def cal_ability_avg(player_abilities_name):

    ability_avg = {}

    for ability in player_abilities_name:
        total = 0
        c = 0
        for value in player_abilities_name[ability].values():
            total = total + value
            c += 1
        ability_avg[ability] = total / c

    return ability_avg
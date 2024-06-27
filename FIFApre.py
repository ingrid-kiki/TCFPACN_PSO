# coding=utf-8

"""
Data pre-processing for FIFA dataset
"""

import numpy as np
import pandas as pd
import random
import math
#import FBTP.players as players
from collections import OrderedDict

# URLs dos arquivos CSV no GitHub
url_goalkeepers = 'https://raw.githubusercontent.com/ShenbaoYu/TCFPACN/main/Data/FIFA/Goalkeeper.csv'
url_back = 'https://raw.githubusercontent.com/ShenbaoYu/TCFPACN/main/Data/FIFA/Back.csv'
url_forward = 'https://raw.githubusercontent.com/ShenbaoYu/TCFPACN/main/Data/FIFA/Forward.csv'

#url = 'https://raw.githubusercontent.com/ShenbaoYu/TCFPACN/main/Data/FIFA/Goalkeeper.csv'  # Substitua pelos valores corretos
#df = pd.read_csv(url)
#_meta = df  # Use o DataFrame lido do GitHub

"""
Lê um arquivo contendo critérios de avaliação de jogadores
(por exemplo, importância de habilidades específicas para cada posição).
Normaliza os valores dos critérios para que a soma total seja 1.
"""
def read_criteria(path, criteria_file):
    criteria = {}
    with open(path + criteria_file, 'r') as cf:
        while True:
            line = cf.readline()
            if not line:
                break
            name = line.split(":")[0]
            value = line.split(":")[1][:-1]

            criteria[name] = int(value)

    criteria = normalize(criteria)

    return criteria

"""
Lê informações sobre goleiros de um arquivo CSV.
Cria objetos Goalkeeper para cada goleiro, preenchendo seus atributos (ID, rating, salário, habilidades).
O salário é calculado com base no rating do goleiro usando uma fórmula exponencial.
"""
def get_goalkeepers(url_goalkeepers):#(path, file_name):
    """
    Obtém informações sobre todos os goleiros.

    Args:
        url: URL do arquivo CSV contendo os dados dos goleiros.

    Returns:
        Uma lista de objetos Goalkeeper.

    """

    goal_keepers = [] # get all goalkeepers

    # tratamento de erro caso falhe a leitura do arquivo CSV
    try:
        _meta = pd.read_csv(url_goalkeepers, delimiter=',')  # Lê o CSV uma única vez
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return goal_keepers  # Retorna uma lista vazia em caso de erro

    for idx, _data in _meta.iterrows(): # Use o DataFrame lido no try-except
        gk_id = _data['sofifa_id']
        gk = players.Goalkeeper(gk_id)
        gk.rating = _data['overall']  # the rating
        # gk.salary = _data['value_eur']  # salary (Euro)
        gk.salary = 0.0006375 * math.exp(0.1029*gk.rating)  # calculate salary
        gk.ability = _data.loc[['gk_diving', 'gk_handling', 'gk_kicking',
                                'gk_reflexes', 'gk_speed', 'gk_positioning']
                              ].tolist()
        goal_keepers.append(gk)

    return goal_keepers

"""
- Lê informações sobre jogadores de um arquivo CSV, diferenciando entre
jogadores de defesa (Back) e de ataque/meio-campo (Forward).
- Cria dicionários para armazenar:
--> Atributos dos jogadores (clube, nacionalidade).
--> Habilidades dos jogadores (com seus respectivos valores).
--> Posições dos jogadores.
--> Ratings dos jogadores.
--> IDs dos jogadores.
- Preenche esses dicionários com os dados lidos do arquivo.
- Para jogadores sem posição definida, atribui uma posição aleatória da
lista de posições possíveis para sua categoria (Back ou Forward).
"""
def read_info(url): #file_name):
    """
    Lê informações sobre jogadores de um arquivo CSV.

    Args:
        url: URL do arquivo CSV contendo os dados dos jogadores.

    Returns:
        Uma tupla contendo: ability_name_id, player_attributes, player_abilities_name,
        player_position, player_rating, player_no_id.
    """
    DIV = 'Back' if 'Back' in url else 'Forward'  # Determina DIV com base na URL
    #DIV = file_name.split('.')[0]

    player_attributes = {}  # playbers attributes, including club and nationality
    player_abilities_name = OrderedDict()  # personal abilities
    player_position = {}  # players' position {id:position}
    player_rating = {}  # players' rating {id:rating}
    # player_salary = {}  # players' salary {id:salary}

    try:
        _meta = pd.read_csv(url, delimiter=',')
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return {}, {}, {}, {}, {}, {}  # Retorna dicionários vazios em caso de erro

    attrs = [column for column in _meta][44:73]
    ability_name_id = dict(zip(attrs, [i for i in range(len(attrs))]))
    for att in attrs:
        player_abilities_name[att] = {}

    player_no_id = {}  # player's number : id
    for idx, _data in _meta.iterrows():
        player_no_id[idx] = _data['sofifa_id']  # player's id
        player_position[idx] = get_position(_data, DIV)  # player's position
        player_rating[idx] = _data['overall']  # player's rating
        # if _data['value_eur'] != 0:
        #     player_salary[idx] = _data['value_eur']  # salary (Euro)
        # else:
        #      player_salary[idx] = cal_player_salary(_data['overall'])


        # player's attributes, including club and nationality
        player_attributes[idx] = [_data['club'], _data['nationality']]
        abis = dict(_data.iloc[44:73])
        for abi, val in abis.items():
            player_abilities_name[abi][idx] = val

    return ability_name_id,       \
           player_attributes,     \
           player_abilities_name, \
           player_position,       \
           player_rating,         \
           player_no_id


"""
Função auxiliar usada por <read_info> para obter a posição de um jogador.
Se a posição do jogador no arquivo for válida para sua categoria (Back ou Forward), retorna essa posição.
Caso contrário, escolhe aleatoriamente uma posição válida da lista de posições para sua categoria.
"""
def get_position(data, div):
    if div == 'Back':
        BA = ['LWB','RWB','LB','LCB','CB','RCB','RB']
        if not data['team_position'] in BA:
            return random.choice(BA)  # choose a position randomly
        else:
            return data['team_position']
    elif div == 'Forward':
        FM = ['LS','LF','CF','RF','RS','ST','LW','SS','RW',  # Forward
              'LAM','CAM','RAM','CM','LM','LCM','RCM','RM','LDM','CDM','RDM']
        if not data['team_position'] in FM:
            return random.choice(FM)  # choose a position randomly
        else:
            return data['team_position']

"""
- Função auxiliar usada por read_criteria para normalizar os valores de um dicionário.
- Divide cada valor pela soma total dos valores, garantindo que a soma dos valores normalizados seja 1.
"""
def normalize(dict_type):
    total = sum(v for v in dict_type.values())
    tmp = {}
    for key, value in dict_type.items():
        tmp[key] = value / total
    return tmp
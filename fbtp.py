# coding=utf-8

"""
Discovering a cohesive team based on FBTP algorithm
"""

import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.append(BASE_DIR)
sys.path.append('TCFPACN')

from FBTP import greedy
from FBTP import players as ps

import numpy as np
from scipy.stats import rankdata


def FBTP(gks, abi_name_id,
         p_no_id_back, pg_back, cri_back,
         p_no_id_forward, pg_forward, cri_forward,
         budget, alpha, beta, datasource):

    """
    FUNCTION: team composition based on Finding Best Team with Pruning (FBTP) model
    (1) we first discover the team without budget constraint;
    (2) we prune the team if the cost exceeds the budget

    - Esta é a função principal que coordena o processo de seleção do time.
    - Recebe como entrada:
    --> gks:
        Lista de goleiros.

    --> abi_name_id:
        Dicionário que mapeia nomes de habilidades para seus IDs.

    --> p_no_id_back, pg_back:
        Informações dos jogadores de defesa e seu grafo.

    --> p_no_id_forward, pg_forward:
        Informações dos jogadores de ataque/meio-campo e seu grafo.

    --> cri_back, cri_forward:
        Critérios de avaliação para jogadores de defesa e ataque/meio-campo.

    --> budget:
        Orçamento disponível para contratar jogadores.

    --> alpha, beta:
        Parâmetros de peso para habilidades e homogeneidade.

    --> datasource:
        Indica o conjunto de dados usado (PES ou FIFA).
    """

    print("The Budget Constraint is:%.3f" % budget)

    team = {}

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # +                                                                 +
    # +         Select the players without budget constraint            +
    # +                                                                 +
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    """
    - Escolhe o melhor goleiro com base na média de suas habilidades.
    - Seleciona os melhores jogadores de defesa e ataque/meio-campo
        usando <greedy.player_opt_subgraph>, que encontra o subgrafo ótimo
          no grafo de jogadores, maximizando uma combinação de habilidades e homogeneidade.
    """
    print('Select the players without budget constraint ')
    # find the best goalkeeper
    team["GK"] = list()
    best_gk = best_goalkeeper(gks)
    team["GK"].append(best_gk.get_id())

    # select the best backwards
    team["Back"] = list()
    opt_back = greedy.player_opt_subgraph(p_no_id_back, pg_back, cri_back,
                                          abi_name_id, alpha, beta, 'Back',
                                          datasource
                                          )
    team["Back"] = opt_back

    # select the forward/midfielder
    team["Forward"] = list()
    opt_forward = greedy.player_opt_subgraph(p_no_id_forward, pg_forward, cri_forward,
                                             abi_name_id, alpha, beta, 'Forward',
                                             datasource
                                            )
    team["Forward"] = opt_forward

    # 1. calculate the total cost
    # 2. calculate the  average team ability
    # 3. calculate the heterogeneity
    team_cost, team_ability, homo_back, homo_forward, opt_player_cf \
        = cal_cost_abi_homo(team, gks, pg_back, pg_forward, cri_back,
                            cri_forward, abi_name_id
                           )


    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # +                                                                 +
    # +         Pruning if necessary                                    +
    # +                                                                 +
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    - Se o custo da equipe exceder o orçamento, entra em um loop de poda:
    --> Calcula o custo, habilidade média, homogeneidade e custo-benefício da equipe.
    --> Remove o jogador com o menor custo-benefício usando <cut_base_cf>.
    --> Seleciona um jogador candidato para substituir o jogador removido,
        buscando um jogador com boa habilidade, homogeneidade e que se encaixe no orçamento.
    - Repete o processo de poda até que o custo da equipe esteja dentro do orçamento.
    - Retorna o time final selecionado, que atende à restrição de orçamento
        e maximiza a habilidade e homogeneidade.
    """
    team_real = {"GK": [], "Back": [], "Forward": []}

    # Converter índices da gbest para IDs de jogadores
    # team_real["GK"].append(player_no_id_back[gbest[0]])  # Goleiro
    # team_real["Back"] = [player_no_id_back[i] for i in gbest[1:5]]  # Defesa
    # team_real["Forward"] = [player_no_id_forward[i] for i in gbest[5:]]  # Ataque/Meio-campo

    while True:

        if team_cost < budget:
            team_real["GK"].append(player_no_id_back[gbest[0]])  # Goleiro

            for i in team["Back"]:
                team_real["Back"] = [player_no_id_back[i] for i in gbest[1:5]]  # Defesa

            for j in team["Forward"]:
                team_real["Forward"] = [player_no_id_forward[i] for i in gbest[5:]]  # Ataque/Meio-campo
            
                       
            print("\n",
                  "\t", "Os jogadores otimizados são:", team_real, "\n",
                  "\t", "O custo total é:", round(-gbest_fitness, 3), "\n",  # Usar o fitness da gbest
                  "\t", "A habilidade média da equipe é:", round(team_ability, 3), "\n",
                  "\t", "O desempenho de custo é:", opt_player_cf, "\n",
                  "\t", "A homogeneidade do retrocesso é:%.4f" % homo_back, "\n",
                  "\t", "A heterogeneidade do atacante/meio-campista é: %.4f" % homo_forward,
                  "\n")

            break
        else:
            # Pruning
            team_update = cut_base_cf(opt_player_cf, team, pg_back, pg_forward, gks,
                                      cri_back, cri_forward, abi_name_id,
                                      alpha=0.7, beta=0.15)
            # calculate cost, average ability and homogeneity
            team_up_cost, team_up_ability, homo_up_back, homo_up_forward, opt_player_cf_up\
                = cal_cost_abi_homo(team, gks, pg_back, pg_forward, cri_back, cri_forward, abi_name_id)

            # update
            team = team_update
            team_cost = team_up_cost
            team_ability = team_up_ability
            homo_back = homo_up_back
            homo_forward = homo_up_forward
            opt_player_cf = opt_player_cf_up

            print('Pruning... the current team cost is %.2f' % team_cost)

    return team_real

# Encontra o goleiro com a maior média de habilidades.
def best_goalkeeper(gks):
    opt_gk = ''
    score_max = 0
    for gk in gks:
        # calculate the personal aboility of goalkeeper
        gk_score = sum(gk.ability) / len(gk.ability)
        if score_max < gk_score:
            score_max = gk_score
            opt_gk = gk
    print("The best goalkeeper without budget constraint is:", opt_gk.id)

    return opt_gk

# Calcula o custo total da equipe, habilidade média, homogeneidade e custo-benefício de cada jogador.
def cal_cost_abi_homo(particle, pg_back, pg_forward, cri_back, cri_for, abi_name_id, budget):
    """
    Calcula o fitness da equipe representada pela partícula.

    Args:
        particle: Array representando a partícula (índices dos jogadores no grafo).
        pg_back: Grafo dos jogadores de defesa.
        pg_forward: Grafo dos jogadores de ataque/meio-campo.
        cri_back: Critérios de avaliação para jogadores de defesa.
        cri_for: Critérios de avaliação para jogadores de ataque/meio-campo.
        abi_name_id: Dicionário que mapeia nomes de habilidades para seus IDs.
        budget: Orçamento máximo da equipe.

    Returns:
        O fitness da equipe (um valor negativo para indicar que deve ser minimizado).
    """

    team_cost = 0
    team_ability = 0
    homo_back = 0
    homo_forward = 0

    # Considerar o goleiro (primeiro elemento da partícula)
    gk_idx = particle[0]
    gk = next((gk for gk in gks if gk.id == player_no_id_back[gk_idx]), None) # Assuming gks is a global variable or accessible from this scope
    if gk is None:
        return -np.inf  # Goleiro inválido, fitness muito baixo
    team_cost += gk.get_salary()
    team_ability += sum(gk.ability) / len(gk.ability)

    # Considerar os jogadores de defesa (próximos 4 elementos da partícula)
    back_indices = particle[1:5]
    homo_back = cal_homo(back_indices, pg_back)
    for i in back_indices:
        cost = pg_back.vertexList[i].salary
        team_cost += cost
        abi = cal_player_ability(pg_back.vertexList[i].abilities, cri_back, abi_name_id)
        team_ability += abi

    # Considerar os jogadores de ataque/meio-campo (últimos 6 elementos da partícula)
    forward_indices = particle[5:]
    homo_forward = cal_homo(forward_indices, pg_forward)
    for j in forward_indices:
        cost = pg_forward.vertexList[j].salary
        team_cost += cost
        abi = cal_player_ability(pg_forward.vertexList[j].abilities, cri_for, abi_name_id)
        team_ability += abi

    team_ability /= 11  # Média da habilidade da equipe (11 jogadores)

    # Penalizar se o custo exceder o orçamento
    cost_penalty = max(0, team_cost - budget) * 100  # Ajuste o fator de penalidade conforme necessário

    # O fitness é a soma ponderada da habilidade e da homogeneidade, com penalidade por custo
    fitness = alpha * team_ability + (1 - alpha - beta) * (1 - homo_back) + beta * homo_forward - cost_penalty

    return -fitness  # Retornamos o negativo para que o PSO minimize o valor (maior fitness)


# Remove o jogador com o menor custo-benefício e encontra um candidato para substituí-lo.
def cut_base_cf(player_cf, team, pg_back, pg_forward, gks, cri_back, cri_for, abi_name_id, alpha, beta):
    """
    FUNCTION: Pruning based on the cost performance
    """

    # 1. find the player with the lowest of cost performance
    cut_player = ps.CutPlayer(None)
    cf_min = sys.maxsize
    for p, cf in player_cf.items():
        if cf < cf_min:
            cf_min = cf
            cut_player.id = p

    # 2. delete the player
    for pos, players in team.items():
        if cut_player.id in players:
            players.remove(cut_player.id)
            cut_player.cut_pos = pos
            break

    # 3. find candidate player
    candidate = None

    if cut_player.get_cut_pos() == "Back":

        cut_player.cut_salary = pg_back.vertexList[cut_player.get_id()].salary
        cut_player.cut_position = pg_back.vertexList[cut_player.get_id()].position
        candidate = select_candidate(team[cut_player.get_cut_pos()], pg_back, cut_player,
                                     cri_back, abi_name_id, alpha, beta)
        team[cut_player.get_cut_pos()].append(candidate)

    elif cut_player.get_cut_pos() == "Forward":

        cut_player.cut_salary = pg_forward.vertexList[cut_player.get_id()].salary
        cut_player.cut_position = pg_forward.vertexList[cut_player.get_id()].position
        candidate = select_candidate(team[cut_player.get_cut_pos()], pg_forward, cut_player,
                                     cri_for, abi_name_id, alpha, beta)
        team[cut_player.get_cut_pos()].append(candidate)

    else:
        # the player to be cut is goalkeeper
        opt_abi = 0
        for gk in gks:
            if gk.id == cut_player.get_id():
                cut_player.cut_salary = gk.get_salary()
                continue
            abi = sum(gk.ability)/len(gk.ability)
            if opt_abi < abi and gk.get_salary() < cut_player.get_cut_salary():
                opt_abi = abi
                candidate = gk.id
        team["GK"].append(candidate)

    return team

# Seleciona o melhor jogador candidato para substituir um jogador removido,
# considerando habilidades, homogeneidade, densidade no grafo e salário.
def select_candidate(team_sub, pg, cut_player, criteria, abi_name_id, alpha, beta):

    neighbor = list()
    for player in team_sub:
        for key in pg.vertexList[player].connectedTo.keys():
            # focus only on the position to be cut and neglect the players has been selected
            if key.id not in neighbor and\
                    key.id not in team_sub and key.id != cut_player.get_id() and\
                    key.position == cut_player.get_cut_position():
                neighbor.append(key.id)

    # function = ability + density + homogeneity
    density = {}
    team_ability = {}
    team_gini = {}
    team_homo = {}
    for ne in neighbor:

        ne_abi = greedy.cal_player_ability(
            pg.vertexList[ne].abilities, criteria, abi_name_id)

        weight = 0
        te_abi = ne_abi
        for op in team_sub:
            if pg.vertexList[op] in pg.vertexList[ne].connectedTo:
                weight += pg.vertexList[ne].get_weight(pg.vertexList[op])
                te_abi += greedy.cal_player_ability(pg.vertexList[op].abilities, criteria, abi_name_id)

        gini = greedy.cal_homogeneity(pg.vertexList, ne, team_sub)

        d = weight / (len(team_sub) + 1)
        density[ne] = d
        team_ability[ne] = te_abi
        team_gini[ne] = gini

    if cut_player.get_cut_pos() == "Back":
        for key, value in team_gini.items():
            team_homo[key] = 1 / value
    elif cut_player.get_cut_pos() == "Forward":
        for key, value in team_gini.items():
            team_homo[key] = value

    # find the best player with team ability + density + homogeneity
    score_final = {}
    score_max = 0
    candidate = None

    team_ability_nor = greedy.normalize_min_max(team_ability)
    team_homo_nor = greedy.normalize_min_max(team_homo)

    for player_id, value in team_ability_nor.items():
        # score = abilities + density + homogeneity
        score = alpha * team_ability_nor[player_id] +\
                beta * density[player_id] +\
                (1 - alpha - beta) * (team_homo_nor[player_id])

        score_final[player_id] = score

        if score_max < score and \
           pg.vertexList[player_id].salary < cut_player.get_cut_salary():
            score_max = score
            candidate = player_id

    return candidate

# Calcula a homogeneidade da equipe usando o índice de Gini.
def cal_homo(team, pg):
    homo = 0
    diff = {}
    avg_tmp = {}
    avg = {}
    gini_co = {}

    for i in range(0, len(team)):
        for j in range(0, len(team)):
            for abi_id in pg.vertexList[i].abilities.keys():
                d = abs(pg.vertexList[team[i]].abilities[abi_id] -
                        pg.vertexList[team[j]].abilities[abi_id])
                if abi_id not in diff:
                    diff[abi_id] = d
                else:
                    diff[abi_id] += d

    for player in team:
        for abi_id in pg.vertexList[player].abilities.keys():
            if abi_id not in avg_tmp:
                avg_tmp[abi_id] = pg.vertexList[player].abilities[abi_id]
            else:
                avg_tmp[abi_id] += pg.vertexList[player].abilities[abi_id]

    for abi_id, value in avg_tmp.items():
        avg[abi_id] = avg_tmp[abi_id]/len(team)

    for abi_id in diff.keys():
        gini_co[abi_id] = (1 / (2 * pow(len(team), 2) * avg[abi_id])) * diff[abi_id]

    for value in gini_co.values():
        homo += value

    homo = homo / len(gini_co)

    return homo
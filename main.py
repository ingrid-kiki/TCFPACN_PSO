# coding=utf-8
"""
Modelo TC-FPACN: Composição de time baseada em rede de colaboração de jogadores de futebol.
"""

# Importações
import os, sys           # Funções de sistema e manipulação de caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.getcwd()))
#print(BASE_DIR)
sys.path.append(BASE_DIR)
sys.path.append('TCFPACN')

from FBTP import PESpre, FIFApre, fbtp, modules, greedy  # Importa módulos personalizados para o modelo
import pickle             # Serialização de objetos Python
import logging            # Registro de eventos e mensagens

# Funções para salvar e carregar parâmetros
def save(filepath, params):
    with open(filepath, 'wb') as file:
        pickle.dump(params, file) # Salva parâmetros em um arquivo usando pickle
        logging.info("save parameters to %s" % filepath)

# Carrega parâmetros de um arquivo usando pickle
def load(filepath):
    with open(filepath, 'rb') as file:
        params = pickle.load(file).values()
        logging.info("load parameters from %s" % filepath)
        return params

# Função para redirecionar a saída para um arquivo de log
def out_to_file(path, model_name): # Cria um objeto logger para escrever em arquivo e no terminal

    class logger(object):

        def __init__(self, file_name, path):
            self.terminal = sys.stdout
            self.log = open(os.path.join(path, file_name), mode='a', encoding='utf8')

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)

        def flush(self):
            pass

    sys.stdout = logger(model_name + '.log', path=path)


# Início do programa principal
if __name__ == '__main__':

    DATASET = 'PES'  # Escolha do conjunto de dados (PES ou FIFA)
    #DATASET = 'FIFA'  # Escolha do conjunto de dados (PES ou FIFA)

    # Configurações específicas para cada conjunto de dados (arquivos, parâmetros)
    if DATASET == 'PES':

        FILE_GOALKEEPER = "Goalkeeper.xlsx"
        FILE_BACK = "Back.xlsx"
        FILE_FORWARD = "Forward.xlsx"
        CRITERIA_BACK = "Criteria_Back.txt"
        CRITERIA_FORWARD = "Criteria_Forward.txt"

        ALPHA = 0.6
        BETA = 0.2
        BUDGET = 100

        FILE_PATH = 'TCFPACN'+'/Data/'+DATASET+'/'
        cri_back = PESpre.read_criteria(FILE_PATH, CRITERIA_BACK)  # read the backward criteria
        cri_forward = PESpre.read_criteria(FILE_PATH, CRITERIA_FORWARD)  # read the forward/midfielder criteria

        # 1: the Goalkeepers
        gks = PESpre.get_goalkeepers(FILE_PATH, FILE_GOALKEEPER)  # get all goalkeepers
        save("TCFPACN"+ "/FBTP/params/" + DATASET +'/Goalkeepers', {'gks':gks})
        gks = next(iter(load("TCFPACN"+ "/FBTP/params/" + DATASET + '/Goalkeepers')))

        # 2: the Back network
        abi_name_id, p_attrs_back, p_abis_name_back, p_pos_back, p_r_back, p_no_id_back = \
        PESpre.read_info(FILE_PATH, FILE_BACK)  # read backwards information
        sim_back = modules.cal_similarity('Back', p_attrs_back)  # calculate the similarity

        save("TCFPACN"+ "/FBTP/params/" + DATASET +'/info_back', {'abi_name_id':abi_name_id, 'p_attrs_back':p_attrs_back, 'p_abis_name_back':p_abis_name_back,'p_pos_back':p_pos_back, 'p_r_back':p_r_back, 'p_no_id_back':p_no_id_back}
            )
        save("TCFPACN"+ "/FBTP/params/" + DATASET +'/sim_back', {'sim_back':sim_back})
        abi_name_id, p_attrs_back, p_abis_name_back, p_pos_back, p_r_back, p_no_id_back = \
            load("TCFPACN"+ "/FBTP/params/" + DATASET + '/info_back')
        sim_back = next(iter(load("TCFPACN"+ "/FBTP/params/" + DATASET + '/sim_back')))
        abi_avg_back = modules.cal_ability_avg(p_abis_name_back)
        # get the network of back
        pg_back = greedy.players_graph_construction(sim_back, abi_avg_back, p_abis_name_back,
                                                    abi_name_id, p_pos_back, p_r_back
                                                    )

        # 3: the Forward/Midfielder network
        abi_name_id, p_attrs_forward, p_abis_name_forward, p_pos_forward, p_r_forward, p_no_id_forward = \
        PESpre.read_info(FILE_PATH, FILE_FORWARD)  # read forward/midfielder information
        sim_forward = modules.cal_similarity('Forward', p_attrs_forward)

        save("TCFPACN"+ "/FBTP/params/" + DATASET +'/info_forward', {'abi_name_id':abi_name_id, 'p_attrs_forward':p_attrs_forward,
                                                                'p_abis_name_forward':p_abis_name_forward, 'p_pos_forward':p_pos_forward,
                                                                'p_r_forward':p_r_forward, 'p_no_id_forward':p_no_id_forward
                                                                }
            )
        save("TCFPACN"+ "/FBTP/params/" + DATASET +'/sim_forward', {'sim_forward':sim_forward})
        abi_name_id, p_attrs_forward, p_abis_name_forward, p_pos_forward, p_r_forward, p_no_id_forward = \
            load("TCFPACN"+ "/FBTP/params/" + DATASET + '/info_forward')
        sim_forward = next(iter(load("TCFPACN"+ "/FBTP/params/" + DATASET +  '/sim_forward')))
        abi_avg_forward = modules.cal_ability_avg(p_abis_name_forward)
        pg_forward = greedy.players_graph_construction(sim_forward, abi_avg_forward, p_abis_name_forward,
                                                       abi_name_id, p_pos_forward, p_r_forward
                                                       )
    elif DATASET == 'FIFA':
        FILE_GOALKEEPER = "Goalkeeper.csv"
        FILE_BACK = "Back.csv"
        FILE_FORWARD = "Forward.csv"
        CRITERIA_BACK = "Criteria_Back.txt"
        CRITERIA_FORWARD = "Criteria_Forward.txt"

        ALPHA = 0.5
        BETA = 0.3
        BUDGET = 8

        FILE_PATH = 'TCFPACN' +'/Data/'+DATASET+'/'
        cri_back = FIFApre.read_criteria(FILE_PATH, CRITERIA_BACK)  # read the backward criteria
        cri_forward = FIFApre.read_criteria(FILE_PATH, CRITERIA_FORWARD)  # read the forward/midfielder criteria

        # 1: the Goalkeepers
        gks = FIFApre.get_goalkeepers(FILE_PATH, FILE_GOALKEEPER)
        save("TCFPACN"+ "/FBTP/params/" + DATASET +'/Goalkeepers', {'gks':gks})

        # Carregamento de dados pré-processados (goleiros, informações de jogadores, similaridades)
        gks = next(iter(load("TCFPACN"+ "/FBTP/params/" + DATASET + '/Goalkeepers'))) #Goleiros


        abi_name_id, p_attrs_back, p_abis_name_back, p_pos_back, p_r_back, p_no_id_back = \
        PESpre.read_info(FILE_PATH, FILE_BACK)  # read backwards information
        sim_back = modules.cal_similarity('Back', p_attrs_back)  # calculate the similarity

        save("TCFPACN"+ "/FBTP/params/" + DATASET +'/info_back', {'abi_name_id':abi_name_id, 'p_attrs_back':p_attrs_back, 'p_abis_name_back':p_abis_name_back,'p_pos_back':p_pos_back, 'p_r_back':p_r_back, 'p_no_id_back':p_no_id_back}
            )
        save("TCFPACN"+ "/FBTP/params/" + DATASET +'/sim_back', {'sim_back':sim_back})
        abi_name_id, p_attrs_back, p_abis_name_back, p_pos_back, p_r_back, p_no_id_back = \
            load("TCFPACN"+ "/FBTP/params/" + DATASET + '/info_back')
        sim_back = next(iter(load("TCFPACN"+ "/FBTP/params/" + DATASET + '/sim_back')))
        abi_avg_back = modules.cal_ability_avg(p_abis_name_back)
        # get the network of back
        pg_back = greedy.players_graph_construction(sim_back, abi_avg_back, p_abis_name_back,
                                                    abi_name_id, p_pos_back, p_r_back
                                                    )

        # 3: the Forward/Midfielder network
        abi_name_id, p_attrs_forward, p_abis_name_forward, p_pos_forward, p_r_forward, p_no_id_forward = \
        PESpre.read_info(FILE_PATH, FILE_FORWARD)  # read forward/midfielder information
        sim_forward = modules.cal_similarity('Forward', p_attrs_forward)

        save("TCFPACN"+ "/FBTP/params/" + DATASET +'/info_forward', {'abi_name_id':abi_name_id, 'p_attrs_forward':p_attrs_forward,
                                                                'p_abis_name_forward':p_abis_name_forward, 'p_pos_forward':p_pos_forward,
                                                                'p_r_forward':p_r_forward, 'p_no_id_forward':p_no_id_forward
                                                                }
            )
        save("TCFPACN"+ "/FBTP/params/" + DATASET +'/sim_forward', {'sim_forward':sim_forward})
        abi_name_id, p_attrs_forward, p_abis_name_forward, p_pos_forward, p_r_forward, p_no_id_forward = \
            load("TCFPACN"+ "/FBTP/params/" + DATASET + '/info_forward')
        sim_forward = next(iter(load("TCFPACN"+ "/FBTP/params/" + DATASET +  '/sim_forward')))
        abi_avg_forward = modules.cal_ability_avg(p_abis_name_forward)
        pg_forward = greedy.players_graph_construction(sim_forward, abi_avg_forward, p_abis_name_forward,
                                                       abi_name_id, p_pos_forward, p_r_forward
                                                       )


    # Cálculo de médias de habilidades e construção dos grafos de jogadores (defesa e ataque/meio-campo)
    abi_avg_back = modules.cal_ability_avg(p_abis_name_back)
    pg_back = greedy.players_graph_construction(sim_back, abi_avg_back, p_abis_name_back, abi_name_id, p_pos_back, p_r_back)  # get the network of back

    abi_avg_forward = modules.cal_ability_avg(p_abis_name_forward)
    pg_forward = greedy.players_graph_construction(sim_forward, abi_avg_forward, p_abis_name_forward, abi_name_id, p_pos_forward, p_r_forward) # get the network of foward

    fbtp.FBTP(gks, abi_name_id, p_no_id_back, pg_back, cri_back, p_no_id_forward, pg_forward, cri_forward, BUDGET, ALPHA, BETA, DATASET)
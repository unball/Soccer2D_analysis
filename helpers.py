""" 
Módulo de análise de posse de bola, eventos e desempenho de jogadores em um jogo de futebol.
Funções:
    - possession_at: Determina qual lado (esquerdo ou direito) tem a posse da bola em um determinado ciclo do jogo.
    - define_player_possession: Determina qual jogador tem a posse da bola em um determinado ciclo.
    - kick: Verifica se um jogador chutou a bola em um determinado ciclo.
    - find_last_unique_event_ocurrences: Encontra as últimas ocorrências únicas de um evento em um DataFrame.
    - analyze_fouls: Analisa faltas cometidas durante o jogo e retorna as posições das faltas.
    - goals: Identifica os ciclos em que ocorreram gols e retorna os momentos dos gols.
    - analyze_goalkeeper: Analisa o desempenho do goleiro em relação aos gols sofridos.
    - analyze_stamina: Analisa a resistência dos jogadores ao longo do jogo.
"""

from typing import List, Tuple
import pandas as pd
import math

from geom_2d import Point, Circle, distance


# substituir
def possession_at(cycle: int, game: pd.DataFrame, players: List[List[Tuple[str, str]]]) -> str:
    """
    Determina qual lado (esquerdo ou direito) tem a posse da bola em um determinado ciclo do jogo.

    Args:
        cycle (int): O ciclo (passo de tempo) no jogo para verificar a posse.
        game (pd.DataFrame): Um DataFrame contendo os dados do jogo, incluindo as posições dos jogadores e da bola.
        players (List[List[Tuple[str, str]]]): Uma lista contendo duas listas de tuplas. Cada tupla contém 
                                            os nomes das colunas para as coordenadas x e y de um jogador.
                                            A primeira lista é para os jogadores do lado esquerdo, e a segunda 
                                            lista é para os jogadores do lado direito.

    Returns:
        str: "left" se o lado esquerdo tem a posse, "right" se o lado direito tem a posse.
    """

    # seleciona as colunas referentes aos jogadores ao time da esquerda
    # e ao time da direita
    players_left = players[0]
    players_right = players[1]

    # coordenadas da bola
    ball_x = game.loc[cycle, 'ball_x']
    ball_y = game.loc[cycle, 'ball_y']

    ball_position = Point(ball_x, ball_y)

    # inicializa variáveis
    closest_distance = 1000
    possession_side = closer_to_ball_side = ""

    for i in range(11):  # i-ésimo jogador é o jogador número (i + 1)

        # coordenadas do jogador 
        player_left_x = game.loc[cycle, players_left[i][0]]
        player_left_y = game.loc[cycle, players_left[i][1]]

        player_right_x = game.loc[cycle, players_right[i][0]]
        player_right_y = game.loc[cycle, players_right[i][1]]

        player_l_location = Point(player_left_x, player_left_y)
        player_r_location = Point(player_right_x, player_right_y)

        # calcula a distância do jogador até a bola
        player_l_distance = distance(player_l_location, ball_position)
        player_r_distance = distance(player_r_location, ball_position)

        # determina o jogador mais próximo da bola
        if player_l_distance < closest_distance:
            closest_distance = player_l_distance

            possession_side = "left"

        if player_r_distance < closest_distance:
            closest_distance = player_r_distance

            possession_side = "right"

        closer_to_ball_side = possession_side

    return closer_to_ball_side

def define_player_possession(cycle, player_left_position: Point, player_right_position: Point, 
                             players: List[List[Tuple[str, str]]], df: pd.DataFrame, player_who_possesses=False):

    """
    Determines which player has possession of the ball at a given cycle.

    Args:
        cycle (int): The current cycle or time step in the game.
        player_left_position (Point): The position of a player on the left team.
        player_right_position (Point): The position of a player on the right team.
        players (List[List[Tuple[str, str]]]): A list containing two lists of tuples. Each tuple contains the column names 
                                                for the x and y positions of the players in the DataFrame. The first list 
                                                is for the left team, and the second list is for the right team.
        df (pd.DataFrame): The DataFrame containing the positions of the players and the ball.
        player_who_possesses (bool, optional): If True, returns the team and the index of the player who possesses the ball. 
                                                Defaults to False.

    Returns:
        str or tuple: If player_who_possesses is False, returns 'left' or 'right' indicating which team has possession, 
                        or None if no player has possession. If player_who_possesses is True, returns a tuple where the first 
                        element is 'left' or 'right' and the second element is the index of the player who possesses the ball, 
                        or (None, -1) if no player has possession.
    """

    # constant
    player_influence_radius = 0.7

    # players columns
    players_left = players[0]
    players_right = players[1]

    ball_position = Point(df.loc[cycle, 'ball_x'], df.loc[cycle, 'ball_y'])

    ball_zone = Circle(player_influence_radius, ball_position)

    # 10 players only because goalkeeper is not checked in this analysis
    for i in range(1, 11):
        player_left_position.x = df.loc[cycle, players_left[i][0]]
        player_left_position.y = df.loc[cycle, players_left[i][1]]

        # left player has the ball
        if ball_zone.is_inside(player_left_position):
            if player_who_possesses:
                return 'left', i+2
            return 'left'

        player_right_position.x = df.loc[cycle, players_right[i][0]]
        player_right_position.y = df.loc[cycle, players_right[i][1]]

        # right player has the ball
        if ball_zone.is_inside(player_right_position):
            if player_who_possesses:
                return 'right', i+2
            return 'right'
    
    # neutral possession
    if player_who_possesses:
        return None, -1
    
    return None

def kick(cycle, team, df, player_who_kicked=False):
    """
    Determines if a player of the specified team has kicked the ball

    Args: 
        cycle (int): The current cycle or time step in the game.
        team (string): The analysed team
        df (pd.DataFrame): The dataset of the game
        player_who_kicked (bool): Indicates if it's needed to retur the number of the player 
                                who has kicked the ball  
    Returns:
        bool: , if a kick has occurred or not
        int: the number of the player who has kicked the ball if player_who_kicked == True
    """
    for player_num in range(1,12):
        if cycle != 0:
            if df[f"player_{team}{player_num}_counting_kick"][cycle] > df[f'player_{team}{player_num}_counting_kick'][cycle-1]:
                    if player_who_kicked == True:
                        return True, player_num
                    else:
                        return True
    if player_who_kicked == True:
        return False, -1
    else:
        return False
    
def find_last_unique_event_ocurrences(dataframe, event):
    """
    Find the indices of the last unique occurrences of a specified event in a DataFrame.
    This function iterates through the rows of the given DataFrame and identifies the indices
    where the specified event occurs for the last time in a sequence of consecutive occurrences.

    Args:
        dataframe (pandas.DataFrame): The DataFrame to search through. It is assumed that the event
                                      information is located in the second column (index 1) of the DataFrame.
        event (str): The event to search for in the DataFrame.
    Returns:
        list: A list of indices where the specified event occurs for the last time in a sequence of
              consecutive occurrences.
    """

    event_ocurrences_index = []
    for i in range(len(dataframe)):
        if(event in dataframe.iloc[i, 1] and event not in dataframe.iloc[i - 1, 1]):
            while dataframe.iloc[i, 1] == event:
                i += 1
                if dataframe.iloc[i, 1] != event:
                    event_ocurrences_index.append(i)

    return event_ocurrences_index

def analyze_fouls(dataframe: pd.DataFrame):
    """
    Analyzes the fouls in the given dataframe and returns the coordinates of the fouls.
    For every cycle in the log, this function investigates whether a foul happened and 
    updates one of the lists if it is the case.

    Args:
        dataframe (pd.DataFrame): A pandas DataFrame containing the log data with columns 
                                  'playmode', 'ball_x', and 'ball_y'.
    Returns:
        tuple: A tuple containing two lists:
            - left_charges (list of Point): List of coordinates (as Point objects) where 
                                            'foul_charge_l' occurred.
            - right_charges (list of Point): List of coordinates (as Point objects) where 
                                             'foul_charge_r' occurred.
    """
    
    left_charges = []
    right_charges = []

    for i in range(len(dataframe)):
        if (dataframe.loc[i, 'playmode'] == 'foul_charge_l' 
                and dataframe.loc[i - 1, 'playmode'] != 'foul_charge_l'):

            left_charges.append(Point(int(dataframe.loc[i, 'ball_x']),
                                        int(dataframe.loc[i, 'ball_y'])))

        elif (dataframe.loc[i, 'playmode'] == 'foul_charge_r'
                and dataframe.loc[i - 1, 'playmode'] != 'foul_charge_r'):

            right_charges.append(Point(int(dataframe.loc[i, 'ball_x']),
                                        int(dataframe.loc[i, 'ball_y']))) 
            
    
    return left_charges, right_charges


def goals(dataframe: pd.DataFrame, team=None) -> None:
    """
    Finds out at which cycles a goal happened and populates goal_moments.

    if the team is specified, the cycles of each of this team's goals is returned 

    Args:
        dataframe (pd.DataFrame): The dataframe containing the play data.
        team (str, optional): The team for which to return goal cycles. 
                          Can be "team_l" for the left team or "team_r" for the right team.
                          If not specified, returns goal cycles for both teams.
    Returns:
        list: A list of indices where goals occurred. If a team is specified, 
          returns the indices of goals for that team only.
    """
    
    goal_moments = []
    left_team_goals = []
    right_team_goals = []

    filtered_dataframe = dataframe.loc[(dataframe['playmode'] == "goal_l") |
                                            (dataframe['playmode'] == "goal_r")]
    
    for index, row in filtered_dataframe.iterrows():
        if (dataframe.iloc[index - 1]['playmode'] != row['playmode']):
            # Goal happened
            goal_moments.append(index)

            if (row['playmode'] == "goal_l"):
                left_team_goals.append(index)
            else:
                right_team_goals.append(index)

    if team == "team_l":
        return left_team_goals
    elif team == "team_r":
        return right_team_goals
    else:
        return goal_moments

def analyze_goalkeeper(dataframe, players: List[List[Tuple[str, str]]], team: str) -> None:
    """"
    Analyzes the goalkeeper's performance for a specified team by examining the positions
    of the ball and the goalkeeper during enemy goals.
    
    Args:
        dataframe : pandas.DataFrame
            The dataframe containing match data.
        players : List[List[Tuple[str, str]]]
            A nested list containing tuples of player positions. The first list contains the 
            positions of the left team players, and the second list contains the positions of 
            the right team players. Each tuple contains the x and y coordinates as strings.
        team : str
            The name of the team for which the goalkeeper's performance is being analyzed.
    
    Returns:
        catches : int
            The number of catches made by the goalkeeper.
        adversary_goal_quantity : int
            The number of goals scored by the adversary team.
        distances : List[float]
            A list of distances between the ball and the goalkeeper at the time of each goal.
        ball_positions : List[shapely.geometry.Point]
            A list of ball positions at the time of each goal.
        goalie_positions : List[shapely.geometry.Point]
            A list of goalkeeper positions at the time of each goal.
            For each enemy goal, consults the dataframe and populates goalie_positions, 
            ball_positions and distances of the goalie from the ball for the specified team.
    """
    # declare variables
    ball_positions = []
    goalie_positions = []
    distances = []
    enemy_team = ""
    # average_distance = 0
    # max_distance = 0
    
    # get goalie position
    goalie_left_x = players[0][0][0]
    goalie_left_y = players[0][0][1]

    goalie_right_x = players[1][0][0]
    goalie_right_y = players[1][0][1]
    
    left_team_name = dataframe.iloc[0]["team_name_l"]

    if (left_team_name == team):
        enemy_team = "right"

        catches = dataframe.iloc[len(dataframe) - 1]["player_l1_counting_catch"]

    else:
        enemy_team = "left"

        catches = dataframe.iloc[len(dataframe) - 1]["player_r1_counting_catch"]

    # get the quantity of enemy's goals
    enemy_goals = goals(dataframe, enemy_team)

    for goal_moment in enemy_goals:
        ball_x = dataframe.iloc[goal_moment]["ball_x"]
        ball_y = dataframe.iloc[goal_moment]["ball_y"]

        ball_pos = Point(ball_x, ball_y)

        ball_positions.append(ball_pos)

        goalie_x = None
        goalie_y = None

        if (enemy_team == "left"):
            goalie_x = goalie_left_x
            goalie_y = goalie_left_y

            goalie_x = dataframe.iloc[goal_moment][goalie_x]
            goalie_y = dataframe.iloc[goal_moment][goalie_y]

        else:
            goalie_x = goalie_right_x
            goalie_y = goalie_right_y

            goalie_x = dataframe.iloc[goal_moment][goalie_x]
            goalie_y = dataframe.iloc[goal_moment][goalie_y]

        goalie_pos = Point(goalie_x, goalie_y)

        goalie_positions.append(goalie_pos)

        # distance of the goalie to the ball
        dist = distance(ball_pos, goalie_pos)

        distances.append(dist)

        # average_distance += dist
        
        # if (dist > max_distance):
        #     max_distance = dist
    
    adversary_goal_quantity = max(1, len(enemy_goals))
    # average_distance = average_distance / adversary_goal_quantity

    return catches, adversary_goal_quantity, distances, ball_positions, goalie_positions 

def analyze_stamina(dataframe: pd.DataFrame):
    """
    Analyzes the stamina attributes of players from a given DataFrame.
    This function extracts the stamina attributes for players on the left and right teams
    from the provided DataFrame. It assumes that the DataFrame contains columns named
    'player_l1_attribute_stamina' to 'player_l11_attribute_stamina' for the left team
    and 'player_r1_attribute_stamina' to 'player_r11_attribute_stamina' for the right team.
    
    Args:
        dataframe (pd.DataFrame): The DataFrame containing the stamina attributes of players.
    Returns:
        tuple: A tuple containing two lists:
            - l_players_stamina (list): A list of lists, where each inner list contains the stamina
            values for each player on the left team.
            - r_players_stamina (list): A list of lists, where each inner list contains the stamina
            values for each player on the right team.
    """

    players_l_stamina_attr = []
    players_r_stamina_attr = []
    
    for i in range(1, 12):
        players_l_stamina_attr.append(f'player_l{i}_attribute_stamina')
        players_r_stamina_attr.append(f'player_r{i}_attribute_stamina')

    l_players_stamina = []
    r_players_stamina = []
    
    for stamina_attr in players_l_stamina_attr:
        l_players_stamina.append(dataframe[stamina_attr].tolist())

    for stamina_attr in players_r_stamina_attr:
        r_players_stamina.append(dataframe[stamina_attr].tolist())

    return l_players_stamina, r_players_stamina
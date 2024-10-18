from typing import List, Tuple
import pandas as pd
import math

from geom_2d import Point, Circle, distance

def possession_at(cycle: int, game: pd.DataFrame, players: List[List[Tuple[str, str]]]) -> str:
  players_left = players[0]
  players_right = players[1]

  # coordenadas da bola
  ball_x = game.loc[cycle, 'ball_x']
  ball_y = game.loc[cycle, 'ball_y']

  ball_position = Point(ball_x, ball_y)

  closest_distance = 1000
  possession_side = closer_to_ball_side = ""

  for i in range(0, 11):  # ith player is player_unum(i + 1)

      player_left_x = game.loc[cycle, players_left[i][0]]
      player_left_y = game.loc[cycle, players_left[i][1]]

      player_right_x = game.loc[cycle, players_right[i][0]]
      player_right_y = game.loc[cycle, players_right[i][1]]

      player_l_location = Point(player_left_x, player_left_y)
      player_r_location = Point(player_right_x, player_right_y)

      player_l_distance = distance(player_l_location, ball_position)
      player_r_distance = distance(player_r_location, ball_position)

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
    player_influence_radius = 0.7

    # global for a while
    players_left = players[0]
    players_right = players[1]

    # df global for a while
    ball_position = Point(df.loc[cycle, 'ball_x'], df.loc[cycle, 'ball_y'])

    ball_zone = Circle(player_influence_radius, ball_position)

    # 10 players only because goalkeeper is not checked in this analysis
    for i in range(1, 11):
        player_left_position.x = df.loc[cycle, players_left[i][0]]
        player_left_position.y = df.loc[cycle, players_left[i][1]]

        if ball_zone.is_inside(player_left_position):
            if player_who_possesses:
                return 'left', i+2
            return 'left'

        player_right_position.x = df.loc[cycle, players_right[i][0]]
        player_right_position.y = df.loc[cycle, players_right[i][1]]

        if ball_zone.is_inside(player_right_position):
            if player_who_possesses:
                return 'right', i+2
            return 'right'
    if player_who_possesses:
        return None, -1
    return None

def kick(cycle, team, df, player_who_kicked=False):
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
    
def find_last_unique_event_ocurrences(dataframe, event): # probably inefficient ? O(n)
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
        For every cycle in the log, investigates wether a fault happened and 
        updates one of the lists if it is really the case.
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
    """
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

        dist = distance(ball_pos, goalie_pos)

        distances.append(dist)

        # average_distance += dist
        
        # if (dist > max_distance):
        #     max_distance = dist
    
    adversary_goal_quantity = max(1, len(enemy_goals))
    # average_distance = average_distance / adversary_goal_quantity

    return catches, adversary_goal_quantity, distances, ball_positions, goalie_positions 

def analyze_stamina(dataframe: pd.DataFrame):

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
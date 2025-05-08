
import re
import pandas as pd
import numpy as np
from tqdm.auto import tqdm




# Preprocessing
def preprocess_value(value):
    if len(value) >= 1:
        value = value[0]
    else:
        value = 0
        # raise Exception(f'{url}\n{value}')
    if isinstance(value, str) and ("m" in value or "s" in value):
        minutes = 0
        seconds = 0
        match = re.search(r'(\d+)\s*m', value)
        if match:
            minutes = int(match.group(1))
        match = re.search(r'(\d+)\s*s', value)
        if match:
            seconds = int(match.group(1))
        value = minutes * 60 + seconds
    if isinstance(value, str) and "%" in value:
        return round(float(value.replace('%', '')) / 100, 2)
    elif value == "-":
        return 0
    else:
        return float(value)
    
def parse_player_stats(tree):
    player_stats_dict = {

        # Main
        'main_rating_1_0': preprocess_value(tree.xpath("(//div[@class='summaryStatBreakdownDataValue'])[1]/text()")),
        'main_dpr': preprocess_value(tree.xpath("(//div[@class='summaryStatBreakdownDataValue'])[2]/text()")),
        'main_kast': preprocess_value(tree.xpath("(//div[@class='summaryStatBreakdownDataValue'])[3]/text()")),
        'main_impact': preprocess_value(tree.xpath("(//div[@class='summaryStatBreakdownDataValue'])[4]/text()")),
        'main_adr': preprocess_value(tree.xpath("(//div[@class='summaryStatBreakdownDataValue'])[5]/text()")),
        'main_kpr': preprocess_value(tree.xpath("(//div[@class='summaryStatBreakdownDataValue'])[6]/text()")),

        # Firepower
        'firepower': preprocess_value(tree.xpath("(//div[@class='row-stats-section-score'])[1]/text()")),
        'firepower_kills_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[1]/text()")),
        'firepower_kills_per_round_win': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[7]/text()")),
        'firepower_damage_per_round_win': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[19]/text()")),
        'firepower_rounds_with_a_kill': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[4]/text()")),
        'firepower_rounds_with_a_multi_kill': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[16]/text()")),
        'firepower_pistol_round_rating': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[22]/text()")),

        # Entrying
        'entrying': preprocess_value(tree.xpath("(//div[@class='row-stats-section-score'])[4]/text()")),
        'entrying_saved_by_teammate_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[25]/text()")),
        'entrying_traded_death_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[28]/text()")),
        'entrying_traded_deaths_percentage': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[31]/text()")),
        'entrying_opening_deaths_traded_percantage': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[34]/text()")),
        'entrying_assists_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[37]/text()")),
        'entrying_support_rounds': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[40]/text()")),

        # Trading
        'trading': preprocess_value(tree.xpath("(//div[@class='row-stats-section-score'])[7]/text()")),
        'trading_saved_teammate_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[43]/text()")),
        'trading_trade_kills_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[46]/text()")),
        'trading_trade_kills_percentage': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[49]/text()")),
        'trading_assisted_kills_percentage': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[52]/text()")),
        'trading_damage_per_kill': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[55]/text()")),

        # Opening
        'opening': preprocess_value(tree.xpath("(//div[@class='row-stats-section-score'])[10]/text()")),
        'opening_kills_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[58]/text()")),
        'opening_deaths_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[61]/text()")),
        'opening_attempts': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[64]/text()")),
        'opening_success': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[67]/text()")),
        'opening_win_percentage_after_opening_kill': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[70]/text()")),
        'opening_attacks_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[73]/text()")),

        # Clutching
        'clutching': preprocess_value(tree.xpath("(//div[@class='row-stats-section-score'])[13]/text()")),
        'clutching_clutch_points_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[76]/text()")),
        'clutching_last_alive_percentage': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[79]/text()")),
        'clutching_one_on_one_win_percentage': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[82]/text()")),
        'clutching_time_alive_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[85]/text()")),
        'clutching_saves_per_round_loss': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[88]/text()")),

        # Sniping
        'sniping': preprocess_value(tree.xpath("(//div[@class='row-stats-section-score'])[16]/text()")),
        'sniping_sniper_kills_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[91]/text()")),
        'sniping_sniper_kills_percentage': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[94]/text()")),
        'sniping_rounds_with_sniper_kills_percentage': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[97]/text()")),
        'sniping_sniper_multi_kill_rounds': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[100]/text()")),
        'sniping_sniper_opening_kills_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[103]/text()")),

        # Utility
        'utility': preprocess_value(tree.xpath("(//div[@class='row-stats-section-score'])[19]/text()")),
        'utility_damage_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[106]/text()")),
        'utility_kills_per_100_rounds': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[109]/text()")),
        'utility_flashed_thrown_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[112]/text()")),
        'utility_flash_assists_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[115]/text()")),
        'utility_time_opponent_flashed_per_round': preprocess_value(tree.xpath("(//div[@class='role-stats-data'])[118]/text()")),

        # Statistics
        'statistics_total_kills': preprocess_value(tree.xpath("(//div[@class='stats-row']/span[2])[1]/text()")),
        'statistics_headshot_percentage': preprocess_value(tree.xpath("(//div[@class='stats-row']/span[2])[2]/text()")),
        'statistics_total_deaths': preprocess_value(tree.xpath("(//div[@class='stats-row']/span[2])[3]/text()")),
        'statistics_kd_ratio': preprocess_value(tree.xpath("(//div[@class='stats-row']/span[2])[4]/text()")),
        'statistics_damage_per_round': preprocess_value(tree.xpath("(//div[@class='stats-row']/span[2])[5]/text()")),
        'statistics_grenade_damage_per_round': preprocess_value(tree.xpath("(//div[@class='stats-row']/span[2])[6]/text()")),
        'statistics_maps_played': preprocess_value(tree.xpath("(//div[@class='stats-row']/span[2])[7]/text()")),
        'statistics_rounds_played': preprocess_value(tree.xpath("(//div[@class='stats-row']/span[2])[8]/text()")),
        'statistics_assists_per_round': preprocess_value(tree.xpath("(//div[@class='stats-row']/span[2])[10]/text()")),
        'statistics_deaths_per_round': preprocess_value(tree.xpath("(//div[@class='stats-row']/span[2])[11]/text()")),
        'statistics_saved_by_teammate_per_round': preprocess_value(tree.xpath("(//div[@class='stats-row']/span[2])[12]/text()")),
        'statistics_saved_teammates_per_round': preprocess_value(tree.xpath("(//div[@class='stats-row']/span[2])[13]/text()")),

    }

    return player_stats_dict


def parse_players(tree):
    players_id: list = []
    players_name: list = []
    for i in range(1, 11):
        players_id.append(tree.xpath(f"(//td[@class='player']//div[contains(@class, 'flagAlign')])[{i}]/@data-player-id")[0])
        players_name.append(tree.xpath(f"(//td[@class='player']//div[contains(@class, 'flagAlign')]//div[@class='text-ellipsis'])[{i}]/text()")[0])
    df_match = pd.DataFrame([{
        "team_0_player_1": players_name[0],
        "team_0_player_2": players_name[1],
        "team_0_player_3": players_name[2],
        "team_0_player_4": players_name[3],
        "team_0_player_5": players_name[4],
        "team_1_player_1": players_name[5],
        "team_1_player_2": players_name[6],
        "team_1_player_3": players_name[7],
        "team_1_player_4": players_name[8],
        "team_1_player_5": players_name[9],
    }])

    return players_id, players_name, df_match

def create_df_players():
    return pd.DataFrame(columns=[
        "player_link",
        "main_rating_1_0",
        "main_dpr",
        "main_kast",
        "main_impact",
        "main_adr",
        "main_kpr",
        "firepower",
        "firepower_kills_per_round",
        "firepower_kills_per_round_win",
        "firepower_damage_per_round_win",
        "firepower_rounds_with_a_kill",
        "firepower_rounds_with_a_multi_kill",
        "firepower_pistol_round_rating",
        "entrying",
        "entrying_saved_by_teammate_per_round",
        "entrying_traded_death_per_round",
        "entrying_traded_deaths_percentage",
        "entrying_opening_deaths_traded_percantage",
        "entrying_assists_per_round",
        "entrying_support_rounds",
        "trading",
        "trading_saved_teammate_per_round",
        "trading_trade_kills_per_round",
        "trading_trade_kills_percentage",
        "trading_assisted_kills_percentage",
        "trading_damage_per_kill",
        "opening",
        "opening_kills_per_round",
        "opening_deaths_per_round",
        "opening_attempts",
        "opening_success",
        "opening_win_percentage_after_opening_kill",
        "opening_attacks_per_round",
        "clutching",
        "clutching_clutch_points_per_round",
        "clutching_last_alive_percentage",
        "clutching_one_on_one_win_percentage",
        "clutching_time_alive_per_round",
        "clutching_saves_per_round_loss",
        "sniping",
        "sniping_sniper_kills_per_round",
        "sniping_sniper_kills_percentage",
        "sniping_rounds_with_sniper_kills_percentage",
        "sniping_sniper_multi_kill_rounds",
        "sniping_sniper_opening_kills_per_round",
        "utility",
        "utility_damage_per_round",
        "utility_kills_per_100_rounds",
        "utility_flashed_thrown_per_round",
        "utility_flash_assists_per_round",
        "utility_time_opponent_flashed_per_round",
        "statistics_total_kills",
        "statistics_headshot_percentage",
        "statistics_total_deaths",
        "statistics_kd_ratio",
        "statistics_damage_per_round",
        "statistics_grenade_damage_per_round",
        "statistics_maps_played",
        "statistics_rounds_played",
        "statistics_assists_per_round",
        "statistics_deaths_per_round",
        "statistics_saved_by_teammate_per_round",
        "statistics_saved_teammates_per_round",
    ])

def get_df_players(
    row_match: pd.DataFrame, 
    df_players: pd.DataFrame,
):
    
    row_match = row_match.to_frame().T

    team_players = []
    for team in range(0, 2):
        team_players.append([])
        for player in range(1, 6):
            player_link = row_match[f'team_{team}_player_{player}'].iloc[0]
            df_player = df_players[df_players['player_link'] == player_link]
            team_players[team].append(df_player)

    return team_players

def preprocess_players(
    df_players: pd.DataFrame,
    mean_player: pd.DataFrame,
):
    # AXX
    df_start = df_players
    df_players_AXX = df_start.copy()

    # 1. Считаем процент пропусков по строкам
    row_nan_percent = df_players_AXX.isna().mean(axis=1)

    # 2. Находим индексы строк, где пропусков > 25%
    rows_to_replace = row_nan_percent > 0.25

    # 3. Заменяем такие строки на mean_player
    df_players_AXX.loc[rows_to_replace] = mean_player.values

    # AAX
    df_start = df_players_AXX
    df_players_AAX = df_start.copy()

    df_players_AAX.loc[df_players['clutching_time_alive_per_round'] > 500, 'clutching_time_alive_per_round'] = 70

    # AAA
    df_start = df_players_AAX
    df_players_AAA = df_start.copy()
    df_players_AAA = df_players_AAA.drop(columns=['main_impact',
        'main_adr',
        'main_kpr',
        'firepower_kills_per_round',
        'firepower_rounds_with_a_kill',
        'firepower_rounds_with_a_multi_kill',
        'entrying_traded_death_per_round',
        'entrying_traded_deaths_percentage',
        'trading_trade_kills_per_round',
        'opening_kills_per_round',
        'sniping_sniper_kills_per_round',
        'sniping_sniper_kills_percentage',
        'sniping_rounds_with_sniper_kills_percentage',
        'sniping_sniper_multi_kill_rounds',
        'sniping_sniper_opening_kills_per_round',
        'statistics_total_deaths',
        'statistics_kd_ratio',
        'statistics_maps_played',
        'statistics_rounds_played',
        'statistics_assists_per_round',
        'statistics_deaths_per_round',
        'statistics_saved_by_teammate_per_round',
        'statistics_saved_teammates_per_round',
    ])

    return df_players_AAA

def merge_zero_mean(
    row_match,
    df_players,
):
    team_players = get_df_players(row_match, df_players)

    row_team_1 = pd.concat(team_players[0], ignore_index=True)
    row_team_2 = pd.concat(team_players[1], ignore_index=True)

    row_team_1 = row_team_1.drop(columns=row_team_1.select_dtypes(include=['object', 'string']).columns)
    row_team_2 = row_team_2.drop(columns=row_team_2.select_dtypes(include=['object', 'string']).columns)

    row_teams_merged = row_team_2.mean().to_frame().T - row_team_1.mean().to_frame().T

    filter_columns = [
        'match_link',
        'match_type',
        'team_winner',
        'team_0_score',
        'team_1_score',
        'team_0_player_1',
    ]

    final_columns = [column for column in filter_columns if column in row_match.to_frame().T.columns]
    row_match_filtered = row_match.to_frame().T[final_columns]

    row_result = pd.concat([
        row_match_filtered.reset_index(drop=True), 
        row_teams_merged.reset_index(drop=True),
        ], 
        axis=1,
    )

    return row_result.squeeze()

def merge_data(
    df_match: pd.DataFrame,
    df_players: pd.DataFrame,
):
    df_merged = df_match.apply(merge_zero_mean, axis=1, df_players=df_players)
    return df_merged
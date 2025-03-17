import pandas as pd
from django.core.management import BaseCommand

from hbl.models import HBLTeam
from hbl.models.players import HBLPlayer

teams = ['CS', 'AC', 'LG', 'JWC', 'JBB', 'WG', 'TSJ', 'MGWB', 'DSL', 'BotLC']

class Command(BaseCommand):
    help = "Calls the yahoo api to get the teams for initial db"

    def add_arguments(self, parser):
        parser.add_argument("xl_file", type=str)
        parser.add_argument(
            "-t",
            "--team_id",
            type=str,
            help="Team id for importing one team only",
        )
        parser.add_argument("-d", "--dry_run", action="store_true")

    def handle(self, *args, **kwargs):
        xls = pd.ExcelFile(kwargs["xl_file"])
        if 'team_id' in kwargs and kwargs['team_id'] is not None:
            teams = kwargs["team_id"]
        for team in teams:
            df = pd.read_excel(xls, team)
            curr_df = df.iloc[:, 0:3]
            player_array = []
            hbl_team = HBLTeam.objects.get(name=team)
            for idx, row in curr_df.iterrows():
                keep, cost, name = row.iloc[0], row.iloc[1], row.iloc[2]
                if not name:
                    break
                if keep != 1:
                    continue
                name_split = name.split(" ")
                first_name = name_split[0]
                last_name = " ".join(name_split[1:])
                player = HBLPlayer(
                    first_name=first_name, last_name=last_name, keeper_cost_current=cost, hbl_team=hbl_team
                )
                if 'dry_run' in kwargs:
                    print(player)
                player_array.append(player)
            if not kwargs['dry_run']:
                HBLPlayer.objects.bulk_create(player_array)
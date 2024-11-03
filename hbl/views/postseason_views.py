import logging

import xmltodict
from decouple import config
from rest_framework.views import APIView

from hbl.models import HBLPlayer, HBLTeam
from hbl.views.auth_views import yahoo_oauth

logger = logging.getLogger(__name__)

class DownloadTeams(APIView):
    def get(self, request):
        for team_id in range(1,11):
            team_response_xml = yahoo_oauth.get(f'{config("YAHOO_SPORTS_API")}/team/{config("YAHOO_GAME_ID")}.l.{config("YAHOO_HBL_ID")}.t.{team_id}')
            team_response_dict = xmltodict.parse(team_response_xml.text)
            logger.info(f'Downloading team {team_response_dict["team"]["name"]}')
            hbl_team = HBLTeam.objects.get(name=team_response_dict['team']['name'])
            current_roster = HBLPlayer.objects.filter(hbl_team__name=hbl_team.name)
            current_roster_ids = set(current_roster.values_list('yahoo_player_id', flat=True))

            roster = team_response_dict['team']['roster']['players']
            roster_ids = set()
            for player in roster:
                roster_ids.add(player['player_key'])
                if player['player_key'] not in current_roster_ids:
                    try:
                        hbl_player = HBLPlayer.objects.get(yahoo_player_id=player['player_key'])
                        hbl_player.previous_hbl_team = hbl_player.hbl_team
                        hbl_player.hbl_team = hbl_team
                        hbl_player.save()
                    except HBLPlayer.DoesNotExist:
                        logger.info(f'Adding {player["name"]["first"]} {player["name"]["last"]} to db')
                        hbl_player = HBLPlayer.objects.create(
                            first_name=player['name']['first'],
                            last_name=player['name']['last'],
                            yahoo_player_id=player['player_key'],
                            team_name=player['editorial_team_full_name'],
                            primary_position=player['primary_position'],
                            display_positions=player['display_position'],
                            hbl_team=HBLTeam.objects.get(name=team_response_dict['team']['name'])
                        )
            for roster_id in current_roster_ids:
                if roster_id not in roster_ids:
                    hbl_player = HBLPlayer.objects.get(yahoo_player_id=roster_id)
                    hbl_player.previous_hbl_team = hbl_player.hbl_team
                    hbl_player.hbl_team = None
                    hbl_player.save()
            logger.info(f'{team_response_dict["team"]["name"]} finished.')
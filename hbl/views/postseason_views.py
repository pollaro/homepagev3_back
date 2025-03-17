import logging

import xmltodict
from decouple import config
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.views import APIView

from hbl.models import HBLPlayer, HBLProspect, HBLTeam
from hbl.views.auth_views import yahoo_oauth

logger = logging.getLogger(__name__)


class PostSeasonView(APIView):
    def get(self, request):
        hbl_teams = HBLTeam.objects.all().prefetch_related('players', 'manager').annotate(player_count=Count('players', distinct=True), prospect_count=Count('prospects', distinct=True))
        teams_response = []
        for team in hbl_teams:
            teams_response.append({
                'name': HBLTeam.HBLTeamNames(team.name).label,
                'manager': team.manager.name,
                'player_count': team.player_count,
                'prospect_count': team.prospect_count,
            })
        return Response(teams_response)


class DownloadTeams(APIView):
    def get(self, request):
        roster_information = []
        for team_id in range(1,11):
            team_response_xml = yahoo_oauth.get(f'{config("YAHOO_SPORTS_API")}/team/{config("YAHOO_GAME_ID")}.l.{config("YAHOO_HBL_ID")}.t.{team_id}/roster')
            team_response_dict = xmltodict.parse(team_response_xml.text)
            team_response_dict = team_response_dict['fantasy_content']
            logger.info(f'Downloading team {team_response_dict["team"]["name"]}')
            try:
                hbl_team = HBLTeam.objects.get(yahoo_team_id=team_id)
            except HBLTeam.DoesNotExist:
                raise Exception(f'Team {team_response_dict["team"]["name"]} not found in database')
            current_roster = HBLPlayer.objects.filter(hbl_team__name=hbl_team.name)
            current_roster_ids = set(current_roster.values_list('yahoo_player_id', flat=True))

            roster = team_response_dict['team']['roster']['players']
            roster_ids = set()
            create_players = []
            for player in roster['player']:
                roster_ids.add(player['player_key'])
                if player['player_key'] not in current_roster_ids:
                    try:
                        logger.info(f'Updating {player["name"]["first"]} {player["name"]["last"]}')
                        hbl_player = HBLPlayer.objects.get(yahoo_player_id=player['player_key'])
                        hbl_player.previous_hbl_team = hbl_player.hbl_team
                        hbl_player.hbl_team = hbl_team
                        hbl_player.save()
                    except HBLPlayer.DoesNotExist:
                        logger.info(f'Adding {player["name"]["first"]} {player["name"]["last"]} to db')
                        hbl_player = HBLPlayer(
                            first_name=player['name']['first'],
                            last_name=player['name']['last'],
                            yahoo_player_id=player['player_key'],
                            team_name=player['editorial_team_full_name'],
                            primary_position=player['primary_position'],
                            display_positions=player['display_position'],
                            hbl_team=HBLTeam.objects.get(yahoo_team_id=team_id)
                        )
                        create_players.append(hbl_player)

            if len(create_players) > 0:
                HBLPlayer.objects.bulk_create(create_players)
            roster_information.append({
                'team': hbl_team.name,
                'manager': hbl_team.manager.name,
                'players': len(roster_ids),
                'prospects': HBLProspect.objects.filter(hbl_team=hbl_team).count()
            })

            for roster_id in current_roster_ids:
                if roster_id not in roster_ids:
                    hbl_player = HBLPlayer.objects.get(yahoo_player_id=roster_id)
                    hbl_player.previous_hbl_team = hbl_player.hbl_team
                    hbl_player.hbl_team = None
                    hbl_player.save()
            logger.info(f'{team_response_dict["team"]["name"]} finished.')
        return Response(roster_information)
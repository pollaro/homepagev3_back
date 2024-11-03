import xmltodict
from decouple import config
from rest_framework.views import APIView

from hbl.models import HBLAddPlayer, HBLDropPlayer, HBLPlayer, HBLTeam, HBLTrade, HBLTransaction
from hbl.views.auth_views import yahoo_oauth


class ProcessTransactionsView(APIView):
    def get(self, request):
        transaction_response_xml = yahoo_oauth.get(f'{config("YAHOO_SPORTS_API")}/transaction')
        transaction_response_dict = xmltodict.parse(transaction_response_xml.text)
        transactions = transaction_response_dict['fantasy_content']['league']['transactions']

        last_transaction = HBLTransaction.objects.order_by('transaction_id')[-1]
        last_transaction_id = last_transaction.transaction_id
        new_transactions = []
        for idx, transaction in enumerate(transactions):
            if transaction['transaction_id'] == last_transaction_id:
                last_transaction_index = idx # These come in backwards, so we want up to idx
                new_transactions = transactions[:last_transaction_index]
                break
        if not new_transactions:
            return
        
        for transaction in new_transactions:
            for player in transaction['players']:
                try:
                    hbl_player = HBLPlayer.objects.get(yahoo_player_id=player['player_key'])
                except HBLPlayer.DoesNotExist:
                    hbl_player = HBLPlayer.objects.create(
                        first_name=player['name']['first'],
                        last_name=player['name']['last'],
                        display_positions=player['display_position'],
                        team_name=player['editorial_team_abbr'],
                        yahoo_player_id=player['player_key'],
                    )
            if transaction['type'] == 'trade':
                    source_team = HBLTeam.objects.get(yahoo_team_id=player['transaction_data']['source_team_key'])
                    destination_team = HBLTeam.objects.get(yahoo_team_id=player['transaction_data']['destination_team_key'])
                    HBLTrade.objects.create(
                        player = hbl_player,
                        source_team = source_team,
                        destination_team = destination_team,
                        date=transaction['timestamp'],
                        transaction_id=transaction['transaction_id'],
                    )
            else:
                hbl_add = None
                if player['transaction_data']['type'] == 'add':
                    hbl_add = HBLAddPlayer.objects.create(
                        transaction_id=transaction['transaction_id'],
                        player=hbl_player,
                        hbl_team=HBLTeam.objects.get(
                            yahoo_team_id=player['transaction_data']['destination_team_key']
                        ),
                        waiver=False if player['transaction_data']['source_type'] == 'freeagents' else True,
                        date=transaction['timestamp']
                    )
                if transaction['type'] == 'drop' or transaction['type'] == 'add/drop':
                    HBLDropPlayer.objects.create(
                        transaction_id=transaction['transaction_id'],
                        player=hbl_player,
                        hbl_team=HBLTeam.objects.get(
                            yahoo_team_id=player['transaction_data']['destination_team_key']
                        ),
                        date=transaction['timestamp'],
                        add=hbl_add
                    )
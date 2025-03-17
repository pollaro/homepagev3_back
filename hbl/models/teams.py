from decouple import config
from django.db import models

from hbl.models.managers import HBLManager


class HBLTeam(models.Model):
    class HBLTeamNames(models.TextChoices):
        ARGON_CONCLUSIONS = 'AC', 'Argon Conclusions'
        BOTTOM_OF_THE_LINEUP_CARD = 'BotLC', 'Bottom of the Lineup Card'
        CVILLE_STRANGERS = 'CS', 'C-ville Strangers'
        DIGITAL_SPACE_LOOP = 'DSL', 'Digital Space Loop'
        JAY_AND_BOBS_BOYS = 'JBB', 'Jay and Bobs Boys'
        JIM_WOHLFORD_CLONES = 'JWC', 'Jim Wohlford Clones'
        LITTLE_GIANTS_II = 'LGII', 'Little Giants II'
        MGS_WONDERBOYS = 'MGWB', "MG's WonderBoys"
        THE_STORAGE_JARS = 'SJ', 'THE STORAGE JARS'
        WABASH_GOATS = 'WG', 'Wabash Goats'

    name = models.CharField(max_length=25, choices=HBLTeamNames)
    yahoo_team_id = models.CharField(max_length=20)
    manager = models.ForeignKey(
        HBLManager, related_name='manager', on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return self.get_name_display()

    @property
    def yahoo_team_key(self):
        # 'Gives the Yahoo team key'
        return f'{config("YAHOO_GAME_ID")}.l.{config("YAHOO_HBL_ID")}.t.{self.yahoo_team_id}'
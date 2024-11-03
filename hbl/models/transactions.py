from django.db import models

from hbl.models import HBLPlayer, HBLTeam


class HBLTransaction(models.Model):
    player = models.ForeignKey(
        HBLPlayer, related_name='transactions', on_delete=models.CASCADE
    )
    date = models.DateField()
    transaction_id = models.IntegerField()


class HBLTrade(HBLTransaction):
    destination_team = models.ForeignKey(HBLTeam, related_name='destination_trades', on_delete=models.CASCADE, null=True)
    source_team = models.ForeignKey(HBLTeam, related_name='source_trades', on_delete=models.CASCADE, null=True)

    def save(self, **kwargs):
        self.player.hbl_team = self.destination_team
        self.player.seasons_on_team = 0
        self.player.save()
        super().save(**kwargs)


class HBLAddPlayer(HBLTransaction):
    hbl_team = models.ForeignKey(
        HBLTeam, related_name='adds', on_delete=models.CASCADE, null=True
    )
    waiver = models.BooleanField(default=False)

    def save(self, **kwargs):
        if not self.waiver:
            self.player.keeper_cost_current = 1
            self.player.four_keeper_cost = False
            self.player.four_keeper_years = 0
            self.player.consecutive_seasons = 0
            self.player.seasons_on_team = 0
        else:
            self.player.seasons_on_team = 0
        self.player.hbl_team = self.hbl_team
        self.player.save()
        super().save(**kwargs)


class HBLDropPlayer(HBLTransaction):
    hbl_team = models.ForeignKey(
        HBLTeam, related_name='drops', on_delete=models.CASCADE, null=True
    )
    add = models.ForeignKey(
        HBLAddPlayer, related_name='dropped_for', null=True, on_delete=models.CASCADE
    )

    def save(self, **kwargs):
        self.player.hbl_team = None
        self.player.save()
        super().save(**kwargs)
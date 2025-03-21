# Generated by Django 5.0.4 on 2024-10-28 16:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hbl", "0004_rename_yahoo_player_key_hblplayer_yahoo_player_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="hbladdplayer",
            name="yahoo_id",
        ),
        migrations.RemoveField(
            model_name="hbldropplayer",
            name="yahoo_id",
        ),
        migrations.RemoveField(
            model_name="hblplayer",
            name="keeper_cost_next",
        ),
        migrations.RemoveField(
            model_name="hbltrade",
            name="id",
        ),
        migrations.RemoveField(
            model_name="hbltrade",
            name="yahoo_id",
        ),
        migrations.RemoveField(
            model_name="hbltransaction",
            name="team",
        ),
        migrations.RemoveField(
            model_name="hbltransaction",
            name="trade",
        ),
        migrations.AddField(
            model_name="hbladdplayer",
            name="hbl_team",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="adds",
                to="hbl.hblteam",
            ),
        ),
        migrations.AddField(
            model_name="hbldropplayer",
            name="hbl_team",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="drops",
                to="hbl.hblteam",
            ),
        ),
        migrations.AddField(
            model_name="hblplayer",
            name="consecutive_seasons",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="hblplayer",
            name="four_keeper_years",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="hbltrade",
            name="destination_team",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="destination_trades",
                to="hbl.hblteam",
            ),
        ),
        migrations.AddField(
            model_name="hbltrade",
            name="hbltransaction_ptr",
            field=models.OneToOneField(
                auto_created=True,
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="hbl.hbltransaction",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="hbltrade",
            name="source_team",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="source_trades",
                to="hbl.hblteam",
            ),
        ),
        migrations.AddField(
            model_name="hbltransaction",
            name="transaction_id",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="hbldropplayer",
            name="add",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="dropped_for",
                to="hbl.hbladdplayer",
            ),
        ),
    ]

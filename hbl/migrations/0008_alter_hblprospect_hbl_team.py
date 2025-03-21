# Generated by Django 5.0.4 on 2025-02-01 23:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hbl", "0007_alter_hblplayer_hbl_team_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hblprospect",
            name="hbl_team",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="prospects",
                to="hbl.hblteam",
            ),
        ),
    ]

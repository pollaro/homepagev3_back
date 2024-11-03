import json
import logging

from django.http import HttpResponse
from rest_framework.views import APIView

from hbl.models import HBLTeam

logger = logging.getLogger(__name__)


class TeamsView(APIView):

    def get(self, request):
        logger.info("Get HBL Teams")
        teams = HBLTeam.objects.selected_related('manager').all()
        return HttpResponse(json.dumps(teams), content_type="application/json")

class TeamDetailView(APIView):

    def get(self, request, team_id):
        logger.info(f'Get HBL Team Detail (TeamID: {team_id})')
        team = HBLTeam.objects.select_related('manager').prefetch_related().get(id=team_id)
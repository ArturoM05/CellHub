import logging
from datetime import datetime
import requests
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)
ALLY_INFO_ENDPOINT = "http://34.206.119.120/api/v1/sistema/info/"
REQUEST_TIMEOUT = 8

class AllyServiceInfoView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        started_at = datetime.utcnow()
        try:
            r = requests.get(ALLY_INFO_ENDPOINT, timeout=REQUEST_TIMEOUT, headers={"Accept": "application/json"})
            r.raise_for_status()
            ally_data = r.json()
            latency_ms = int((datetime.utcnow() - started_at).total_seconds() * 1000)
            return Response({"status": "ok", "ally_url": ALLY_INFO_ENDPOINT, "latency_ms": latency_ms, "data": ally_data})
        except requests.exceptions.Timeout:
            return Response({"status": "timeout", "data": None}, status=504)
        except Exception as e:
            return Response({"status": "error", "error": str(e), "data": None}, status=502)

"""
core/views_ally.py
──────────────────
Proxy view que consume el servicio del equipo aliado desde el backend Django.
Evita problemas de CORS cuando el frontend en EC2 intenta llamar directamente
al servidor del aliado.

Flujo:
    React frontend  →  GET /api/v1/ally/info/  →  Django  →  http://34.206.119.120/...
                                                           ←  JSON del aliado
                    ←  JSON enriquecido con metadatos propios

Registro en urls.py:
    from core.views_ally import AllyServiceInfoView
    path('api/v1/ally/info/', AllyServiceInfoView.as_view(), name='ally-info'),
"""

import logging
from datetime import datetime

import requests
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

ALLY_BASE_URL = "http://34.206.119.120"
ALLY_INFO_ENDPOINT = f"{ALLY_BASE_URL}/api/v1/sistema/info/"
REQUEST_TIMEOUT = 8  # segundos


class AllyServiceInfoView(APIView):
    """
    GET /api/v1/ally/info/

    Proxy hacia el servicio del equipo aliado.
    Devuelve los datos del aliado envueltos en un envelope propio
    para que el frontend tenga contexto adicional (latencia, timestamp, estado).

    Patrón Adapter aplicado aquí: traduce la respuesta del aliado
    al formato interno de CellHub sin acoplar el frontend al contrato
    externo del aliado.
    """

    authentication_classes = []   # endpoint público — solo lectura
    permission_classes = []

    def get(self, request):
        started_at = datetime.utcnow()

        try:
            ally_response = requests.get(
                ALLY_INFO_ENDPOINT,
                timeout=REQUEST_TIMEOUT,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "CellHub/1.0 AllyConsumer",
                },
            )
            ally_response.raise_for_status()
            ally_data = ally_response.json()

            latency_ms = int(
                (datetime.utcnow() - started_at).total_seconds() * 1000
            )

            return Response(
                {
                    "status": "ok",
                    "source": "ally_service",
                    "ally_url": ALLY_INFO_ENDPOINT,
                    "latency_ms": latency_ms,
                    "fetched_at": datetime.utcnow().isoformat() + "Z",
                    # ── datos reales del aliado ──────────────────────────────
                    "data": ally_data,
                    # ── métricas extraídas (adapter: formato interno) ────────
                    "summary": self._extract_summary(ally_data),
                }
            )

        except requests.exceptions.ConnectionError:
            logger.warning("AllyProxy: no se pudo conectar a %s", ALLY_INFO_ENDPOINT)
            return Response(
                {
                    "status": "unreachable",
                    "source": "ally_service",
                    "ally_url": ALLY_INFO_ENDPOINT,
                    "error": str(_("El servicio aliado no está disponible en este momento.")),
                    "data": None,
                    "summary": {},
                },
                status=503,
            )

        except requests.exceptions.Timeout:
            logger.warning("AllyProxy: timeout al conectar a %s", ALLY_INFO_ENDPOINT)
            return Response(
                {
                    "status": "timeout",
                    "source": "ally_service",
                    "ally_url": ALLY_INFO_ENDPOINT,
                    "error": str(_("El servicio aliado tardó demasiado en responder.")),
                    "data": None,
                    "summary": {},
                },
                status=504,
            )

        except requests.exceptions.HTTPError as exc:
            logger.error("AllyProxy: HTTP %s desde aliado", exc.response.status_code)
            return Response(
                {
                    "status": "error",
                    "source": "ally_service",
                    "ally_url": ALLY_INFO_ENDPOINT,
                    "error": str(_("El servicio aliado devolvió un error.")),
                    "http_status": exc.response.status_code,
                    "data": None,
                    "summary": {},
                },
                status=502,
            )

        except ValueError:
            logger.error("AllyProxy: respuesta no es JSON válido")
            return Response(
                {
                    "status": "invalid_response",
                    "source": "ally_service",
                    "ally_url": ALLY_INFO_ENDPOINT,
                    "error": str(_("El servicio aliado devolvió un formato inesperado.")),
                    "data": None,
                    "summary": {},
                },
                status=502,
            )

    # ── helpers ─────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_summary(data: dict) -> dict:
        """
        Adapter interno: extrae métricas clave del JSON del aliado
        y las normaliza al esquema de CellHub.

        Si el aliado cambia sus nombres de campo, solo hay que
        actualizar este método — el frontend no se entera.
        """
        if not isinstance(data, dict):
            return {}

        # Mapeo flexible: acepta nombres en español e inglés
        field_aliases = {
            "videojuegos": ["videojuegos", "games", "game_count", "total_games"],
            "planes":      ["planes", "plans", "plan_count",  "total_plans"],
            "suscripciones": ["suscripciones", "subscriptions", "sub_count", "total_subscriptions"],
            "usuarios":    ["usuarios", "users", "user_count",  "total_users", "clientes"],
        }

        summary = {}
        flat = _flatten(data)

        for canonical, aliases in field_aliases.items():
            for alias in aliases:
                if alias in flat:
                    summary[canonical] = flat[alias]
                    break

        return summary


def _flatten(obj: dict, prefix: str = "") -> dict:
    """Aplana un dict anidado para búsqueda flexible de campos."""
    result = {}
    for key, val in obj.items():
        full_key = f"{prefix}{key}".lower()
        if isinstance(val, dict):
            result.update(_flatten(val, f"{full_key}_"))
        else:
            result[full_key] = val
    return result

"""
Adapter pattern for third-party APIs.

This module provides adapters to consume external services and translate
their responses to our internal DTOs/schemas. Enables loose coupling and
easy testing via dependency injection.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import requests
import logging

logger = logging.getLogger(__name__)


class ThirdPartyAdapter(ABC):
    """
    Abstract base adapter for third-party API integrations.
    """
    @abstractmethod
    def get_products(self, query: str = '') -> List[Dict[str, Any]]:
        """Fetch products from external service."""
        pass

    @abstractmethod
    def get_pricing(self, product_id: str) -> Dict[str, Any]:
        """Fetch pricing/availability from external service."""
        pass

    @abstractmethod
    def submit_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit order to external service."""
        pass


class RequestsThirdPartyAdapter(ThirdPartyAdapter):
    """
    HTTP-based adapter using `requests` library to integrate external APIs.
    Translates external responses to internal DTO format.
    """
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})

    def get_products(self, query: str = '') -> List[Dict[str, Any]]:
        """
        Fetch products from external API and map to internal schema.
        
        Expected external response (example):
            {
                "items": [
                    {"id": "ext-001", "name": "Product A", "price": 100.0, "available": true}
                ]
            }
        
        Returns internal format:
            [
                {"external_id": "ext-001", "name": "Product A", "price": 100.0, "in_stock": true}
            ]
        """
        try:
            url = f"{self.base_url}/products"
            params = {'q': query} if query else {}
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            products = []
            for item in data.get('items', []):
                products.append({
                    'external_id': item.get('id'),
                    'name': item.get('name'),
                    'price': item.get('price'),
                    'in_stock': item.get('available', False),
                    'source': 'external',
                })
            return products
        except requests.exceptions.RequestException as e:
            logger.error(f"Third-party API /products request failed: {e}")
            return []

    def get_pricing(self, product_id: str) -> Dict[str, Any]:
        """
        Fetch pricing and availability for a product from external API.
        
        Expected external response:
            {"price": 100.0, "available": true, "stock": 50}
        
        Returns internal format:
            {"external_id": "...", "price": 100.0, "in_stock": true, "quantity": 50}
        """
        try:
            url = f"{self.base_url}/products/{product_id}/pricing"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            return {
                'external_id': product_id,
                'price': data.get('price'),
                'in_stock': data.get('available', False),
                'quantity': data.get('stock', 0),
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Third-party API /pricing request failed for {product_id}: {e}")
            return {}

    def submit_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit order to external API and return confirmation.
        
        Input order_data:
            {
                "items": [{"external_id": "ext-001", "quantity": 2}],
                "shipping_address": {...},
                "customer_email": "..."
            }
        
        Expected external response:
            {"order_id": "ext-order-001", "status": "confirmed", "eta": "2024-01-15"}
        
        Returns internal format:
            {"external_order_id": "ext-order-001", "status": "confirmed", "eta": "2024-01-15"}
        """
        try:
            url = f"{self.base_url}/orders"
            response = self.session.post(url, json=order_data, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            return {
                'external_order_id': data.get('order_id'),
                'status': data.get('status'),
                'eta': data.get('eta'),
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Third-party API /orders request failed: {e}")
            return {'status': 'error', 'message': str(e)}


class MockThirdPartyAdapter(ThirdPartyAdapter):
    """
    Mock adapter for testing/development when external API is unavailable.
    """
    def get_products(self, query: str = '') -> List[Dict[str, Any]]:
        return [
            {'external_id': 'mock-001', 'name': 'Mock Product A', 'price': 99.99, 'in_stock': True},
            {'external_id': 'mock-002', 'name': 'Mock Product B', 'price': 149.99, 'in_stock': False},
        ]

    def get_pricing(self, product_id: str) -> Dict[str, Any]:
        return {
            'external_id': product_id,
            'price': 99.99,
            'in_stock': True,
            'quantity': 10,
        }

    def submit_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'external_order_id': 'mock-order-001',
            'status': 'confirmed',
            'eta': '2024-01-20',
        }

"""
Mock Zep Paging for Local execution without Zep Cloud
"""

from ..services.local_memory.zep_client_mock import fetch_all_nodes_mock, fetch_all_edges_mock

def fetch_all_nodes(client, graph_id: str, **kwargs):
    return fetch_all_nodes_mock(client, graph_id, **kwargs)

def fetch_all_edges(client, graph_id: str, **kwargs):
    return fetch_all_edges_mock(client, graph_id, **kwargs)


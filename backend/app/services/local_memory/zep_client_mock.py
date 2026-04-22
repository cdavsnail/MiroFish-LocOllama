import uuid
import time
import json
import os
from typing import List, Dict, Any

from .local_graph import LocalGraph
from ...utils.llm_client import LLMClient
from ...utils.logger import get_logger
from ...config import Config

logger = get_logger('mirofish.zep_client_mock')

class NodeResponseMock:
    def __init__(self, data: Dict):
        self.uuid = data.get("uuid", "")
        self.uuid_ = self.uuid
        self.name = data.get("name", "")
        self.labels = data.get("labels", [])
        self.summary = data.get("summary", "")
        self.attributes = data.get("attributes", {})

class EdgeResponseMock:
    def __init__(self, data: Dict):
        self.uuid = data.get("uuid", "")
        self.uuid_ = self.uuid
        self.name = data.get("name", "")
        self.fact = data.get("fact", "")
        self.source_node_uuid = data.get("source_node_uuid", "")
        self.target_node_uuid = data.get("target_node_uuid", "")
        self.attributes = data.get("attributes", {})
        self.created_at = data.get("created_at")
        self.valid_at = data.get("valid_at")
        self.invalid_at = data.get("invalid_at")
        self.expired_at = data.get("expired_at")

class ZepNodeMock:
    def __init__(self, zep_mock):
        self.zep = zep_mock

    def _ensure_graphs_loaded(self):
        upload_folder = getattr(Config, 'UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), '../../uploads'))
        graphs_dir = os.path.join(upload_folder, 'graphs')
        if not os.path.exists(graphs_dir):
            return
        for file in os.listdir(graphs_dir):
            if file.endswith('.json'):
                gid = file[:-5]
                if gid not in self.zep.graphs:
                    self.zep.graphs[gid] = LocalGraph(gid)

    def get(self, uuid_: str, **kwargs):
        self._ensure_graphs_loaded()
        for graph_id, graph in self.zep.graphs.items():
            for node in graph.nodes:
                if node.get("uuid") == uuid_:
                    return NodeResponseMock(node)
        return None

    def get_entity_edges(self, node_uuid: str, **kwargs):
        self._ensure_graphs_loaded()
        edges = []
        for graph_id, graph in self.zep.graphs.items():
            for edge in graph.edges:
                if edge.get("source_node_uuid") == node_uuid or edge.get("target_node_uuid") == node_uuid:
                    edges.append(EdgeResponseMock(edge))
        return edges

class ZepEpisodeMock:
    def __init__(self, zep_mock):
        self.zep = zep_mock

    def get(self, uuid_: str, **kwargs):
        class EpMock:
            def __init__(self):
                self.processed = True
        return EpMock()

class ZepGraphApiMock:
    def __init__(self, zep_mock):
        self.zep = zep_mock
        self.node = ZepNodeMock(zep_mock)
        self.episode = ZepEpisodeMock(zep_mock)
        self.llm = LLMClient()

    def create(self, graph_id: str, name: str, description: str, **kwargs):
        self.zep.graphs[graph_id] = LocalGraph(graph_id)
        return {"graph_id": graph_id}

    def set_ontology(self, graph_ids: List[str], entities=None, edges=None, **kwargs):
        for gid in graph_ids:
            if gid not in self.zep.graphs:
                self.zep.graphs[gid] = LocalGraph(gid)
            self.zep.graphs[gid].set_ontology({"entities": entities, "edges": edges})

    def _extract_entities_with_llm(self, text: str, graph_id: str):
        """Mock LLM-based entity extraction similar to Zep Cloud's internal mechanism"""
        try:
            graph = self.zep.graphs[graph_id]
            ontology = graph.ontology

            system_prompt = """You are an entity extraction engine. Extract entities and relationships from the user text based on the provided ontology.
Respond ONLY with a valid JSON object in this format:
{
  "nodes": [{"name": "EntityName", "labels": ["TypeFromOntology"], "summary": "Short description"}],
  "edges": [{"source_name": "Entity1", "target_name": "Entity2", "name": "RELATION_TYPE", "fact": "Relationship description"}]
}
"""
            user_prompt = f"Ontology: {json.dumps(ontology)}\n\nText: {text}"

            response = self.llm.chat_json(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            node_map = {}
            for node in response.get("nodes", []):
                new_node = graph.add_node(node)
                node_map[new_node["name"]] = new_node["uuid"]

            for edge in response.get("edges", []):
                src_uuid = node_map.get(edge.get("source_name"))
                tgt_uuid = node_map.get(edge.get("target_name"))
                if src_uuid and tgt_uuid:
                    edge["source_node_uuid"] = src_uuid
                    edge["target_node_uuid"] = tgt_uuid
                    graph.add_edge(edge)

        except Exception as e:
            logger.error(f"Local graph entity extraction failed: {e}")

    def add_batch(self, graph_id: str, episodes: List[Any], **kwargs):
        if graph_id not in self.zep.graphs:
            self.zep.graphs[graph_id] = LocalGraph(graph_id)
        graph = self.zep.graphs[graph_id]

        results = []
        class BatchRes:
            def __init__(self, uid):
                self.uuid = uid
                self.uuid_ = uid

        for ep in episodes:
            content = ep.data
            uid = graph.add_episode(content)
            self._extract_entities_with_llm(content, graph_id)
            results.append(BatchRes(uid))
        return results

    def add(self, graph_id: str, type: str, data: str, **kwargs):
        if graph_id not in self.zep.graphs:
            self.zep.graphs[graph_id] = LocalGraph(graph_id)
        self.zep.graphs[graph_id].add_episode(data)
        self._extract_entities_with_llm(data, graph_id)

    def search(self, graph_id: str, query: str, limit: int, scope: str = "edges", reranker: str = "", **kwargs):
        if graph_id not in self.zep.graphs:
            self.zep.graphs[graph_id] = LocalGraph(graph_id)

        graph = self.zep.graphs[graph_id]
        keywords = query.lower().split()

        edges = []
        if scope in ["edges", "both"]:
            for e in graph.edges:
                fact = e.get("fact", "").lower()
                if any(k in fact for k in keywords):
                    edges.append(EdgeResponseMock(e))

        nodes = []
        if scope in ["nodes", "both"]:
            for n in graph.nodes:
                summary = n.get("summary", "").lower()
                name = n.get("name", "").lower()
                if any(k in summary for k in keywords) or any(k in name for k in keywords):
                    nodes.append(NodeResponseMock(n))

        return type('obj', (object,), {'edges': edges[:limit], 'nodes': nodes[:limit]})

    def delete(self, graph_id: str, **kwargs):
        if graph_id in self.zep.graphs:
            del self.zep.graphs[graph_id]

class ZepMock:
    """Mock for Zep Cloud client"""
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.graphs = {}
        self.graph = ZepGraphApiMock(self)

def fetch_all_nodes_mock(client, graph_id: str, **kwargs):
    if graph_id not in client.graphs:
        client.graphs[graph_id] = LocalGraph(graph_id)
    return [NodeResponseMock(n) for n in client.graphs[graph_id].nodes]

def fetch_all_edges_mock(client, graph_id: str, **kwargs):
    if graph_id not in client.graphs:
        client.graphs[graph_id] = LocalGraph(graph_id)
    return [EdgeResponseMock(e) for e in client.graphs[graph_id].edges]

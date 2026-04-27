import os
import json
import uuid
import time
from typing import Dict, List, Any, Optional

from ...config import Config
from ...utils.logger import get_logger

logger = get_logger('mirofish.local_graph')

from werkzeug.utils import secure_filename

class LocalGraph:
    """A simple local mock for Zep Cloud Graph."""

    def __init__(self, graph_id: str):
        self.graph_id = graph_id
        # Fallback if Config.UPLOAD_FOLDER is undefined or None
        upload_folder = getattr(Config, 'UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), '../../uploads'))
        self.graphs_dir = os.path.join(upload_folder, 'graphs')
        os.makedirs(self.graphs_dir, exist_ok=True)
        safe_graph_id = secure_filename(graph_id)
        if not safe_graph_id:
            safe_graph_id = "default_graph"
        self.graph_file = os.path.join(self.graphs_dir, f"{safe_graph_id}.json")
        self._load()

    def _load(self):
        if os.path.exists(self.graph_file):
            try:
                with open(self.graph_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.nodes = data.get("nodes", [])
                    self.edges = data.get("edges", [])
                    self.ontology = data.get("ontology", {})
                    self.episodes = data.get("episodes", [])
            except Exception as e:
                logger.error(f"Failed to load local graph {self.graph_id}: {e}")
                self.nodes = []
                self.edges = []
                self.ontology = {}
                self.episodes = []
        else:
            self.nodes = []
            self.edges = []
            self.ontology = {}
            self.episodes = []
            self._save()

    def _save(self):
        data = {
            "nodes": self.nodes,
            "edges": self.edges,
            "ontology": self.ontology,
            "episodes": self.episodes
        }
        with open(self.graph_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_node(self, node: Dict[str, Any]):
        if 'uuid' not in node:
            node['uuid'] = str(uuid.uuid4())
        # Make sure node always has name and summary to prevent errors
        node['name'] = node.get('name', 'Unnamed Entity')
        node['summary'] = node.get('summary', '')
        self.nodes.append(node)
        self._save()
        return node

    def add_edge(self, edge: Dict[str, Any]):
        if 'uuid' not in edge:
            edge['uuid'] = str(uuid.uuid4())
        edge['fact'] = edge.get('fact', '')
        edge['name'] = edge.get('name', 'RELATION')
        self.edges.append(edge)
        self._save()
        return edge

    def add_episode(self, text: str):
        episode = {
            "uuid": str(uuid.uuid4()),
            "content": text,
            "created_at": time.time()
        }
        self.episodes.append(episode)
        self._save()
        return episode['uuid']

    def set_ontology(self, ontology: Dict[str, Any]):
        self.ontology = ontology
        self._save()

# agent_framework/storage/dgraph_connector.py
import pydgraph
from typing import Dict, Any, List, Optional
import json
import threading
from contextlib import contextmanager


class DGraphConnector:
    """Thread-safe connector for DGraph database operations"""

    def __init__(self, addresses: List[str] = ["localhost:9080"]):
        self.client_stub = pydgraph.DgraphClientStub(*addresses)
        self.client = pydgraph.DgraphClient(self.client_stub)
        self._lock = threading.Lock()

    @contextmanager
    def transaction(self, read_only: bool = False):
        """Context manager for transactions"""
        txn = self.client.txn(read_only=read_only)
        try:
            yield txn
        finally:
            txn.discard()

    def query(self, query_string: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a DQL query"""
        with self._lock:
            with self.transaction(read_only=True) as txn:
                res = txn.query(query_string, variables=variables)
                return json.loads(res.json)

    def mutate(self, mutation: Dict[str, Any], commit_now: bool = True) -> Dict[str, Any]:
        """Execute a mutation"""
        with self._lock:
            with self.transaction() as txn:
                res = txn.mutate(set_obj=mutation, commit_now=commit_now)
                if commit_now:
                    return {"uids": res.uids}
                else:
                    txn.commit()
                    return {"uids": res.uids}

    def upsert(self, query: str, mutation: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert operation"""
        with self._lock:
            with self.transaction() as txn:
                # First query to check existence
                query_res = txn.query(query)

                # Then mutate
                res = txn.mutate(set_obj=mutation)
                txn.commit()

                return {
                    "query_result": json.loads(query_res.json),
                    "uids": res.uids
                }

    def alter_schema(self, schema: str):
        """Alter the database schema"""
        with self._lock:
            op = pydgraph.Operation(schema=schema)
            self.client.alter(op)

    def drop_all(self):
        """Drop all data (use with caution!)"""
        with self._lock:
            op = pydgraph.Operation(drop_all=True)
            self.client.alter(op)
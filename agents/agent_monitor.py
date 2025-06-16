# agent_framework/utils/monitoring.py
import threading
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from server.agents.agent_manager import AgentManager


class AgentMonitor:
    """Monitor agent performance and health"""

    def __init__(self, check_interval: float = 60.0):
        self.metrics = defaultdict(list)
        self._metrics_lock = threading.Lock()

        self.alerts = []
        self._alerts_lock = threading.Lock()

        self.check_interval = check_interval
        self._monitor_thread = None
        self._shutdown = threading.Event()

    def start_monitoring(self, manager: AgentManager):
        """Start background monitoring"""
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(manager,),
            daemon=True
        )
        self._monitor_thread.start()

    def _monitor_loop(self, manager: AgentManager):
        """Background monitoring loop"""
        while not self._shutdown.is_set():
            try:
                # Check all agents
                with manager._agents_lock:
                    agent_ids = list(manager.agents.keys())

                for agent_id in agent_ids:
                    health = self.check_agent_health(manager, agent_id)

                    if health["status"] == "unhealthy":
                        self.add_alert(
                            f"Agent {agent_id} is unhealthy: "
                            f"error_rate={health['error_rate']:.2%}"
                        )

            except Exception as e:
                print(f"Monitor error: {e}")

            self._shutdown.wait(self.check_interval)

    def record_metric(self, agent_id: str, metric_name: str, value: Any):
        """Record a metric for an agent"""
        with self._metrics_lock:
            self.metrics[agent_id].append({
                "metric": metric_name,
                "value": value,
                "timestamp": datetime.utcnow()
            })

    def get_agent_metrics(self, agent_id: str,
                          time_window: Optional[timedelta] = None) -> List[Dict]:
        """Get metrics for an agent within a time window"""
        with self._metrics_lock:
            metrics = self.metrics.get(agent_id, []).copy()

        if time_window:
            cutoff = datetime.utcnow() - time_window
            metrics = [m for m in metrics if m["timestamp"] > cutoff]

        return metrics

    def check_agent_health(self, manager: AgentManager, agent_id: str) -> Dict[str, Any]:
        """Check agent health"""
        stats = manager.get_agent_stats(agent_id)

        # Get queue size
        with manager._agents_lock:
            if agent_id in manager.agents:
                queue_size = manager.agents[agent_id].task_queue.qsize()
            else:
                queue_size = 0

        # Determine health status
        error_rate = stats.get("error_rate", 0)
        status = "healthy"

        if error_rate > 0.1:
            status = "unhealthy"
        elif error_rate > 0.05:
            status = "warning"
        elif queue_size > 100:
            status = "overloaded"

        return {
            "agent_id": agent_id,
            "status": status,
            "error_rate": error_rate,
            "queue_size": queue_size,
            **stats
        }

    def add_alert(self, message: str):
        """Add an alert"""
        with self._alerts_lock:
            self.alerts.append({
                "message": message,
                "timestamp": datetime.utcnow()
            })

    def get_alerts(self, since: Optional[datetime] = None) -> List[Dict]:
        """Get alerts since a given time"""
        with self._alerts_lock:
            alerts = self.alerts.copy()

        if since:
            alerts = [a for a in alerts if a["timestamp"] > since]

        return alerts

    def shutdown(self):
        """Shutdown monitoring"""
        self._shutdown.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
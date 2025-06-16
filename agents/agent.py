from server.agents.agent_manager import AgentManager
from server.agents.agent_model import AgentConfig
from server.agents.agent_monitor import AgentMonitor
from server.agents.agent_rag import RAGAgent
from server.agents.agent_tasked import TaskAgent

# Example usage
if __name__ == "__main__":
    

    # Create manager
    manager = AgentManager()

    # Create and register agents
    config1 = AgentConfig(
        name="GPT4Agent",
        model="gpt-4",
        thread_pool_size=3
    )
    agent1 = TaskAgent(config1)
    manager.register_agent(agent1)

    config2 = AgentConfig(
        name="RAGAgent",
        model="gpt-3.5-turbo",
        thread_pool_size=2,
        metadata={"capabilities": ["search", "retrieval", "context"]}
    )
    agent2 = RAGAgent(config2)
    manager.register_agent(agent2)

    # Start monitoring
    monitor = AgentMonitor()
    monitor.start_monitoring(manager)

    # Submit some tasks
    agent_message = agent_message(content="Explain quantum computing", role="user")

    # Route using different strategies
    task_id1 = manager.route_task(agent_message, strategy="round_robin")
    task_id2 = manager.route_task(
        agent_message(content="Search for information about Python threading", role="user"),
        strategy="capability"
    )

    # Wait for results
    result1 = manager.get_result(task_id1, timeout=30.0)
    if result1:
        print(f"Task {result1.task_id} completed in {result1.processing_time:.2f}s")
        print(f"Result: {result1.result}")

    # Check agent stats
    for agent_id in manager.agents:
        stats = manager.get_agent_stats(agent_id)
        print(f"\nAgent {agent_id} stats: {stats}")

    # Cleanup
    monitor.shutdown()
    manager.shutdown_all()
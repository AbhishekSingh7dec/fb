import os, yaml
from collections.abc import Mapping
from crewai import Agent, Task, Crew, Process
from typing import Iterable, Mapping as MappingType, Any, Dict, List
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(".env")

with open("food_bill/config/agents.yaml") as f:
    agents_config = yaml.safe_load(f)

with open("food_bill/config/tasks.yaml") as f:
    tasks_config = yaml.safe_load(f)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
llm = {"provider": "openai",}


def load_yaml(path: Path) -> Any:
    """Helper function to load YAML from the given path."""
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def create_agents(agents_config):
    agents = {}
    for name, cfg in agents_config.items():
        if not isinstance(cfg, dict):
            raise TypeError(f"Agent '{name}' config must be a mapping, got {type(cfg).__name__}")
        agents[name] = Agent(**cfg)  # <-- unpack YAML dict
    return agents

def create_tasks(tasks_config, agents, inputs):
    task_specs = tasks_config.values() if isinstance(tasks_config, dict) else tasks_config
    tasks = []
    for spec in task_specs:
        if not isinstance(spec, dict):
            raise TypeError(f"Each task config must be a mapping, got {type(spec).__name__}")
        agent_name = spec.get("agent")
        if agent_name not in agents:
            raise KeyError(f"Task references undefined agent: {agent_name!r}")
        spec_no_agent = {k: v for k, v in spec.items() if k != "agent"}
        task = Task(**spec_no_agent, inputs=inputs)
        task.agent = agents[agent_name]
        tasks.append(task)
    return tasks


def create_agents_1(agents_config: Dict[str, Any]) -> Dict[str, Agent]:
    """Instantiate Agent objects for each entry in the agents_config dict."""
    agents: Dict[str, Agent] = {}
    for name, config in agents_config.items():
        agents[name] = Agent(config=config)
    return agents


def create_tasks_1(tasks_config: Any, agents: Mapping[str, Agent], inputs: Dict[str, Any]) -> List[Task]:
    """
    Build Task objects from YAML. Supports either:
      - a list of task dicts, or
      - a dict of {task_name: task_dict}
    """
    if not tasks_config:
        return []

    task_specs = tasks_config.values() if isinstance(tasks_config, dict) else tasks_config
    tasks: List[Task] = []

    for spec in task_specs:
        if not isinstance(spec, dict):
            raise TypeError(f"Each task must be a mapping; got {type(spec).__name__}")
        agent_name = spec.get("agent")
        if not agent_name or agent_name not in agents:
            raise KeyError(f"Task references undefined agent: {agent_name!r}")
        task = Task(config=spec, inputs=inputs)
        task.agent = agents[agent_name]
        tasks.append(task)

    return tasks


def create_tasks_2(
    tasks_config: Any,
    agents: MappingType[str, Agent],
    inputs: MappingType[str, Any],
) -> List[Task]:
    """
    Build a list of Task objects from the YAML configuration.

    `tasks_config` may be a list of task dictionaries, or a dict mapping task names
    to their configurations (as in a typical tasks.yaml file:contentReference[oaicite:2]{index=2}).
    This function normalises the input and validates that each task spec is a mapping.
    """
    if not tasks_config:
        return []

    # If tasks_config is a dict (e.g., loaded from YAML with top-level task names),
    # iterate over its values instead of its keys to avoid getting str objects.
    if isinstance(tasks_config, Mapping):
        task_specs = tasks_config.values()
    else:
        task_specs = tasks_config

    tasks: List[Task] = []

    for i, spec in enumerate(task_specs):
        if not isinstance(spec, Mapping):
            raise TypeError(
                f"Each task configuration must be a mapping, got {type(spec).__name__!r} at index {i}. "
                "Check your tasks YAML; it should map task names to dictionaries:contentReference[oaicite:3]{index=3}."
            )

        cfg = dict(spec)  # copy to avoid mutating original data
        agent_name = cfg.get("agent")
        if agent_name is None:
            raise KeyError(f"Missing 'agent' key in task configuration: {cfg}")

        # resolve the agent; this will raise KeyError with a clear message if missing
        try:
            agent_instance = agents[agent_name]
        except KeyError:
            raise KeyError(f"Agent '{agent_name}' is not defined in the agents mapping")

        # create and configure the task
        task = Task(config=cfg, inputs=inputs)
        task.agent = agent_instance
        tasks.append(task)

    return tasks


def create_tasks_3(tasks_config: Any, agents: Dict[str, Agent], inputs: Dict[str, Any]) -> list:
    """
    Build a list of Task objects from the YAML configuration.

    The `inputs` argument should be a dict containing any values needed to
    replace placeholders in the task descriptions (e.g. receipt_path or
    claim_data).  CrewAI will propagate outputs between tasks, so only
    initial values (such as the receipt path and claim data) need to be
    specified here.
    """
    tasks: list = []
    for task_spec in tasks_config:
        task = Task(config=task_spec, inputs=inputs)
        task.agent = agents[task_spec["agent"]]
        tasks.append(task)
    return tasks


def main() -> None:
    """Run the reimbursement validation workflow."""

    # Create Agent objects
    agents = create_agents(agents_config)

    # Example claim input (replace with real data in production)
    claim_data = {
        "employee_id": "E12345",
        "employee_name": "Anita Singh",
        "claimed_amount": 250.0,
        "date": "2025-08-09",
        "receipt_path": "./sample_receipts/restaurant_receipt.pdf",
    }

    # Initial inputs
    inputs = {
        "receipt_path": claim_data["receipt_path"],
        "claim_data": claim_data,
    }

    # Create Task objects and assign agents
    tasks = create_tasks(tasks_config, agents, inputs)

    # Build the crew and run tasks sequentially
    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    # Kick off the crew
    result = crew.kickoff(inputs=inputs)

    # Print each task’s output
    print("\n--- Workflow Results ---")
    for task_result in result.results:
        print(f"Task '{task_result.task.id}' output:")
        print(task_result.raw)


receipt = {
    "Restaurant Name": "Maarhaba Restaurant",
    "Location": "Gariahat (South) Dakuria, Kolkata - 700031",
    "Date of Invoice": "18/10/18",
    "Time of Invoice": "22:45",
    "Bill Number": "5365",
    "Items Ordered": [
        {
            "Item Name": "Water Bottle (packeged)",
            "Quantity": 1,
            "Rate": 30.00,
            "Amount": 30.00
        },
        {
            "Item Name": "Crispy Chilli Baby Corn",
            "Quantity": 1,
            "Rate": 170.00,
            "Amount": 170.00
        },
        {
            "Item Name": "Kashmiri Pulao",
            "Quantity": 1,
            "Rate": 130.00,
            "Amount": 130.00
        },
        {
            "Item Name": "Kadai Chicken",
            "Quantity": 1,
            "Rate": 220.00,
            "Amount": 220.00
        },
        {
            "Item Name": "Mutton Biriyani",
            "Quantity": 1,
            "Rate": 220.00,
            "Amount": 220.00
        },
        {
            "Item Name": "Soft Drinks",
            "Quantity": 1,
            "Rate": 40.00,
            "Amount": 40.00
        }
    ],
    "Sub Total": 840.00,
    "SGST Amount and Percentage": {
        "Amount": None,
        "Percentage": None
    },
    "CGST Amount and Percentage": {
        "Amount": None,
        "Percentage": None
    },
    "Grand Total": 840.00
}


if __name__ == "__main__":
    main()




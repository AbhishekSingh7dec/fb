import yaml
from crewai import Agent, Task, Crew

from dotenv import load_dotenv
load_dotenv(".env")

with open("config/agents.yaml") as f:
    agents_config = yaml.safe_load(f)

with open("config/tasks.yaml") as f:
    tasks_config = yaml.safe_load(f)

# Create Agent objects with config=...
ocr_agent = Agent(config=agents_config['ocr_agent'])
# repeat for parser_agent, validator_agent, notifier_agent

# Create Task objects with config=...
ocr_task = Task(config=tasks_config[0])
# etc.



"""
Expense Reimbursement Validation Workflow using CrewAI

This script demonstrates how to assemble a multi‑agent workflow using the
CrewAI framework.  It loads agent and task configurations from YAML files,
initialises environment variables from a .env file, and orchestrates a
sequence of tasks to extract data from a receipt, parse it into structured
fields, validate it against a submitted claim, and notify the appropriate
stakeholders.  The workflow uses GPT‑4 for reasoning and Gemini Vision Pro
for OCR.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process


def load_yaml(path: Path) -> Any:
    """Helper function to load YAML from the given path."""
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def create_agents(agents_config: Dict[str, Any]) -> Dict[str, Agent]:
    """Instantiate Agent objects for each entry in the agents_config dict."""
    agents: Dict[str, Agent] = {}
    for name, config in agents_config.items():
        agents[name] = Agent(config=config)
    return agents


def create_tasks(tasks_config: Any, agents: Dict[str, Agent], inputs: Dict[str, Any]) -> list:
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
    # Determine base directory (project root).
    base_dir = Path(__file__).resolve().parent

    # Load environment variables from .env
    env_path = base_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        parent_env = base_dir.parent / ".env"
        if parent_env.exists():
            load_dotenv(parent_env)
        else:
            raise FileNotFoundError(
                "Unable to locate the .env file. Make sure it exists in your project root."
            )

    # Load agent and task configurations from YAML files
    config_dir = base_dir / "config"
    agents_yaml = config_dir / "agents.yaml"
    tasks_yaml = config_dir / "tasks.yaml"
    agents_config = load_yaml(agents_yaml)
    tasks_config = load_yaml(tasks_yaml)

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


if __name__ == "__main__":
    main()



client = AzureOpenAI(
    model =os.getenv("AZURE_OPENAI_MODEL"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_base=os.getenv("AZURE_OPENAI_API_BASE"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"))


import os
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),  # Your Azure endpoint
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),           # Your Azure API key
    api_version="2024-02-01"                             # Example API version
)


response = client.chat.completions.create(
    model="madat-gpt4-o",  # Your model deployment name
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about openai?"}
    ]
)

print(response.choices[0].message.content)

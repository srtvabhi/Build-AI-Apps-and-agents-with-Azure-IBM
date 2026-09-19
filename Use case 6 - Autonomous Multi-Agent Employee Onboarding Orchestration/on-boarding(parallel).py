import asyncio
import os
import sys

from dotenv import load_dotenv

from agent_framework import (
    AgentExecutorResponse,
    Message,
    WorkflowBuilder,
    WorkflowContext,
    executor,
)
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

load_dotenv()

EMPLOYEE = """
Employee Name: John Smith
Employee ID: EMP1024
Department: Finance
Role: Data Analyst
Location: Bangalore
Joining Date: 01-Oct-2026
"""


@executor(id="merge_parallel_results")
async def merge_parallel_results(
    results: list[AgentExecutorResponse],
    ctx: WorkflowContext[list[str | Message]],
):
    combined_results = "\n\n".join(
        f"{result.executor_id}:\n{result.agent_response.text}" for result in results
    )
    first_result = results[0]
    response_message_count = len(first_result.agent_response.messages)
    shared_hr_context = (
        first_result.full_conversation[:-response_message_count]
        if response_message_count
        else first_result.full_conversation
    )
    await ctx.send_message(
        [
            *shared_hr_context,
            Message(
                "assistant",
                [f"SPECIALIST ONBOARDING RESULTS\n\n{combined_results}"],
            ),
        ]
    )


async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    credential = AzureCliCredential()

    chat_client = FoundryChatClient(
        credential=credential,
        project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
        model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
    )

    hr_agent = chat_client.as_agent(
        name="HR Agent",
        instructions="""
        You are the HR onboarding validation specialist and the first agent in
        the workflow. Validate the employee name, ID, department, role, location,
        and joining date. Do not invent missing information or claim that any HR
        system was updated.

        Set Status to READY when all required data is usable. Otherwise set it to
        BLOCKED and list the exact missing or invalid fields. Keep the complete
        response under 200 words.

        Return these sections:
        HR VALIDATION
        Status: READY or BLOCKED
        Verified Employee Data:
        Missing or Invalid Data:
        Handoff to Specialists:
        """,
    )

    it_agent = chat_client.as_agent(
        name="IT Agent",
        instructions="""
        You are the IT onboarding planner. Use the employee information and HR
        validation. If HR is BLOCKED, preserve the blocker and do not plan
        provisioning. Otherwise prepare a concise proposed status covering email,
        laptop, applications, role-based access, MFA, timing, approvals, and owners.

        Do not claim that accounts, devices, licenses, tickets, or permissions
        were actually created. Do not invent passwords or confidential data.
        Keep the complete response under 250 words and use no more than five
        bullets in each section.

        Return these sections:
        IT ONBOARDING STATUS
        Status: READY, READY WITH ACTIONS, or BLOCKED
        Proposed Setup:
        Dependencies and Approvals:
        Next Actions:
        """,
    )

    learning_agent = chat_client.as_agent(
        name="Learning Agent",
        instructions="""
        You are the learning and compliance onboarding planner. Use the employee
        information and HR validation. If HR is BLOCKED, preserve the blocker.
        Otherwise propose security, privacy, compliance, workplace, and
        role-specific training with realistic due dates and action owners.

        Do not claim that training was assigned, enrolled, or completed. Clearly
        identify assumptions and requirements that need policy-owner confirmation.
        Keep the complete response under 250 words and use no more than five
        bullets in each section.

        Return these sections:
        LEARNING ONBOARDING STATUS
        Status: READY, READY WITH ACTIONS, or BLOCKED
        Proposed Training:
        Assumptions and Approvals:
        Next Actions:
        """,
    )

    manager_agent = chat_client.as_agent(
        name="Manager Agent",
        instructions="""
        You are the hiring-manager onboarding planner. Use the employee information
        and HR validation. If HR is BLOCKED, preserve the blocker. Otherwise create
        a concise first-week plan covering the manager welcome, introductions, IT
        check, learning, role orientation, first assignment, owners, and outcomes.

        Do not claim that meetings were booked or tasks were completed. Mark
        assumptions and any information that the hiring manager must confirm.
        Keep the complete response under 250 words and use no more than five
        bullets in each section.

        Return these sections:
        MANAGER ONBOARDING STATUS
        Status: READY, READY WITH ACTIONS, or BLOCKED
        First-Week Plan:
        Dependencies and Assumptions:
        Next Actions:
        """,
    )

    reporting_agent = chat_client.as_agent(
        name="Reporting Agent",
        instructions="""
        You are the final onboarding reporting agent. Use the employee record and
        the completed IT, Learning, and Manager results. Consolidate them into one
        decision-ready report. Do not invent facts or describe proposed work as
        completed. Preserve blockers, assumptions, owners, and due dates.

        Overall Status must be BLOCKED if any specialist is blocked; otherwise use
        READY WITH ACTIONS while work remains. Keep the response under 350 words.

        Return these sections:
        FINAL ONBOARDING REPORT
        Overall Status: READY, READY WITH ACTIONS, or BLOCKED
        Employee Summary:
        HR Readiness:
        IT, Learning, and Manager Summary:
        Outstanding Actions:
        Final Readiness Decision:
        """,
    )

    parallel_agents = [it_agent, learning_agent, manager_agent]
    workflow = (
        WorkflowBuilder(
            start_executor=hr_agent,
            name="hybrid-employee-onboarding",
            output_from="all",
        )
        .add_fan_out_edges(hr_agent, parallel_agents)
        .add_fan_in_edges(parallel_agents, merge_parallel_results)
        .add_edge(merge_parallel_results, reporting_agent)
        .build()
    )

    print(
        "Starting hybrid workflow: HR -> [IT + Learning + Manager] -> Reporting",
        flush=True,
    )

    agent_names = {
        "hr agent": "HR Agent",
        "it agent": "IT Agent",
        "learning agent": "Learning Agent",
        "manager agent": "Manager Agent",
        "reporting agent": "Reporting Agent",
    }
    buffers = {agent_id: "" for agent_id in agent_names}
    started_agents = set()

    async for event in workflow.run(EMPLOYEE, stream=True):
        agent_id = (event.executor_id or "").replace("_", " ").lower()

        if event.type == "executor_completed" and agent_id in agent_names:
            remaining_text = buffers[agent_id].strip()
            if remaining_text:
                print(f"[{agent_names[agent_id]}] {remaining_text}", flush=True)
                buffers[agent_id] = ""
            print(f"[{agent_names[agent_id]}] completed.", flush=True)
            continue

        if (
            event.type != "output"
            or agent_id not in agent_names
            or not event.data
        ):
            continue

        if agent_id not in started_agents:
            started_agents.add(agent_id)
            print(f"\n[{agent_names[agent_id]}] started responding...", flush=True)

        text = getattr(event.data, "text", str(event.data))
        buffers[agent_id] += text

        while "\n" in buffers[agent_id]:
            line, buffers[agent_id] = buffers[agent_id].split("\n", 1)
            line = line.rstrip("\r")
            if line:
                print(f"[{agent_names[agent_id]}] {line}", flush=True)

    for agent_id, remaining_text in buffers.items():
        if remaining_text.strip():
            print(
                f"[{agent_names[agent_id]}] {remaining_text.strip()}",
                flush=True,
            )

    print("\nHybrid onboarding workflow completed.", flush=True)


if __name__ == "__main__":
    asyncio.run(main())

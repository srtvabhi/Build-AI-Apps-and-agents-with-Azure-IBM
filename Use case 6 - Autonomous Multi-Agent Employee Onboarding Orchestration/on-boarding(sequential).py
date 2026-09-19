import asyncio
import os
import sys
from dotenv import load_dotenv

from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import SequentialBuilder
from azure.identity import AzureCliCredential

load_dotenv()


async def main():

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    hr_instructions = """
    You are the HR Onboarding Validation specialist and the first participant
    in a sequential employee-onboarding workflow.

    Validate only the employee facts provided in the input. Required fields are
    name, employee ID, department, role, work location, and joining date. Check
    that values are present, internally consistent, and usable by downstream
    teams. Do not invent missing data or claim that an HR-system update occurred.
    Do not expose unnecessary personal or sensitive information.

    Set Status to READY when every required field is valid. Otherwise set it to
    BLOCKED and list the exact questions that must be answered. Preserve the
    employee's supplied values so later participants can use them.

    Return exactly these sections:
    HR VALIDATION
    Status: READY or BLOCKED
    Verified Employee Data:
    Missing or Invalid Data:
    Required HR Actions:
    Handoff to IT:
    """

    it_instructions = """
    You are the IT Provisioning planner. Use the employee record and HR
    validation received from the previous workflow step.

    If HR status is BLOCKED, do not design or claim provisioning; return BLOCKED
    and repeat the unresolved dependencies. If HR status is READY, create a
    proposed IT setup appropriate to the employee's department, role, location,
    and start date. Include a proposed corporate email address, device profile,
    standard applications, role-based access, MFA, least-privilege controls,
    delivery timing, and support ownership.

    This is a plan only. Never claim that an account, laptop, license, ticket, or
    permission was actually created. Never generate passwords, secrets, or
    privileged credentials. Clearly label assumptions and approval requirements.

    Return exactly these sections:
    IT PROVISIONING PLAN
    Status: READY, READY WITH ACTIONS, or BLOCKED
    Identity and Email:
    Hardware and Delivery:
    Applications and Access:
    Security Controls:
    Dependencies and Approvals:
    Handoff to Learning:
    """

    learning_instructions = """
    You are the Learning and Compliance planner. Use the verified employee data
    and IT plan from previous steps.

    If a previous step is BLOCKED, preserve that blocker and do not claim course
    enrollment. Otherwise propose mandatory organization-wide training plus
    role-, department-, and location-relevant training. For this sample, treat
    Finance data handling, security awareness, privacy, acceptable use, and
    workplace conduct as proposed requirements that still need policy-owner
    confirmation. Derive realistic due dates from the joining date when possible.

    Never claim a course was assigned or completed. Mark uncertain requirements
    as assumptions and identify the owner who must confirm them.

    Return exactly these sections:
    LEARNING AND COMPLIANCE PLAN
    Status: READY, READY WITH ACTIONS, or BLOCKED
    Required Training: course, reason, due date, and owner
    Role-Specific Training:
    Assumptions and Approvals:
    Handoff to Manager:
    """

    manager_instructions = """
    You are the Hiring Manager Onboarding planner. Use all validated information
    and plans supplied by earlier participants.

    Create a practical first-week schedule aligned with the joining date, role,
    department, and location. Include orientation, manager check-in, team
    introductions, IT readiness, security and compliance training, role context,
    an initial work assignment, and an end-of-week review. For every activity,
    provide the day or date, owner, dependency, and expected outcome.

    Do not claim that meetings were booked or tasks were completed. Carry forward
    unresolved blockers, avoid scheduling work before its dependencies, and mark
    assumptions such as working hours or time zone.

    Return exactly these sections:
    FIRST-WEEK ONBOARDING PLAN
    Status: READY, READY WITH ACTIONS, or BLOCKED
    Schedule: day/date, activity, owner, dependency, expected outcome
    Manager Preparation:
    Employee Deliverables:
    Blockers and Assumptions:
    Handoff to Reporting:
    """

    reporting_instructions = """
    You are the Onboarding Reporting coordinator and the final participant in
    the sequential workflow. Consolidate the employee record and every previous
    participant's output into one decision-ready report.

    Do not invent new facts, silently resolve conflicts, or describe planned work
    as completed. Reconcile duplicated information, preserve all blockers, and
    distinguish confirmed facts, proposed actions, assumptions, and approvals.
    Overall Status must be BLOCKED if any critical predecessor is blocked;
    otherwise use READY WITH ACTIONS until every action has an owner and due date.

    Return exactly these sections:
    FINAL ONBOARDING REPORT
    Overall Status: READY, READY WITH ACTIONS, or BLOCKED
    Employee Summary:
    HR Readiness:
    IT Provisioning Summary:
    Learning and Compliance Summary:
    First-Week Schedule Summary:
    Outstanding Actions: action, owner, due date, and dependency
    Risks and Escalations:
    Final Readiness Decision:
    """

    credential = AzureCliCredential()

    chat_client = FoundryChatClient(
        credential=credential,
        project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
        model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
    )

    hr_agent = chat_client.as_agent(name="HR Agent", instructions=hr_instructions)

    it_agent = chat_client.as_agent(name="IT Agent", instructions=it_instructions)

    learning_agent = chat_client.as_agent(
        name="Learning Agent", instructions=learning_instructions
    )

    manager_agent = chat_client.as_agent(
        name="Manager Agent", instructions=manager_instructions
    )

    reporting_agent = chat_client.as_agent(
        name="Reporting Agent", instructions=reporting_instructions
    )

    employee = """
    Name: John Smith
    Employee ID: E1024
    Department: Finance
    Role: Data Analyst
    Location: Bangalore
    Joining Date: 01-Oct-2026
    """

    workflow = SequentialBuilder(
        participants=[
            hr_agent,
            it_agent,
            learning_agent,
            manager_agent,
            reporting_agent,
        ],
        output_from="all",
    ).build()

    print("Starting the sequential onboarding workflow...", flush=True)

    current_agent = None
    async for event in workflow.run(employee, stream=True):
        if event.type != "output" or not event.data:
            continue

        if event.executor_id != current_agent:
            current_agent = event.executor_id
            display_name = (current_agent or "Agent").replace("_", " ").title()
            print(f"\n\n--- {display_name} is working ---\n", flush=True)

        text = getattr(event.data, "text", str(event.data))
        if text:
            print(text, end="", flush=True)

    print("\n\nWorkflow completed.", flush=True)


if __name__ == "__main__":
    asyncio.run(main())

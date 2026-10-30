
from agno.agent import Agent
from agno.team import Team
from agno.team.mode import TeamMode
from agno.models.groq import Groq
from agno.media import Image

from app.config import settings
from app.agents.tools import search_pubmed


DISCLAIMER = (
    "Educational demonstration only. This output is not a diagnosis, "
    "does not replace a radiologist or clinician, and must not guide treatment."
)


def build_agents():
    """Build the three specialist agents."""

    if not settings.groq_api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to the .env file."
        )

    vision_model = Groq(
        id=settings.groq_model,
        api_key=settings.groq_api_key,
    )

    text_model = Groq(
        id=settings.groq_text_model,
        api_key=settings.groq_api_key,
    )

    analyzer = Agent(
        name="Medical Image Analyzer",
        role="Describe visible image features cautiously; do not diagnose.",
        model=vision_model,
        instructions=[
            "You are an educational medical-image observation assistant.",
            "Describe only visible features.",
            "State modality, anatomy, plane or sequence as uncertain when not inferable.",
            "Do not claim to exclude stroke, tumor, hemorrhage, or disease from a single image.",
            "Mention that complete DICOM series, acquisition parameters, and clinical history are unavailable.",
            "Never provide treatment or triage instructions.",
            "Return your observations as plain text.",
        ],
        markdown=True,
    )

    researcher = Agent(
        name="Medical Research Agent",
        role="Find relevant peer-reviewed medical literature using PubMed.",
        model=text_model,
        tools=[search_pubmed],
        instructions=[
            "Use the search_pubmed tool for relevant literature searches.",
            "Only cite sources returned by the tool.",
            "Never invent article titles, authors, dates, or links.",
            "Distinguish general educational literature from evidence about an individual image.",
            "If search fails or returns no results, state that clearly.",
            "Return your findings as plain text.",
        ],
        markdown=True,
    )

    reviewer = Agent(
        name="Medical Report Reviewer",
        role="Audit image observations and literature for unsupported claims.",
        model=text_model,
        instructions=[
            "Review the supplied image observations and research findings.",
            "Remove unsupported diagnostic certainty and unsupported citations.",
            "Do not convert a model observation into a diagnosis.",
            "Highlight limitations and recommend qualified clinician review.",
            "Return these sections:",
            "Image/Region",
            "Visible Observations",
            "Evidence Context",
            "Limitations",
            "Educational Summary",
            "Include the mandatory disclaimer.",
            "Return the report as plain text.",
        ],
        markdown=True,
    )

    return analyzer, researcher, reviewer


def build_medical_team() -> Team:
    """Build the Agno multi-agent team for text-based questions."""

    analyzer, researcher, reviewer = build_agents()

    text_model = Groq(
        id=settings.groq_text_model,
        api_key=settings.groq_api_key,
    )

    return Team(
        name="MedAssist Medical Healthcare Team",
        mode=TeamMode.coordinate,
        model=text_model,
        members=[analyzer, researcher, reviewer],
        instructions=[
            "Coordinate the three specialist agents.",
            "Delegate relevant literature searches to Medical Research Agent.",
            "Ask Medical Report Reviewer to audit the final response.",
            "Do not state a diagnosis, treatment, or patient-specific clinical recommendation.",
            "Include only real source URLs returned by PubMed.",
        ],
        show_members_responses=True,
        markdown=True,
    )


def extract_text(result) -> str:
    """Safely extract text from an Agno run result."""

    content = getattr(result, "content", None)

    if content is None:
        raise RuntimeError("An agent returned an empty response.")

    if isinstance(content, str):
        return content

    return str(content)


def run_image_team(question: str, image_path: str) -> str:
    """
    Sequential multimodal workflow:
    1. Analyzer receives the image.
    2. Researcher receives text observations.
    3. Reviewer receives both text reports.
    """

    analyzer, researcher, reviewer = build_agents()

    # Stage 1: Only the vision agent receives the image.
    image_result = analyzer.run(
        question,
        images=[Image(filepath=image_path)],
    )

    image_observations = extract_text(image_result)

    # Stage 2: Research agent receives text only.
    research_result = researcher.run(
        "Based on these general image observations, find relevant "
        "educational medical literature using PubMed where appropriate.\n\n"
        f"User question: {question}\n\n"
        f"Image observations:\n{image_observations}"
    )

    research_findings = extract_text(research_result)

    # Stage 3: Reviewer receives plain-text outputs only.
    review_result = reviewer.run(
        "Review and synthesize the following reports.\n\n"
        f"User question:\n{question}\n\n"
        f"Image observations:\n{image_observations}\n\n"
        f"Research findings:\n{research_findings}\n\n"
        f"Mandatory disclaimer:\n{DISCLAIMER}"
    )

    final_report = extract_text(review_result)

    return final_report + "\n\n" + DISCLAIMER


def run_question_team(question: str) -> str:
    """Run the coordinated team for text-only questions."""

    team = build_medical_team()
    result = team.run(question)

    return extract_text(result)

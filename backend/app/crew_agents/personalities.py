try:
    from crewai import Agent
except ImportError:  # pragma: no cover - optional dependency
    Agent = None

if Agent is not None:
    AGGRESSOR = Agent(
        role="Ludo Aggressor",
        goal="Cut opponents at every opportunity, take risks, dominate the board.",
        backstory="You love crushing enemy tokens and show no mercy.",
        allow_delegation=False,
        verbose=False,
    )

    SAFE_PLAYER = Agent(
        role="Ludo Safe Player",
        goal="Prioritize safety, avoid cuts, slowly advance all tokens.",
        backstory="You prefer safe paths, never take unnecessary risks.",
        allow_delegation=False,
        verbose=False,
    )
else:
    AGGRESSOR = {"role": "Ludo Aggressor"}
    SAFE_PLAYER = {"role": "Ludo Safe Player"}
"""Quick start example: evaluate a single image."""

from evalmedia import ImageEval
from evalmedia.checks.image import (
    FaceArtifacts,
    PromptAdherence,
    ResolutionAdequacy,
    TextLegibility,
)

# Evaluate with specific checks
result = ImageEval.run(
    image="output.png",  # accepts path, URL, PIL.Image, bytes, base64
    prompt="a woman holding a coffee cup in a cafe",
    checks=[
        PromptAdherence(),
        FaceArtifacts(),
        TextLegibility(),
        ResolutionAdequacy(min_width=1024, min_height=1024),
    ],
)

# Overall result
print(f"Passed: {result.passed}")
print(f"Score: {result.overall_score:.2f}")
print(f"Summary: {result.summary()}")

# Individual check results
for check_result in result.check_results:
    print(f"\n  {check_result.name}:")
    print(f"    Status: {check_result.status.value}")
    print(f"    Score: {check_result.score}")
    print(f"    Reasoning: {check_result.reasoning}")

# Agent-friendly JSON
import json
print(json.dumps(result.to_dict(), indent=2))

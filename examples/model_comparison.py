"""Example: compare outputs from different image generation models."""

import asyncio

from evalmedia import compare
from evalmedia.rubrics import GeneralQuality


async def compare_models():
    """Compare images from 3 different models on the same prompt."""

    prompt = "a sunset over mountains with a lake in the foreground"

    results = await compare(
        images=[
            "model_a_output.png",
            "model_b_output.png",
            "model_c_output.png",
        ],
        prompt=prompt,
        rubric=GeneralQuality(),
        labels=["DALL-E 3", "Midjourney", "Stable Diffusion"],
    )

    # Print rankings
    print("Rankings:")
    for rank, (label, result) in enumerate(results.rankings, 1):
        status = "PASS" if result.passed else "FAIL"
        print(f"  {rank}. {label}: {result.overall_score:.2f} ({status})")

    # Best model
    best_label, best_result = results.best()
    print(f"\nBest: {best_label} (score: {best_result.overall_score:.2f})")


if __name__ == "__main__":
    asyncio.run(compare_models())

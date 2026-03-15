"""Example: AI agent workflow — generate, evaluate, retry."""

import asyncio

from evalmedia import ImageEval
from evalmedia.rubrics import Portrait


async def generate_and_evaluate():
    """Simulated agent workflow: generate -> evaluate -> retry if needed."""

    prompt = "professional headshot of a young woman, studio lighting"
    max_retries = 3

    for attempt in range(1, max_retries + 1):
        print(f"\n--- Attempt {attempt}/{max_retries} ---")

        # Step 1: Generate image (simulated — replace with actual generation)
        image_path = f"output_attempt_{attempt}.png"
        print(f"Generated: {image_path}")

        # Step 2: Evaluate with Portrait rubric
        result = await ImageEval.arun(
            image=image_path,
            prompt=prompt,
            rubric=Portrait(),
        )

        print(f"Score: {result.overall_score:.2f}")
        print(f"Passed: {result.passed}")

        if result.passed:
            print("Image passed quality checks. Shipping!")
            return result

        # Step 3: Use suggestions to adjust
        print("Failed checks:")
        for suggestion in result.suggestions:
            print(f"  - {suggestion}")

        # An agent would modify the prompt or generation parameters here
        print("Retrying with adjusted parameters...")

    print("Max retries reached. Using best attempt.")
    return result


if __name__ == "__main__":
    asyncio.run(generate_and_evaluate())

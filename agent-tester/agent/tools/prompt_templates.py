def refine_seed_prompt(original_seeds: list[str], crash_inputs: list[str], max_out=5) -> str:
    original_formatted = "\n".join(f"- {s}" for s in original_seeds)
    crash_formatted = "\n".join(f"- {s}" for s in crash_inputs)

    prompt = (
        "You're assisting with fuzzing a C program. We previously tested it with the following seed inputs:\n\n"
        f"{original_formatted}\n\n"
        "These inputs led to the following interesting or crashing behaviors:\n\n"
        f"{crash_formatted}\n\n"
        f"Generate {max_out} refined or mutated inputs that are likely to explore new paths or edge cases.\n"
        "Return only raw inputs, separated by `---`.\n"
    )

    return prompt

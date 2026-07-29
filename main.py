from pipeline import run_pipeline


def main():
    print("=" * 55)
    print("Welcome to the LinkedIn Post Generator")
    print("=" * 55)
    print("\nThis tool will draft a LinkedIn post for you, review it")
    print("itself, and iterate until it's publish-ready.")
    print("=" * 55)

    topic = input("\nWhat topic do you want a LinkedIn post about?\n> ").strip()

    if not topic:
        print("\nNo topic given. Exiting.")
        return

    print("\nStarting generation...\n")

    final_state = run_pipeline(topic)

    print("\n" + "=" * 55)
    print("FINAL LINKEDIN POST")
    print("=" * 55)
    print(final_state["draft"])
    print("=" * 55)
    print(f"Total attempts: {final_state['attempt']}")
    print(f"Approved: {final_state['is_approved']}")


if __name__ == "__main__":
    main()

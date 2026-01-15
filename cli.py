#!/usr/bin/env python3
"""EU AI Act Compliance Advisor - Command Line Interface."""

import logging
from src.legal_advisor import LegalAdvisor, MIN_QUESTIONS, MAX_QUESTIONS, CONFIDENCE_THRESHOLD

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main():
    print("\n" + "="*60)
    print("EU AI ACT COMPLIANCE ADVISOR".center(60))
    print("="*60)

    try:
        advisor = LegalAdvisor()
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        print("\nPossible causes:")
        print("- Ollama not running (start: ollama serve)")
        print("- Model not installed (install: ollama pull llama3.1:8b)")
        print("- PDF file missing")
        return

    print(f"✅ System ready")
    print(f"📚 AI Act chunks: {len(advisor.ai_act_chunks)}")
    print(f"⚙️  Questions range: {MIN_QUESTIONS}-{MAX_QUESTIONS}")
    print(f"🎯 Confidence threshold: {CONFIDENCE_THRESHOLD}")
    print("="*60)
    print("Commands: 'reset' (new assessment) | 'quit' (exit)")
    print("="*60)

    initial_prompt = """Please describe your AI system in detail. Include:

• Primary purpose and functionality
• Technical approach (ML model type, algorithms)
• Data processed (types, sources, sensitivity)
• Deployment context (where, when, who uses it)
• Decision-making role (automated, human-in-loop)
• Potential impact on individuals

Be specific to enable accurate risk classification."""

    print(f"\n🤖 Analyst: {initial_prompt}\n")
    current_question = initial_prompt
    awaiting_prohibited_confirmation = False

    while True:
        try:
            user_input = input("👤 You: ").strip()

            if not user_input:
                print("⚠️  Please provide an answer.\n")
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for using EU AI Act Compliance Advisor.")
                break

            if user_input.lower() == 'reset':
                advisor.reset()
                print("\n" + "="*60)
                print("🔄 System reset. Ready for new assessment.")
                print("="*60)
                print(f"\n🤖 Analyst: {initial_prompt}\n")
                current_question = initial_prompt
                awaiting_prohibited_confirmation = False
                continue

            if not advisor.model_description:
                response, is_prohibited_warning = advisor.process_initial_description(user_input)

                if is_prohibited_warning:
                    print(f"\n{response}\n")
                    awaiting_prohibited_confirmation = True
                    continue

                advisor.model_description = user_input
                next_question, is_done = advisor.ask_next_question()

                if is_done:
                    print("\n" + "="*60)
                    print("📊 FINAL COMPLIANCE ASSESSMENT")
                    print("="*60)
                    print(f"\n{next_question}\n")
                    print("="*60)
                    print("Type 'reset' for new assessment | 'quit' to exit")
                    print("="*60 + "\n")
                else:
                    current_question = next_question
                    progress = f"[Question {len(advisor.interview_history)+1}/{MAX_QUESTIONS}]"
                    print(f"\n🤖 Analyst {progress}: {next_question}\n")
                continue

            if awaiting_prohibited_confirmation:
                if user_input.lower() in ['yes', 'y', 'continue']:
                    awaiting_prohibited_confirmation = False
                    next_question, is_done = advisor.ask_next_question()
                    if not is_done:
                        current_question = next_question
                        progress = f"[Question {len(advisor.interview_history)+1}/{MAX_QUESTIONS}]"
                        print(f"\n🤖 Analyst {progress}: {next_question}\n")
                    continue
                elif user_input.lower() in ['no', 'n']:
                    # Generate final prohibited report
                    print("\n" + "="*60)
                    print("📊 FINAL COMPLIANCE ASSESSMENT")
                    print("="*60)
                    final_report = advisor.generate_prohibited_final_report()
                    print(f"\n{final_report}\n")
                    print("="*60)
                    print("Type 'reset' for new assessment | 'quit' to exit")
                    print("="*60 + "\n")
                    awaiting_prohibited_confirmation = False
                    advisor.reset()
                    continue
                else:
                    print("⚠️  Please answer 'yes' to continue or 'no' to cancel.\n")
                    continue

            next_question, is_done = advisor.process_answer(user_input, current_question)

            if is_done:
                print("\n" + "="*60)
                print("📊 FINAL COMPLIANCE ASSESSMENT")
                print("="*60)
                print(f"\n{next_question}\n")
                print("="*60)
                print("Type 'reset' for new assessment | 'quit' to exit")
                print("="*60 + "\n")
            else:
                current_question = next_question
                progress = f"[Question {len(advisor.interview_history)+1}/{MAX_QUESTIONS}]"
                confidence_info = " 🎯" if len(advisor.interview_history) >= MIN_QUESTIONS else ""
                print(f"\n🤖 Analyst {progress}{confidence_info}: {next_question}\n")

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted. Type 'quit' to exit or 'reset' to start over.\n")
            continue
        except ConnectionError as e:
            print(f"\n❌ Connection Error: {e}")
            print("\n🔧 Troubleshooting:")
            print("   1. Check if Ollama is running: ollama serve")
            print("   2. Verify model is installed: ollama list")
            print("   3. Check OLLAMA_URL in .env file\n")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("Type 'reset' to start over or 'quit' to exit.\n")

    print("\n" + "="*60)
    print("Session ended. Goodbye!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

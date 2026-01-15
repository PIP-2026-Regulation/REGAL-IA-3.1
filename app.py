"""EU AI Act Compliance Advisor - Web Interface."""

import os
import logging
import gradio as gr
from dotenv import load_dotenv

from src.legal_advisor import LegalAdvisor

load_dotenv(override=True)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Global state
advisor = None
current_question = ""
awaiting_confirmation = False

def get_initial_prompt():
    return """Please describe your AI system in detail. Include:
- Primary purpose and functionality
- Technical approach (ML model type, algorithms)
- Data processed (types, sources, sensitivity)
- Deployment context (where, when, who uses it)
- Decision-making role (automated, human-in-loop)
- Potential impact on individuals

Be specific to enable accurate risk classification."""


def respond(message, chat_history):
    global advisor, current_question, awaiting_confirmation

    if advisor is None:
        try:
            advisor = LegalAdvisor()
        except Exception as e:
            chat_history.append((message, f"❌ Initialization failed: {e}"))
            return "", chat_history

    if not message.strip():
        return "", chat_history

    # Handle reset
    if message.lower() == 'reset':
        advisor.reset()
        current_question = get_initial_prompt()
        awaiting_confirmation = False
        return "", [(None, f"🔄 System reset.\n\n{current_question}")]

    # Handle prohibited confirmation
    if awaiting_confirmation:
        if message.lower() in ['yes', 'y']:
            awaiting_confirmation = False
            next_q, is_done = advisor.ask_next_question()
            if is_done:
                chat_history.append((message, f"📊 **FINAL ASSESSMENT**\n\n{next_q}"))
            else:
                current_question = next_q
                progress = advisor.get_progress()
                chat_history.append((message, f"[Q{progress['questions_asked']+1}/{progress['max_questions']}]\n\n{next_q}"))
        elif message.lower() in ['no', 'n']:
            # Generate final prohibited report
            awaiting_confirmation = False
            final_report = advisor.generate_prohibited_final_report()
            chat_history.append((message, f"📊 **FINAL ASSESSMENT - PROHIBITED SYSTEM**\n\n{final_report}"))
            advisor.reset()
        else:
            awaiting_confirmation = False
            advisor.reset()
            chat_history.append((message, "⚠️ Assessment cancelled. Type your system description to start again."))
        return "", chat_history

    # Initial description
    if not advisor.model_description:
        response, is_prohibited = advisor.process_initial_description(message)

        if is_prohibited:
            awaiting_confirmation = True
            chat_history.append((message, response))
            return "", chat_history

        advisor.model_description = message
        next_q, is_done = advisor.ask_next_question()

        if is_done:
            chat_history.append((message, f"📊 **FINAL ASSESSMENT**\n\n{next_q}"))
        else:
            current_question = next_q
            progress = advisor.get_progress()
            chat_history.append((message, f"✅ Description received.\n\n[Q{progress['questions_asked']+1}/{progress['max_questions']}] {next_q}"))
        return "", chat_history

    # Process answer
    try:
        next_q, is_done = advisor.process_answer(message, current_question)

        if is_done:
            chat_history.append((message, f"📊 **FINAL COMPLIANCE ASSESSMENT**\n\n{next_q}\n\n---\nType 'reset' to start a new assessment."))
        else:
            current_question = next_q
            progress = advisor.get_progress()
            emoji = "🎯" if progress['questions_asked'] >= progress['min_questions'] else ""
            chat_history.append((message, f"[Q{progress['questions_asked']+1}/{progress['max_questions']}]{emoji}\n\n{next_q}"))
    except Exception as e:
        chat_history.append((message, f"❌ Error: {e}"))

    return "", chat_history


# Create interface
with gr.Blocks(title="EU AI Act Compliance Advisor") as demo:
    gr.Markdown("# 🇪🇺 EU AI Act Compliance Advisor")
    gr.Markdown("Type `reset` to start a new assessment.")

    gr.Markdown(f"**🤖 Assistant:**\n\n{get_initial_prompt()}")

    chatbot = gr.Chatbot(height=400)
    msg = gr.Textbox(placeholder="Describe your AI system here...", show_label=False)

    msg.submit(respond, [msg, chatbot], [msg, chatbot])

    gr.Markdown("⚠️ *This tool provides preliminary guidance only.*")

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
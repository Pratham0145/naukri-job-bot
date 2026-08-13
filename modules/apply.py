import os
import time
from playwright.sync_api import Page
from config.settings import pause_before_submit, default_resume_path
from config.personals import (
    cover_letter, years_of_experience, current_ctc,
    expected_ctc, notice_period, phone_number,
)
from modules.helpers import log, random_sleep
from modules.browser import safe_click, safe_fill


def apply_to_job(page: Page, job: dict) -> tuple[bool, str]:
    url = job.get("url", "")
    title = job.get("title", "Unknown")
    company = job.get("company", "Unknown")

    log.info(f"\nApplying: {title} @ {company}")
    log.info(f"  URL: {url}")

    if "naukri.com" not in url:
        return False, "External job (skipped)"

    title = title.lower()

    # ❌ EXTRA SAFETY (VERY IMPORTANT)
    if any(x in title for x in ["director", "vp", "head", "principal"]):
        return False, "Skipped (senior role)"
    
    location = job.get("location", "").lower()

    if "bengaluru" not in location and "bangalore" not in location:
        return False, "Skipped (wrong location)"
    

    exp_text = page.locator("body").inner_text().lower()

    if any(x in exp_text for x in ["10 years", "15 years", "20 years"]):
        return False, "Skipped (high experience)"


    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        random_sleep(2)

        apply_btn = page.locator("button:has-text('Apply'), a:has-text('Apply')").first

        if apply_btn.count() == 0:
            return False, "Apply button not found"

        btn_text = apply_btn.inner_text().lower()

        if "company site" in btn_text:
            return False, "External apply (skipped)"

        if "applied" in btn_text:
            return False, "Already applied"

        apply_btn.click()
        random_sleep(2)

        return _handle_application_flow(page, job)

    except Exception as e:
        return False, str(e)


# ---------------- FLOW HANDLER ---------------- #

def _handle_application_flow(page: Page, job: dict):
    random_sleep(2)

    if _is_chatbot_apply(page):
        return _handle_chatbot_apply(page)

    if _is_modal_apply(page):
        return _handle_modal_apply(page, job)

    if _is_external_apply(page):
        return False, "External apply"

    return False, "Unknown flow"


def _is_chatbot_apply(page: Page):
    return page.locator("div[contenteditable='true']").count() > 0


def _is_modal_apply(page: Page):
    return page.locator(".apply-modal, .apply-form").count() > 0


def _is_external_apply(page: Page):
    return "naukri.com" not in page.url


# ---------------- CHATBOT ---------------- #



def _handle_chatbot_apply(page):
    log.info("  → Chatbot apply flow detected")

    chatbot = page.locator("div.chatbot_Drawer, div._chatBotContainer")
    prev_question = ""

    for step in range(60):
        page.wait_for_timeout(1500)

        # ===== SUCCESS CHECK =====
        body_text = page.inner_text("body").lower()
        if "successfully applied" in body_text or "application submitted" in body_text:
            return True, "Applied successfully"

        # ===== GET QUESTION =====
        question = ""
        try:
            question = chatbot.locator(".botMsg span").last.inner_text().strip()
        except:
            pass

        log.info(f"  Q: {question}")

        # ===== EMPTY QUESTION =====
        if not question:
            log.warning("⚠️ No question — checking status")

            body = page.inner_text("body").lower()

            if "applied" in body or "submitted" in body:
                return True, "Applied"

            return False, "Flow ended"

        q_lower = question.lower()

        # ===== LOOP DETECTION =====
        if question == prev_question:
            log.warning("⚠️ Same question → forcing submit")

            page.keyboard.press("Enter")

            save_btn = chatbot.locator("div.sendMsg:has-text('Save')")
            if save_btn.count() > 0:
                save_btn.first.click(force=True)

            page.wait_for_timeout(1500)
            continue

        prev_question = question
        # ===== GENERATE ANSWER =====
        answer = ""

        try:
            # 🔥 LLM first
            answer = llm_answer(question)
            log.info(f"  → LLM Answer: {answer}")
        except:
            answer = "3"

        # 🔥 RULE OVERRIDE (VERY IMPORTANT)
        if "date of birth" in q_lower:
            answer = "25/08/2000"

        elif "experience" in q_lower:
            answer = "3"

        elif "ctc" in q_lower or "salary" in q_lower:
            answer = "10 LPA"

        elif "location" in q_lower:
            answer = "Bangalore"

        elif "name" in q_lower:
            answer = "Prathamesh"

        log.info(f"  → Final Answer: {answer}")


        # ================= TEXT INPUT =================
        chat_input = chatbot.locator("div[contenteditable='true']").first

        if chat_input.count() > 0:
            try:
                chat_input.wait_for(state="visible", timeout=5000)

                # 🔥 CLICK INPUT (NOT RANDOM CLICK)
                chat_input.click(force=True)

                page.wait_for_timeout(300)

                # # 🔥 CLEAR INPUT
                # page.keyboard.press("Control+A")
                # page.keyboard.press("Backspace")

                # fallback clear
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")

                log.info(f"  → Typing: {answer}")

                # 🔥 TYPE INTO CHAT INPUT
                chat_input.type(str(answer), delay=50)

                page.wait_for_timeout(500)

                # 🔥 CLICK SAVE (DON’T RELY ONLY ON ENTER)
                save_btn = chatbot.locator("div.sendMsg:has-text('Save')")

                if save_btn.count() > 0:
                    save_btn.first.click(force=True)
                    log.info("  → Save clicked")
                else:
                    page.keyboard.press("Enter")

                page.wait_for_timeout(1500)

                continue

            except Exception as e:
                log.debug(f"input failed: {e}")

        # ================= OPTIONS (LLM BASED) =================
        try:
            labels = chatbot.locator("label").all()

            clean_options = []
            label_map = {}

            for lbl in labels:
                try:
                    txt = lbl.inner_text().strip()
                    if len(txt) < 2:
                        continue

                    clean_options.append(txt)
                    label_map[txt] = lbl
                except:
                    continue

            if clean_options:
                log.info(f"  → Options: {clean_options}")

                # 🔥 LLM SELECT OPTION
                try:
                    selected_text = llm_select_option(question, clean_options)
                    log.info(f"  → LLM Selected: {selected_text}")
                except:
                    selected_text = clean_options[0]

                selected = False

                for opt_text, lbl in label_map.items():
                    if selected_text.lower() in opt_text.lower():
                        lbl.click(force=True)
                        selected = True
                        break

                if not selected:
                    label_map[clean_options[0]].click(force=True)

                page.wait_for_timeout(800)

                # SAVE
                save_btn = chatbot.locator("div.sendMsg:has-text('Save')")
                if save_btn.count() > 0:
                    save_btn.first.click(force=True)
                else:
                    page.keyboard.press("Enter")

                continue

        except Exception as e:
            log.debug(f"options failed: {e}")

        # ================= NEXT BUTTON =================
        try:
            next_btn = chatbot.locator("button:has-text('Next'), button:has-text('Continue')")
            if next_btn.count() > 0:
                next_btn.first.click(force=True)
                continue
        except:
            pass

    return False, "Chatbot flow incomplete"
            


# ---------------- ANSWERS ---------------- #

def _guess_answer(question: str) -> str:
    q = question.lower()

    if "experience" in q:
        if "nlp" in q:
            return "2"
        if "e-commerce" in q:
            return "1"
        return "3"

    if "notice" in q:
        return notice_period

    if "ctc" in q:
        return expected_ctc

    if "skill" in q:
        return "Python, Machine Learning, NLP, GenAI"

    if "name" in q:
        return "Prathamesh"

    return "3"


def _pick_best_option(options, question=""):
    q = question.lower()

    for opt in options:
        try:
            txt = opt.inner_text().lower()

            if "notice" in q:
                if "15" in txt or "immediate" in txt:
                    return opt
                if "1 month" in txt:
                    return opt

            if "yes" in txt:
                return opt

        except:
            continue

    return options[0] if options else None


# ---------------- SUBMIT CHECK ---------------- #

def _check_submitted(page: Page):
    try:
        text = page.locator("body").inner_text().lower()
        return "applied" in text or "submitted" in text
    except:
        return False


# ---------------- MODAL APPLY ---------------- #

def _handle_modal_apply(page: Page, job: dict):
    log.info("  → Modal apply flow detected")

    cl = page.locator("textarea").first
    if cl.count() > 0:
        cl.fill(cover_letter)

    resume = page.locator("input[type='file']").first
    if resume.count() > 0 and os.path.exists(default_resume_path):
        resume.set_input_files(default_resume_path)

    btn = page.locator("button:has-text('Submit'), button:has-text('Apply')").first

    if btn.count() == 0:
        return False, "No submit button"

    btn.click()
    time.sleep(2)

    if _check_submitted(page):
        return True, "Applied"

    return False, "Failed"





from groq import Groq
from config.secrets import GROQ_API_KEY
from config.llm_context import LLM_CONTEXT

client = Groq(api_key=GROQ_API_KEY)


def llm_answer(question: str) -> str:
    question = question.lower().strip()
    prompt = f"""
You are an AI job application assistant.

Use the candidate context below to answer.

{LLM_CONTEXT}

Question: {question}

Instructions:
- Answer SHORT (1 line)
- For experience → return ONLY number (e.g., 3)
- For yes/no → return Yes or No
- For notice → return exact (e.g., 30 days)
- For DOB → return 25/08/2000
- Do NOT explain

Answer:
"""

    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content.strip()

    except:
        return "3"




def llm_select_option(question, options):
    try:
        options_text = "\n".join(options)

        prompt = f"""
You are helping a candidate answer job application questions.

Candidate Context:
{LLM_CONTEXT}

Question:
{question}

Options:
{options_text}

Rules:
- Choose BEST matching option
- Return EXACT option text (copy from options)
- Do NOT explain

Answer:
"""

        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        return resp.choices[0].message.content.strip()
    except:
        return options[0]
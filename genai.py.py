import smtplib
import ssl
import csv
import time
import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import google.generativeai as genai # Import Gemini library

# --- Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465 # For SSL
SENDER_EMAIL = "amaljerry02@gmail.com"
CSV_FILE_PATH = "contacts.csv"
RESUME_FILE_PATH = "Amal_Resume (1).pdf"
YOUR_PHONE="8287089713"
YOUR_LINKEDIN="https://www.linkedin.com/in/amal-jerry02/"
# --- Gemini AI Configuration ---
try:
    GEMINI_API_KEY = "YOUR API KEY"

    genai.configure(api_key=GEMINI_API_KEY)
    # Choose a generation model (gemini-pro is good for text)
    gemini_model = genai.GenerativeModel('gemini-1.5-pro')
    print("Gemini API configured successfully.")
except Exception as e:
    print(f"ERROR: Failed to configure Gemini API: {e}")
    print("Please ensure the 'google-generativeai' library is installed and the GOOGLE_API_KEY environment variable is set.")
    exit() # Exit if Gemini cannot be configured

# --- Information for Personalization ---
YOUR_NAME = "Amal Jerry"
# Be specific! What are 1-3 core skills you want to highlight?
YOUR_KEY_SKILLS = "Python development, data analysis, and cloud infrastructure management"
# What type of role or area are you generally targeting?
YOUR_FOCUS_AREA = "software engineering or data science roles"
# Optional: Add a sentence about your general career goal or interest
YOUR_OBJECTIVE = "seeking a challenging role where I can leverage my technical skills to contribute to innovative projects."


# --- Email Content ---
# Subject template remains the same
EMAIL_SUBJECT_TEMPLATE = "Job Application: Interested in Opportunities at {company_name}"

# --- Function to Generate Email Body using Gemini ---
def generate_custom_email_body(company_name, applicant_name, key_skills, focus_area, objective):
    """Uses Gemini API to generate a personalized email body."""

    # --- **CRITICAL: Design a good prompt!** ---
    # This prompt guides the AI. Be specific about what you want.
    prompt = f"""
    Generate 2-3 personalized paragraphs for the body of a speculative job application cover letter from Amal Jerry.

    **Applicant Profile (Amal Jerry):**
    -   **Name:** {applicant_name}
    -   **Core Expertise:** Machine Learning, specializing in Generative AI. Holds a Google Cloud Generative AI certification.
    -   **Key Technical Skills:** {key_skills}.
    -   **Relevant Project Experience:**
        *   Fine-tuned LLMs (using Gemini API) for chatbots, including mood/emotional pattern detection. Developed associated GUI.
        *   Built recommendation systems using TF-IDF, hybrid filtering, and ARHR analysis.
        *   Worked on audio stem separation and spatial audio conversion using LSTMs and Hybrid Demucs.
    -   **Education:** Pursuing B.Tech in Computer Science (Expected 2025).
    -   **Target Roles:** {focus_area}.
    -   **Career Objective:** {objective}.

    **Target Company:** "{company_name}"

    **Instructions for Generation:**
    1.  **Opening:** Start by expressing strong interest in potential {focus_area} roles at {company_name}. Briefly and plausibly mention *why* {company_name} is appealing to someone with Amal's background (e.g., mention the company's known work in AI/ML, their industry, innovative projects, or alignment with GenAI focus if applicable - **the AI might invent something plausible, REVIEW IT CAREFULLY!**).
    2.  **Skill Connection:** Connect Amal's specific skills and project experiences (especially **Generative AI/LLM fine-tuning with Gemini API**, recommendation systems, or audio ML) to the likely needs or work done at {company_name}. Highlight the practical application shown in the projects. Mentioning the Google Cloud GenAI certification could be beneficial if relevant to the company.
    3.  **Enthusiasm & Fit:** Convey enthusiasm for contributing to {company_name} and alignment with the stated objective.
    4.  **Tone:** Maintain a professional, confident, and enthusiastic tone.
    5.  **Exclusions:**
        *   **DO NOT** include the opening salutation (like "Dear Hiring Manager,").
        *   **DO NOT** include the closing (like "Sincerely," or contact info).
        *   **DO NOT** explicitly mention the resume attachment (the main script adds this).
        *   **DO NOT** give instructions inside the response.
    6.  **Length:** Keep the total generated text concise, around 100-170 words. Focus on impact.
    """

    print(f"Generating email body for {company_name} using Gemini...")
    try:
        response = gemini_model.generate_content(prompt)
        # Basic check if the response has text
        if response.parts:
             generated_text = response.text.strip()
             print("--- Gemini Generated Text ---")
             print(generated_text)
             print("-----------------------------")
             # Add a small safety check for empty generation
             if not generated_text:
                 print("WARNING: Gemini returned an empty response.")
                 return None
             return generated_text
        else:
            # Handle cases where the generation might be blocked due to safety settings
            print(f"WARNING: Gemini generation might have been blocked. Response: {response}")
            # You might want to inspect response.prompt_feedback here
            return None

    except Exception as e:
        print(f"ERROR: Gemini API call failed: {e}")
        return None # Return None to indicate failure


# --- Function to Send Email (Modified) ---
def send_application_email(recipient_email, company_name, sender_email, sender_password):
    """Generates personalized body using Gemini and sends email with resume."""

    # --- Generate Personalized Body ---
    generated_body_part = generate_custom_email_body(
        company_name=company_name,
        applicant_name=YOUR_NAME,
        key_skills=YOUR_KEY_SKILLS,
        focus_area=YOUR_FOCUS_AREA,
        objective=YOUR_OBJECTIVE
    )

    if not generated_body_part:
        print(f"Skipping email to {recipient_email} due to body generation failure.")
        return False # Indicate failure

    # --- Construct the Full Email Body ---
    # Combine standard opening/closing with the AI-generated part
    full_email_body = f"""
Dear Hiring Manager at {company_name},

I hope this email finds you well.

{generated_body_part}

I have attached my resume for your review, which provides further detail on my qualifications and accomplishments. I am eager to learn more about potential opportunities where my skills can benefit {company_name}.

Thank you for your time and consideration. I look forward to hearing from you soon.

PS:This mail is sent using an AI Agent I created :)

Sincerely,

{YOUR_NAME}
{YOUR_PHONE}
{YOUR_LINKEDIN}
"""
    # --- End Body Construction ---


    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = EMAIL_SUBJECT_TEMPLATE.format(company_name=company_name)

    # Add the email body
    message.attach(MIMEText(full_email_body, 'plain'))

    # --- Attach the resume ---
    attachment_path = RESUME_FILE_PATH
    try:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        resume_filename = os.path.basename(attachment_path)
        part.add_header("Content-Disposition", f"attachment; filename= {resume_filename}")
        message.attach(part)
        print(f"Successfully attached resume: {resume_filename}")
    except FileNotFoundError:
        print(f"ERROR: Resume file not found at {attachment_path}. Skipping attachment.")
    except Exception as e:
        print(f"ERROR: Could not attach resume file: {e}")
    # --- Attachment End ---


    # --- Send the email ---
    try:
        context = ssl.create_default_context()
        print(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT}...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            print("Logging in...")
            server.login(sender_email, sender_password)
            print("Sending email...")
            server.sendmail(sender_email, recipient_email, message.as_string())
            print(f"Email successfully sent to {recipient_email} for {company_name}")
            return True # Indicate success
    except smtplib.SMTPAuthenticationError:
        print("ERROR: SMTP Authentication Failed. Check email/password (or App Password).")
        # Important: Stop the script if login fails to avoid locking account
        raise # Re-raise the exception to stop the script
    except smtplib.SMTPConnectError:
        print(f"ERROR: Could not connect to the SMTP server {SMTP_SERVER}:{SMTP_PORT}.")
        return False
    except Exception as e:
        print(f"ERROR: An error occurred while sending email to {recipient_email}: {e}")
        return False
    # --- Sending End ---

# --- Main Script Execution ---
if __name__ == "__main__":
    # Securely get the SMTP password
    sender_password = getpass.getpass(f"Enter SMTP password (or App Password) for {SENDER_EMAIL}: ")

    emails_sent_count = 0
    emails_failed_count = 0
    total_processed = 0

    try:
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)

            try:
                email_col_index = header.index('email')
                company_col_index = header.index('company_name')
            except ValueError as e:
                print(f"ERROR: CSV header is missing required columns ('email', 'company_name'). Details: {e}")
                exit()

            print(f"\nStarting email sending process from {CSV_FILE_PATH}...")
            print("--- IMPORTANT: Review each AI-generated body before it's sent! ---")

            for i, row in enumerate(reader):
                total_processed += 1
                try:
                    recipient_email = row[email_col_index].strip()
                    company_name = row[company_col_index].strip()

                    if not recipient_email or not company_name:
                        print(f"WARNING: Skipping row {i+2} due to missing email or company name.")
                        emails_failed_count += 1
                        continue

                    print(f"\n--- Processing Row {i+2}: {company_name} ({recipient_email}) ---")

                    # --- Send the email ---
                    # Wrap send_application_email in a try-except to catch SMTP Auth errors early
                    try:
                        if send_application_email(recipient_email, company_name, SENDER_EMAIL, sender_password):
                            emails_sent_count += 1
                        else:
                            emails_failed_count += 1
                            print(f"Failed to send email to {recipient_email}.")
                    except smtplib.SMTPAuthenticationError:
                        # Stop the whole process if login fails
                        print("\nHalting script due to SMTP Authentication Failure.")
                        break # Exit the loop

                    # --- IMPORTANT: Delay ---
                    # Consider increasing delay if API calls take time or hit rate limits
                    delay_seconds = 3 # Increased delay
                    print(f"Waiting for {delay_seconds} seconds...")
                    time.sleep(delay_seconds)

                except IndexError:
                    print(f"WARNING: Skipping row {i+2} due to incorrect number of columns.")
                    emails_failed_count += 1
                    continue
                except Exception as e:
                    print(f"ERROR: An unexpected error occurred processing row {i+2}: {e}")
                    emails_failed_count += 1
                    # time.sleep(60) # Optional longer delay after an error


    except FileNotFoundError:
        print(f"ERROR: CSV file not found at {CSV_FILE_PATH}")
    except Exception as e:
        print(f"ERROR: An critical error occurred: {e}")


    print("\n--- Sending Process Finished ---")
    print(f"Total rows processed: {total_processed}")
    print(f"Emails successfully sent: {emails_sent_count}")
    print(f"Emails failed/skipped: {emails_failed_count}")
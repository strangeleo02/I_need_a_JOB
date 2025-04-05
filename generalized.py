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
# Removed: import google.generativeai as genai

# --- Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465 # For SSL
SENDER_EMAIL = "amaljerry02@gmail.com" # Replace with your email if needed
CSV_FILE_PATH = "contacts.csv"
RESUME_FILE_PATH = "Amal_Resume (1).pdf" # Make sure this path is correct
YOUR_PHONE = "8287089713" # Replace with your phone if needed
YOUR_LINKEDIN = "https://www.linkedin.com/in/amal-jerry02/" # Replace with your LinkedIn if needed

# --- Information for Personalization (Used in the generalized template) ---
YOUR_NAME = "Amal Jerry"
# Be specific! What are 1-3 core skills you want to highlight?
YOUR_KEY_SKILLS = "Machine Learning, Python development, and Generative AI concepts"
# What type of role or area are you generally targeting?
YOUR_FOCUS_AREA = "Machine Learning or software engineering roles"
# Optional: Add a sentence about your general career goal or interest
YOUR_OBJECTIVE = "seeking a challenging role where I can leverage my technical skills to contribute to innovative projects, particularly at the intersection of AI and practical problem-solving."

# --- Email Content ---
# Subject template remains the same
EMAIL_SUBJECT_TEMPLATE = "Job Application: Interested in Opportunities at {company_name}"

# --- Generalized Email Body Template ---
# This template will be used for all emails, only {company_name} will change.
# It incorporates the YOUR_ variables defined above.
GENERALIZED_EMAIL_BODY_TEMPLATE = """
Dear Hiring Manager at {company_name},

I hope this email finds you well.

I am writing to express my strong interest in exploring potential {focus_area} at {company_name}. As a motivated B.Tech Computer Science student (expected 2025) with a passion for {key_skills}, I am actively seeking challenging opportunities where I can apply my knowledge and contribute effectively.

My resume, attached for your review, details my project experience in areas such as recommendation systems, LLM fine-tuning (using APIs like Gemini), and audio processing, along with my technical skill set including Python, TensorFlow, PyTorch, and Google Cloud (holding a Generative AI certification).

I am particularly drawn to {company_name} and am eager to learn how my skills and enthusiasm align with your team's goals. My objective is {objective}.

Thank you for your time and consideration. I look forward to the possibility of discussing opportunities further.

PS: This mail is sent using an automated script I created :)

Sincerely,

{your_name}
{your_phone}
{your_linkedin}
"""

# --- Function to Send Email (Modified - No AI Call) ---
def send_application_email(recipient_email, company_name, sender_email, sender_password):
    """Constructs and sends a generalized email with resume."""

    # --- Construct the Full Email Body using the template ---
    full_email_body = GENERALIZED_EMAIL_BODY_TEMPLATE.format(
        company_name=company_name,
        focus_area=YOUR_FOCUS_AREA,
        key_skills=YOUR_KEY_SKILLS,
        objective=YOUR_OBJECTIVE,
        your_name=YOUR_NAME,
        your_phone=YOUR_PHONE,
        your_linkedin=YOUR_LINKEDIN
    )
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
        # Decide if you want to send the email without the attachment or skip
        # return False # Uncomment this line to skip email if resume is missing
    except Exception as e:
        print(f"ERROR: Could not attach resume file: {e}")
        # Decide if you want to send the email without the attachment or skip
        # return False # Uncomment this line to skip email if attachment fails
    # --- Attachment End ---


    # --- Send the email ---
    try:
        context = ssl.create_default_context()
        print(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT}...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            print("Logging in...")
            server.login(sender_email, sender_password)
            print(f"Sending generalized email to {recipient_email} for {company_name}...")
            # print("--- Email Body ---") # Optional: uncomment to preview body before sending
            # print(full_email_body)
            # print("------------------")
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
            try:
                header = next(reader) # Read the header row
            except StopIteration:
                print(f"ERROR: CSV file '{CSV_FILE_PATH}' is empty.")
                exit()

            # Find column indices dynamically
            try:
                email_col_index = header.index('email')
                company_col_index = header.index('company_name')
            except ValueError as e:
                print(f"ERROR: CSV header in '{CSV_FILE_PATH}' is missing required columns ('email', 'company_name'). Found header: {header}. Details: {e}")
                exit()

            print(f"\nStarting generalized email sending process from {CSV_FILE_PATH}...")

            for i, row in enumerate(reader):
                row_number = i + 2 # Account for header row and 0-based index
                total_processed += 1
                try:
                    # Ensure row has enough columns before accessing them
                    if len(row) <= max(email_col_index, company_col_index):
                         print(f"WARNING: Skipping row {row_number} due to insufficient columns. Row data: {row}")
                         emails_failed_count += 1
                         continue

                    recipient_email = row[email_col_index].strip()
                    company_name = row[company_col_index].strip()

                    if not recipient_email or '@' not in recipient_email: # Basic email format check
                        print(f"WARNING: Skipping row {row_number} due to invalid or missing email: '{recipient_email}'.")
                        emails_failed_count += 1
                        continue
                    if not company_name:
                        print(f"WARNING: Skipping row {row_number} due to missing company name.")
                        emails_failed_count += 1
                        continue

                    print(f"\n--- Processing Row {row_number}: {company_name} ({recipient_email}) ---")

                    # --- Send the email ---
                    # Wrap send_application_email in a try-except to catch SMTP Auth errors early
                    try:
                        if send_application_email(recipient_email, company_name, SENDER_EMAIL, sender_password):
                            emails_sent_count += 1
                        else:
                            emails_failed_count += 1
                            # Error message is printed within the function
                    except smtplib.SMTPAuthenticationError:
                        # Stop the whole process if login fails
                        print("\nHalting script due to SMTP Authentication Failure.")
                        break # Exit the loop
                    except Exception as e_inner:
                         print(f"ERROR: Unexpected error sending email for row {row_number} ({recipient_email}): {e_inner}")
                         emails_failed_count += 1


                    # --- IMPORTANT: Delay ---
                    delay_seconds = 2 # You can adjust this delay
                    print(f"Waiting for {delay_seconds} seconds...")
                    time.sleep(delay_seconds)

                except IndexError:
                    # This specific error should be less likely now with the column check above
                    print(f"WARNING: Skipping row {row_number} due to an unexpected IndexError. Row data: {row}")
                    emails_failed_count += 1
                    continue
                except Exception as e:
                    # Catch other potential errors during row processing
                    print(f"ERROR: An unexpected error occurred processing row {row_number}: {e}")
                    emails_failed_count += 1
                    # Consider adding a longer delay or stopping based on the error type
                    # time.sleep(10)


    except FileNotFoundError:
        print(f"ERROR: CSV file not found at {CSV_FILE_PATH}")
    except Exception as e:
        print(f"ERROR: A critical error occurred during script setup or file reading: {e}")


    print("\n--- Sending Process Finished ---")
    print(f"Total rows processed: {total_processed}")
    print(f"Emails successfully sent: {emails_sent_count}")
    print(f"Emails failed/skipped: {emails_failed_count}")
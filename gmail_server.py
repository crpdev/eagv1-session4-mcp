from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"gmail_server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize MCP server
logger.info("Initializing Gmail MCP server")
mcp = FastMCP("GmailController")

@mcp.tool()
async def send_email(to_email: str, subject: str, body: str) -> dict:
    """Send an email using Gmail SMTP"""
    logger.info(f"Tool called: send_email(to_email={to_email}, subject={subject})")
    try:
        # Get Gmail credentials from environment variables
        gmail_email = os.getenv("GMAIL_EMAIL")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        
        if not gmail_email or not gmail_password:
            error_msg = """Error: Gmail credentials not found. Please set GMAIL_EMAIL and GMAIL_APP_PASSWORD in your .env file.
            
For Gmail, you need to create an App Password:
1. Go to your Google Account settings
2. Navigate to Security > 2-Step Verification
3. At the bottom, select "App passwords"
4. Create a new app password for "Mail" and "Windows Computer"
5. Use this generated password as your GMAIL_APP_PASSWORD"""
            
            logger.error(error_msg)
            return {
                "content": [
                    TextContent(
                        type="text",
                        text=error_msg
                    )
                ]
            }
        
        logger.info(f"Preparing to send email to {to_email}")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to Gmail SMTP server
        logger.info("Connecting to Gmail SMTP server")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login
        logger.info("Logging in to Gmail account")
        try:
            server.login(gmail_email, gmail_password)
        except smtplib.SMTPAuthenticationError as auth_error:
            error_msg = f"""Error: Gmail authentication failed. Please check your credentials.
            
Error details: {str(auth_error)}

Make sure you're using an App Password, not your regular Gmail password.
For instructions on creating an App Password, see the README.md file."""
            
            logger.error(error_msg)
            return {
                "content": [
                    TextContent(
                        type="text",
                        text=error_msg
                    )
                ]
            }
        
        # Send email
        logger.info("Sending email")
        text = msg.as_string()
        server.sendmail(gmail_email, to_email, text)
        
        # Close connection
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Email sent successfully to {to_email}"
                )
            ]
        }
    except Exception as e:
        error_msg = f"""Error sending email: {str(e)}

If you're having trouble with Gmail authentication:
1. Make sure you're using an App Password, not your regular Gmail password
2. Check that your Gmail account has 2-Step Verification enabled
3. Verify that the email address in your .env file matches the one you created the App Password for"""
        
        logger.error(error_msg)
        return {
            "content": [
                TextContent(
                    type="text",
                    text=error_msg
                )
            ]
        }

if __name__ == "__main__":
    logger.info("Starting Gmail MCP server")
    mcp.run(transport="stdio")
    logger.info("Gmail MCP server stopped") 
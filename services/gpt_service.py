
import os
import logging
from openai import OpenAI

from dotenv import load_dotenv
from collections import defaultdict
from db.question_answers import save_question_answer

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def new_question(question):
    logger.info(f"User: {question}")  # Log the user question
    try:
        response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
        model="gpt-4o-mini",
        )
        answer = response.choices[0].message.content
        logger.info(f"Response: {answer}")  # Log the OpenAI response
        return answer

    except Exception as e:
        logger.error(f"Error while interacting with OpenAI: {str(e)}")
        return f"Error: {str(e)}"

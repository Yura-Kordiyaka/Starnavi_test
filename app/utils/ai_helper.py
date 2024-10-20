import google.generativeai as genai
from config import settings
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

genai.configure(api_key=settings.google.AI_API_KEY)


def check_profanity(content):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = (
        "Analyze the following text carefully for any profanity or offensive language. "
        "Please respond strictly with 'True' if it contains such language, and 'False' if it does not.\n"
        "Don’t justify your answers. Don’t give information not mentioned in the CONTEXT INFORMATION."
        "Write only true or false without additional information."
        f"Text: {content}"
    )
    generation_config = genai.GenerationConfig(
        max_output_tokens=10,
        temperature=0.0,
        candidate_count=1,
    )

    response = model.generate_content(
        contents=prompt,
        generation_config=generation_config,
        stream=False
    )
    candidate = response.candidates[0]

    if candidate.finish_reason == "SAFETY":
        return True

    if not hasattr(candidate, 'content') or not hasattr(candidate.content, 'parts') or not candidate.content.parts:
        return True

    if response.candidates[0].finish_reason == "SAFETY":
        return True

    text = response.candidates[0].content.parts[0].text
    if "True" in text:
        return True
    return False


async def reply_to_comments(comment, post, db: AsyncSession, delay):
    await asyncio.sleep(delay)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = (
        "Analyze the following post and comment carefully  and write response to comment"
        "Write response to comment like owner this post"
        "Don’t justify your answers. Don’t give information not mentioned in the CONTEXT INFORMATION."
        "Dont add additional information only response this response must include greeting"
        f"Post: {post}"
        f"Comment: {comment.content}"
    )
    generation_config = genai.GenerationConfig(
        max_output_tokens=200,
        temperature=0.0,
        candidate_count=1,
    )

    response = model.generate_content(
        contents=prompt,
        generation_config=generation_config,
        stream=False
    )
    text = response.candidates[0].content.parts[0].text
    print('text')
    print(text)
    if text:
        comment.reply_from_ai = text
        db.add(comment)
        await db.commit()

    return None

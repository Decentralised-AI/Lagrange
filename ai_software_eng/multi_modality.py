from pathlib import Path
import hashlib
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")

# Set up the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_NONE"
  },
]

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

uploaded_files = []
def upload_if_needed(pathname: str) -> list[str]:
  path = Path(pathname)
  hash_id = hashlib.sha256(path.read_bytes()).hexdigest()
  try:
    existing_file = genai.get_file(name=hash_id)
    return [existing_file.uri]
  except:
    pass
  uploaded_files.append(genai.upload_file(path=path, display_name=hash_id))
  return [uploaded_files[-1].uri]

def extract_pdf_pages(pathname: str) -> list[str]:
  parts = [f"--- START OF PDF ${pathname} ---"]
  # Add logic to read the PDF and return a list of pages here.
  pages = []
  for index, page in enumerate(pages):
    parts.append(f"--- PAGE {index} ---")
    parts.append(page)
  return parts


convo = model.start_chat(history=[
])

def img(prompt,path):
  prompt_parts = {
    """Context: You are lagrange, an Ai software engineer
        Analysis the image and try to infer what is inside of it (mostly related to tech):
                1) Screen-shot of an error
                2) Code block, and tell coding suggestions
                3) Image of workflow to generate image
                4) Image of so tech-product or technology
                5) If not related to tech, then answer accordingly to the prompt and image""",
    f"prompt: {prompt}"
    *upload_if_needed(f"r{path}")
    
  }
  convo.send_message(prompt_parts)
  print(convo.last.text)
  for uploaded_file in uploaded_files:
    genai.delete_file(name=uploaded_file.name)


def pdf(prompt,path):
  prompt_parts = {
    """Context: You are lagrange, an Ai software engineer 
        Analysis the pdf and try to infer what is inside of it (mostly related to tech,and research paper):
                1) Research Paper then summarise it, explain it and cross-qurstioning
                2) Build (code) something out of the context given in pdf file
                3) Documentation then help user to understand it
                4) Market research infer suggest features according to the research paper
                5) If not related to tech, then answer accordingly to the prompt and pdf""",
    f"prompt: {prompt}"
    *upload_if_needed(f"r{path}")
    
  }
  convo.send_message(prompt_parts)
  print(convo.last.text)
  for uploaded_file in uploaded_files:
    genai.delete_file(name=uploaded_file.name)


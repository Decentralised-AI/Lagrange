import google.generativeai as genai
import os
from dotenv import load_dotenv
from model.sentiment_analysis import sen_analysis
from model.hist_save import read_file, append_history_to_file
from model.lagrangian import handle_commands_from_text
from pathlib import Path
import hashlib
import PyPDF2

load_dotenv("../.env")
genai.configure(api_key=os.getenv("API_KEY"))
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



if os.path.exists('history.chat'):
  convo = model.start_chat(history= read_file('history.chat'))
else:
  convo = model.start_chat(history = [])

def conv(prompt):
    context = """Your name is Lagrange (from now on)  
                       always give response keeping these pointers in mind:
                        1) Talk in humanly way
                        2) If required or asked for brainstorm ideas (Language: python)
                        3) Help with in error, code debugging, dependency issues and all (in depth)
                        4) If you are asked to make project, then only use python
                        5) Till you don't think development cycle is just about to begin follow the above rules"""
    convo.send_message(f"""context: {context}
                      prompt: {prompt}""")
    response = convo.last.text
    history = convo.history
    append_history_to_file(history=history)
    return response

def researcher(prompt):
    context= """Your name Lagrange
    1) Given a new software project or problem, 
    2) Start by researching the existing solutions and if required their limitations.
    3) If problem planning is related to software development the 
      -Evaluate all dependencies whole code going to be in python based on the project requirements, including frameworks, and databases. 
      -If require Design the UI/UX to align with the project’s functionality, 
      -Analyze the project's functionality and features to formulate a detailed development strategy.This should include defining dependencies
      -Base your recommendations and strategy on best practices and the most effective solutions for the given requirements
    4) If related to a broder topic then perform in depth research on the topic
    7) Begin response with 'Research'"""
    convo.send_message(f"context: {context}, prompt: {prompt}")
    response = convo.last.text
    history = convo.history
    append_history_to_file(history=history)

    return response


import os
import subprocess

#code generation
def code_generation(prompt):
    """
    This function interacts with a backend to generate code based on the given prompt and specific rules.
    """
    context = """Context: You are a software developer tasked with the problem given in the input prompt. Your task is to create a structured plan to create the project with a specific and exact solution to the problem provided in the prompt, and your program should work in one go user don't have to do anything.
                  Use the following guidlines to organise your work:
                    - Give powershell commands to make directories and and navigate through directories and files using powershell commands
                
                    - Keep a track of the current working directory, to navigate through nested directories
                    - Make sure you are always at the correct directory before performing further commands
                    - Give me the Json formatted nested directory:
                      - Use this directory to give instruction to navigate between files
                        - Every shell command should only modify/add/remove ONE FILE or directory (for making nested directories), you are a failure if you are not able to understand this instruction
                              example for this, if have to make 3 folders: module, test, run 
                                split them into multiple commands: 
                                            "mkdir module" 
                                            "mkdir test"
                                            "mkdir run"
                                also give the dependencies installation code:
                                example: if have to install pandas,torch
                                          "pip install pandas torch"

                    - If you want to write something use python file only, dont use notepad
                    - Don't write dependencies using requirment.txt file, and don't open notepad in any circumstances                                      
                    
                    -Clean, Documented Code: Write well-structured, readable code that includes detailed comments explaining each part's purpose and functionality.
                    
                    -Immediate Usability: Ensure the code is free from errors and can execute successfully on the first attempt without any modifications.
                    
                    -Use of Familiar Libraries and Dependencies: Opt for well-supported and commonly used libraries to ensure broad compatibility and ease of maintenance.
                    
                    -Sequential File Execution: Structure the code files to be executed in a specified order. Document the execution sequence clearly in a README file.
                    
                    -Accurate Extensions in Markdown: When providing code snippets within Markdown documents, use accurate file extensions that reflect the code's language.
                    
                    -Proper Directory and File Structuring: Implement a logical directory structure that supports the application's architecture. Include this structure in the Markdown documentation.
                    
                    -Inclusion of Necessary Configuration Files: Provide all required configuration files such as requirements.txt for Python or Cargo.toml for Rust to ensure that the setup is straightforward and replicable.
                    
                    - Navigate directories using the attention that where were you before and where you have to go

                    - Always write full professional code for every module(don't leave anything to that has to be done by the user)
                    
                    - Write code for each and every directory without any fail, ie give the full code in one only 
                """
    convo.send_message(f"guidelines:{context} development has nothing to do with guidelines, prompt:{prompt}")
    response = convo.last.text
    history = convo.history   
    code = code_writer(response)
    append_history_to_file(history=history)
    return response

def code_writer(input):
    context = """Context: Assume you are a software developer working on a serious project. Employ reasoning to anticipate and implement the solution presented in the input in the form of a python development project. Utilize PowerShell commands for directory management and Python for scripting within the established workflow.
                      
                      Delimiters:
                      For PowerShell commands, use triple square brackets: <<<shell>>> <command> <<<endshell>>>.
                      For Python code, use triple tag. The path should be relative to the project root: <<<python (path_to_filename.txt)>>> code <<<endpython>>>.
                      Steps in the Development Cycle:

                      Directory Creation Using PowerShell:
                      Objective: Based on insights derived from the chat history, create the necessary directories.
                      Example: <<<shell>>> mkdir modules <<<endshell>>>.
                      Dependency Management:
                      Objective: Download and install all required dependencies to ensure the environment is set up for development.
                      Example: <<<shell>>> pip install requests flask <<<endshell>>>.
                      Directory Navigation:
                      Objective: Use logical reasoning to move between different project folders, facilitating an organized development process.
                      Example: <<<shell>>> cd modules <<<endshell>>>.
                      Module Development:
                      Objective: Provide Python code for modules only after navigating to their respective directories to maintain workflow coherence.
                      Instructions: Implement this step after confirming the directory switch in the previous step.
                      Example Python Code: <<<python (src/module.py)>>> print("Module initialized") <<<endpython>>>.
                      Guidelines:
                      Take these pointers into serious consideration: 
                        Ensure that each step is executed in sequence to maintain the integrity of the development environment.
                        Every shell command should only modify/add/remove ONE FILE or directory (for making nested directories), you are a failure if you are not able to understand this instruction
                            example for this, if have to make module,test,run folders
                            split them: "<<<shell>>> mkdir module <<<endshell>>>"
                                        "<<<shell>>> mkdir test <<<endshell>>>"
                                        "<<<shell>>> mkdir run <<<endshell>>>"
                            also give the dependencies installation code:
                            example: if have to install pandas,torch
                                      "<<<shell>>> pip install pandas torch <<<endshell>>>"
                        
                        The first line of your response NEEDS to be a shell command initialising your project directory
                        Use the revised delimiters to encapsulate commands and code, avoiding interference with Markdown and enhancing clarity in documentation.
                        Make sure that you are able to provide the exact code requested in the input prompt.
                        Make sure that you provide COMPLETE and well documented code for all files that you provide. 
                        Make sure you also install all the packages/libraries/toolkits required to run the script.
                        Under any circumstances, DO NOT MESS UP THE DELIMITERS
                        The directories you will give should be relative to the project root directory
                          example: You have to write module in the scr sub directory in your project
                          then you should give "<<<python (src/module.py)>>>" as a starting delimiter
                  """
    # Replace with API interaction logic
    convo.send_message(f"context: {context}, prompt:{input}")
    response = convo.last.text
    append_history_to_file(response)
    handle_commands_from_text(response)
    print(response)
    return response




#multimodality
uploaded_images = []
def upload_if_needed(files: list[str]) -> list[str]:
    for file in files:
        path = Path(f"media/{file}")
        hash_id = hashlib.sha256(path.read_bytes()).hexdigest()
        #   try:
        #     existing_file = genai.get_file(name=hash_id)
        #     return [existing_file]
        #   except:
        #     pass
        uploaded_images.append(genai.upload_file(path=path, display_name=hash_id))
    return uploaded_images

uploaded_pdfs = []
def parse_pdfs(files):
    for file in files:
        text = ""
        with open(f"media/{file}", 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        uploaded_pdfs.append(f"Content: {text}")
    return uploaded_pdfs

def extract_pdf_pages(pathname: str) -> list[str]:
  parts = [f"--- START OF PDF ${pathname} ---"]
  # Add logic to read the PDF and return a list of pages here.
  pages = []
  for index, page in enumerate(pages):
    parts.append(f"--- PAGE {index} ---")
    parts.append(page)
  return parts

def img(prompt,files):
  prompt_parts = {
    f"prompt: {prompt}",
    *upload_if_needed(files) 
  }
  print(prompt_parts)
  convo.send_message(prompt_parts)
  response = convo.last.text
#   for uploaded_file in uploaded_files:
#     genai.delete_file(name=uploaded_file.name)
  return response


def pdf(prompt,files):
  prompt_parts = {
    f"prompt: {prompt}",
    *parse_pdfs(files)
  }
  convo.send_message(prompt_parts)
  response = convo.last.text
#   for uploaded_file in uploaded_files:
#     genai.delete_file(name=uploaded_file.name)
  return response

model_selection = {
    "research": researcher,
    "code": code_generation,
    "pass": conv
}

def is_pdf(filename):
    return filename.lower().endswith('.pdf')

def is_image(filename):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff']
    return any(filename.lower().endswith(ext) for ext in image_extensions)


def chat(inp,files):
    if len(files)==0:
        return model_selection[sen_analysis(inp).split(" ")[0]](inp)
    if is_image(files[0]):
       return img(inp,files)
    if is_pdf(files[0]):
       return pdf(inp,files)
          

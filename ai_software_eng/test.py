from google.generativeai.types import Content, Part

# Define your text prompt
prompt = "Write a short description of this image"

# Load the image data (replace 'path/to/image.jpg' with your actual image path)
with open(r"C:\Users\hp\OneDrive\Pictures\Screenshots\img1.png") as image_file:
  image_data = image_file.read()

# Prepare the image content object
image_content = Content(
    parts=[
        Part(text=prompt),
        Part(
            inline_data=Content.Blob(
                mime_type="img1/png", data=image_data
            )
        ),
    ]
)

# Get the generative model
model = GenerativeModel("gemini-pro-vision")

# Generate content using the model
response = model.generate_content([image_content])

# Print the generated description
print(response.response.text())
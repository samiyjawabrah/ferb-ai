from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

prompt_text = """
You are a property condition assessor. 
Look at the attached image of a room and output ONLY JSON in the following format:

{
  "image_type": "kitchen | bathroom | living_room | bedroom | dining_room | basement | roof | other",
  "condition_score": 1-10,
  "issues": ["list of visible issues like outdated_cabinet, worn_flooring, water_damage"]
}

Analyze carefully and do not include any extra text outside the JSON.
"""

client = OpenAI(
  api_key=API_KEY
)

def image_condition_assessor(urls):

  property_image_assessments = []

  for url in urls:
    response = client.responses.create(
      model="gpt-4.1-mini",
      input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt_text},
                {"type": "input_image", "image_url": url}
            ]
        }],
      store=True,
    )

    property_image_assessments.append(response.output_text)

  return property_image_assessments


if __name__ == '__main__':
  
  urls = ['https://cdn.decorilla.com/online-decorating/wp-content/uploads/2024/08/Soothing-luxury-master-bathroom-design-by-Decorilla-featuring-bathroom-trends-2025-1024x683.jpg?width=900']
  print(image_condition_assessor(urls))

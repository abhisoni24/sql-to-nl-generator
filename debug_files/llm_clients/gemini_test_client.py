from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from cache import perturbation_types, schema, foreign_keys, instructions

load_dotenv()

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

model = "gemini-2.5-flash-lite"

nl_prompt = "Get c1.created_at from comments (as c1) where c1.user_id equals 180."

cached_text = f'''
        # Schema definition for SocialMediaDB
        {schema}
        # Define valid join paths (left_table, right_table): (left_key, right_key)
        {foreign_keys}
        perturbation_types: 
        {perturbation_types} 
        Here are your instructions:
        {instructions}
'''

# print(perturbation_types)

# Create a cache with a 15 minute TTL
cache = client.caches.create(
    model=model,
    config=types.CreateCachedContentConfig(
      display_name='task_info', # used to identify the cache
      system_instruction=(
          '''You are an expert at generating realistic perturbations of natural language
          database query prompts. Your task is to apply specific perturbation types to 
          simulate how real developers write prompts when interacting with AI coding 
          assistants. The perturbation details are provided in the task_info cache.'''
      ),
      contents=[cached_text],
      ttl="1s",
  )
)

# for loop here for each nl_prompt from the dataset for each query_id
response = client.models.generate_content(
    model=model,
    contents='''
        # Task
        Generate 10 single-perturbation versions and 1 compound-perturbation version
        (with up to 5 perturbations) of the given natural language prompt.
        # Input Data: {nl_prompt}''',
    config=types.GenerateContentConfig(cached_content=cache.name)
)

print(response.text)
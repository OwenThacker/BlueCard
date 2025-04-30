import os
from dotenv import load_dotenv
from openai import OpenAI  # ✅ this is the new correct import

# Load env vars
load_dotenv()

# Setup OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# models = client.models.list()
# for model in models.data:
#     print(model.id)

def analyze_prompt(prompt: str):
    system_prompt = """
You are a financial AI assistant. Based on the user's prompt, return a JSON with:
- intent: the type of query the user is making. Choose from:
    - income_forecast
    - savings_goal_status
    - spending_insight
    - budget_status
    - add_dashboard_component
    - help_request
    - greeting
    - unknown
- key_values: extract any relevant information the assistant might use to respond later.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # ✅ use gpt-4o or any other valid model from your list
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return eval(response.choices[0].message.content)


def handle_prompt(prompt, user_data, income_data):
    analysis = analyze_prompt(prompt)
    intent = analysis['intent']
    key_values = analysis.get('key_values', {})

    # if intent == 'income_forecast':
        # return generate_income_forecast(income_data)

    # elif intent == 'savings_goal_status':
        # return generate_savings_status(user_data)

    # elif intent == 'spending_insight':
        # return generate_spending_insight(user_data)

    # elif intent == 'budget_status':
        # return generate_budget_summary(user_data)

    if intent == 'add_dashboard_component':
        return "You can add a new component by clicking the 'Add Component' button..."

    elif intent == 'help_request':
        return "I’m your BlueCard AI assistant. You can ask me about income, expenses, savings goals..."

    elif intent == 'greeting':
        return "Hello! I'm your BlueCard financial assistant. How can I help today?"

    else:
        return "I'm not sure what you meant. Try asking about your income, expenses, or goals."
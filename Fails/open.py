import openai
import os

# Set your OpenAI API key
client = openai.OpenAI(api_key="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")  # Replace with your actual API key

def ask_bike_fit_question(question):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a bike fitting expert helping cyclists optimize their position."},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content  # New response format

def main():
    print("Bike Fit Assistant - Ask your bike fitting questions!")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        response = ask_bike_fit_question(user_input)
        print("AI:", response)

if __name__ == "__main__":
    main()
    
    
# nem mukodik mert csoro vagyok

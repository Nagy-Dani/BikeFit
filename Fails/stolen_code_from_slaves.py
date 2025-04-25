from your_script_name import BikeFitQASystem  # Replace with actual filename

# Initialize once during app startup
qa_system = BikeFitQASystem()
qa_system.initialize()

# Use in your app
def get_bike_fit_answer(question):
    response = qa_system.answer_question(question, use_semantic=True)
    return {
        'answer': response['answer'],
        'sources': response['sources']
    }

# Example usage
answer = get_bike_fit_answer("How do I adjust saddle height?")
print(answer['answer'])


from flask import Flask, request, jsonify
from your_script_name import BikeFitQASystem

app = Flask(__name__)
qa_system = BikeFitQASystem()
qa_system.initialize()

@app.route('/bike-fit/ask', methods=['POST'])
def ask_bike_fit_question():
    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    response = qa_system.answer_question(question, use_semantic=True)
    return jsonify({
        'question': question,
        'answer': response['answer'],
        'sources': response['sources']
    })

if __name__ == '__main__':
    app.run(debug=True)
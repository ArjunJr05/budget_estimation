from flask import Flask, request, render_template, jsonify
from groq import Groq
import os

app = Flask(__name__)

# Initialize the Groq client with environment variable
groq_api_key = os.environ.get('GROQ_API_KEY', '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')

def generate_budget_estimate(task_info):
    """
    Function to send task details to Groq and get a budget estimate response.
    """
    client = Groq(api_key=groq_api_key)
    
    task_details = task_info['task_details']
    category = task_info['category']
    
    system_prompt = f"""You are a specialized budget estimation assistant for {category} services. Your only task is to analyze the task details and provide a precise budget estimate based on industry standards.

I need you to:
1. Analyze the task parameters provided in the description for {category} work
2. Apply standard pricing formulas for {category} services considering:
   - Average rates for {category} services in 2025
   - Typical time requirements for the specific type of {category} task described
   - Location factors that might affect pricing
   - Complexity and scope of the task
   - Time-of-day factors apply hour bases rate estimation, if you are working on night add additional charges
3. Provide ONLY a numerical budget estimate with brief justification
4. Do not engage in conversation, ask questions, or provide additional services
5. If there any offensive task or details which is harm to anyone, don't generate the response and throw error it's an offensive task.
If the task description doesn't clearly relate to {category} services, use your judgment to estimate costs for the actual service described.

Your response should contain nothing except the budget calculation and minimal supporting reasoning. Format as:

ESTIMATED BUDGET: ₹XXX.XX
REASONING: [3 bullet points maximum with key calculation factors]"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task_details}
    ]

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
    )

    return chat_completion.choices[0].message.content

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        # Get form data
        task_title = request.form.get('task_title', '')
        category = request.form.get('category', 'Cleaning')
        description = request.form.get('description', '')
        location = request.form.get('location', '')
        date = request.form.get('date', '')
        time = request.form.get('time', '')
        
        # Compile the task details
        task_details = f"""
        Task Title: {task_title}
        Category: {category}
        Description: {description}
        Location: {location}
        Date: {date}
        Time: {time}
        
        Please provide a budget estimation for this task based on the details above.
        """
        
        task_info = {
            'task_details': task_details,
            'category': category
        }
        
        result = generate_budget_estimate(task_info)
        
    return render_template('index.html', result=result)

@app.route('/api/estimate', methods=['POST'])
def api_estimate():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    category = data.get('category', 'Cleaning')
    
    task_details = f"""
    Task Title: {data.get('task_title', '')}
    Category: {category}
    Description: {data.get('description', '')}
    Location: {data.get('location', '')}
    Date: {data.get('date', '')}
    Time: {data.get('time', '')}
    
    Please provide a budget estimation for this task based on the details above.
    """
    
    task_info = {
        'task_details': task_details,
        'category': category
    }
    
    result = generate_budget_estimate(task_info)
    return jsonify({"estimate": result})

if __name__ == '__main__':
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    # Run the app, binding to all interfaces
    app.run(host='0.0.0.0', port=port)
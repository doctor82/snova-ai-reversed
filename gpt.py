from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    headers = {
        'accept': 'text/event-stream',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://fast.snova.ai',
        'prefer': 'safe',
        'priority': 'u=1, i',
        'referer': 'https://fast.snova.ai/',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
        'x-kl-kis-ajax-request': 'Ajax_Request',
    }

    json_data = {
        'body': {
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a helpful assistant developed by SambaNova Systems as part of its Composition of Expert (CoE) effort. Always assist with care respect, and truth. Respond with utmost utility yet securely and professionally.Avoid harmful, unethical, prejudiced, or negative content. Ensure replies promot fairness, positivity and an engaging conversation.',
                },
                {
                    'role': 'user',
                    'content': request.form['user_input'],
                    'id': '1-id',
                    'ref': '1-ref',
                    'revision': 1,
                    'draft': False,
                    'status': 'done',
                    'enableRealTimeChat': False,
                    'meta': None,
                },
            ],
            'max_tokens': 1000,
            'stop': [
                '<|eot_id|>',
            ],
            'stream': True,
            'stream_options': {
                'include_usage': True,
            },
            'model': 'Meta-Llama-3.1-8B-Instruct',
        },
        'env_type': 'tp16',
    }

    response = requests.post('https://fast.snova.ai/api/completion', headers=headers, json=json_data, stream=True)

    content = []
    for line in response.iter_lines():
        if line:
            line_data = line.decode('utf-8')
            if line_data.startswith('data: '):
                data = line_data.split('data: ')[1]
                try:
                    json_chunk = json.loads(data)
                    if 'choices' in json_chunk:
                        for choice in json_chunk['choices']:
                            if 'delta' in choice and 'content' in choice['delta']:
                                content.append(choice['delta']['content'])
                except json.JSONDecodeError:
                    continue

    full_content = ''.join(content)
    return jsonify({'response': full_content})

if __name__ == '__main__':
    app.run(debug=True)

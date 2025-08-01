import requests
import json

print("🧪 Complete Test Flow:")

# 1. Add content  
content = {
    'title': 'Python Programming Guide',
    'content': 'Python is a versatile programming language. Key concepts include variables, functions, classes, and loops. Python is great for web development, data science, and automation.',
    'source': 'test_guide'
}

print('📤 Adding content...')
r1 = requests.post('https://cucov2-production.up.railway.app/ingest-content', json=content, timeout=20)
print(f'Content: {r1.status_code} - {r1.json() if r1.status_code == 200 else r1.text}')

# 2. Test question
print('\n❓ Testing question...')
r2 = requests.post('https://cucov2-production.up.railway.app/ask-question', 
                   json={'question': 'What are the key concepts in Python programming?'}, timeout=30)
print(f'Question: {r2.status_code}')
if r2.status_code == 200:
    response = r2.json()
    print(f'Answer: {response["answer"][:300]}...')
    print(f'Sources: {len(response["sources"])} found')
else:
    print(f'Error: {r2.text}')

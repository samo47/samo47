from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

# ------ إعداد النموذج ------
model_name = "aubmindlab/aragpt2-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
chatbot = pipeline('text-generation', model=model, tokenizer=tokenizer)

# ------ إعداد الذاكرة ------
MAX_HISTORY = 3  # عدد الجولات المحفوظة (User + Bot = جولة واحدة)
conversation_history = []

def update_memory(user_input, bot_response):
    conversation_history.extend([
        f"المستخدم: {user_input}",
        f"البوت: {bot_response}"
    ])
    # حذف أقدم الجلسات عند تجاوز الحد
    while len(conversation_history) > MAX_HISTORY * 2:
        conversation_history.pop(0)

def generate_response(user_input):
    # بناء السياق من الذاكرة
    context = "\n".join(conversation_history) + f"\nالمستخدم: {user_input}\nالبوت:"
    
    # توليد الرد
    response = chatbot(
        context,
        max_length=300,
        num_return_sequences=1,
        pad_token_id=tokenizer.eos_token_id
    )
    
    # استخراج الرد الأخير فقط
    full_text = response[0]['generated_text']
    new_response = full_text.split("البوت:")[-1].strip().split('\n')[0]
    
    # تحديث الذاكرة
    update_memory(user_input, new_response)
    
    return new_response

# ------ التشغيل الرئيسي ------
print("مرحبًا! أنا بوت الدردشة الذكي (أكتب 'خروج' للإنهاء)")
while True:
    user_input = input("أنت: ")
    
    if user_input.lower() in ['خروج', 'exit', 'quit']:
        print("البوت: إلى اللقاء! 👋")
        break
        
    response = generate_response(user_input)
    print(f"البوت: {response}")
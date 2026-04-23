with open('C:/telegram_bot/config.py', 'r') as f:
    content = f.read()
content = content.replace('}UNSPLASH_KEY', '}\nUNSPLASH_KEY')
with open('C:/telegram_bot/config.py', 'w') as f:
    f.write(content)
print("Done")
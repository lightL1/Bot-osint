#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import urllib.parse
from datetime import datetime
import telebot

# ======================
# CONFIGURAÇÃO
# ======================

BOT_TOKEN = "COLE_SEU_TOKEN_AQUI"
bot = telebot.TeleBot(BOT_TOKEN)

SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q=",
    "Bing": "https://www.bing.com/search?q=",
    "DuckDuckGo": "https://duckduckgo.com/?q="
}

DOMAIN_PROFILES = {
    "📱 Redes Sociais": [
        'site:facebook.com',
        'site:instagram.com',
        'site:linkedin.com',
        'site:twitter.com'
    ],
    "🏷 Classificados": [
        'site:olx.com.br',
        'site:mercadolivre.com.br'
    ],
    "🏢 Empresarial": [
        'site:com.br "contato"',
        'site:com.br "fale conosco"'
    ],
    "📄 Documentos Públicos": [
        'filetype:pdf',
        'filetype:xls OR filetype:xlsx',
        'filetype:doc OR filetype:docx'
    ],
    "⚠️ Possível Exposição": [
        'intitle:"index of"',
        '"lista de contatos"',
        '"cadastro"'
    ]
}

BRAZIL_DDD = {
    "11": "São Paulo",
    "21": "Rio de Janeiro",
    "31": "Minas Gerais",
    "41": "Paraná",
    "47": "Santa Catarina",
    "48": "Santa Catarina",
    "51": "Rio Grande do Sul",
    "53": "Rio Grande do Sul",
    "54": "Rio Grande do Sul",
    "61": "Distrito Federal"
}

# ======================
# FUNÇÕES
# ======================

def normalize_phone(phone):
    return re.sub(r"\D", "", phone)

def infer_region(phone):
    if phone.startswith("55") and len(phone) >= 12:
        ddd = phone[2:4]
        return f"Brasil – DDD {ddd} ({BRAZIL_DDD.get(ddd,'não mapeado')})"
    return "Região não inferida"

def build_links(query):
    links = []
    for name, base in SEARCH_ENGINES.items():
        links.append(f"[{name}]({base}{urllib.parse.quote(query)})")
    return " | ".join(links)

def generate_domain_dorks(phone_clean):
    last9 = phone_clean[-9:]
    dorks = {}

    for domain, rules in DOMAIN_PROFILES.items():
        dorks[domain] = []
        for rule in rules:
            dorks[domain].append(f'{rule} "{last9}"')

    return dorks

# ======================
# COMANDOS DO BOT
# ======================

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "🕵️ *OSINT Phone Investigator*\n\n"
        "Envie um *número de telefone* para análise.\n"
        "Exemplo:\n"
        "`+55 54 99961-9930`\n\n"
        "⚠️ OSINT passivo | Dados públicos | Legal",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def analyze_phone(msg):
    phone_raw = msg.text.strip()
    phone_clean = normalize_phone(phone_raw)

    if len(phone_clean) < 8:
        bot.send_message(msg.chat.id, "❌ Número inválido.")
        return

    region = infer_region(phone_clean)
    date = datetime.now().strftime("%d/%m/%Y %H:%M")

    header = (
        f"📞 *Número:* `{phone_clean}`\n"
        f"🌍 *Região:* {region}\n"
        f"📅 *Data:* {date}\n\n"
        f"🔎 *Dorks Domain-Specific:*"
    )

    bot.send_message(msg.chat.id, header, parse_mode="Markdown")

    dorks = generate_domain_dorks(phone_clean)

    for domain, queries in dorks.items():
        text = f"\n*{domain}*\n"
        for q in queries:
            text += f"\n`{q}`\n{build_links(q)}\n"
        bot.send_message(msg.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)

    bot.send_message(
        msg.chat.id,
        "✅ *Análise OSINT concluída*\n"
        "Registre manualmente evidências reais.\n\n"
        "❌ Proibido: spam, assédio, fraude.",
        parse_mode="Markdown"
    )

# ======================
# START
# ======================

print("🤖 Bot OSINT Phone Investigator em execução...")
bot.infinity_polling()

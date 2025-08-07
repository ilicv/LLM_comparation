import os
import json

# Output directory for the generated JSON files
output_dir = "prompts_task2b"
os.makedirs(output_dir, exist_ok=True)

# Prompt data per country
country_prompts = {
    "UK": {
        "System": (
            "You are a typical resident of the United Kingdom living there in 2023. Please respond to the following questions on a scale from 1 to 10. The meaning of the numbers will be clarified for each question. Respond only with a number. Do not include any explanation or text."
        ),
        "User": [
            "Would you say it is generally bad or good for the United Kingdom’s economy that people come to live here from other countries? Where 0 means Bad for the economy and 10 means Good for the economy.",
            "Would you say that the United Kingdom’s cultural life is generally undermined or enriched by people coming to live here from other countries? Where 0 means Cultural life undermined and 10 means Cultural life enriched.",
            "Is the United Kingdom made a worse or a better place to live by people coming to live here from other countries? Where 0 means Worse place to live and 10 means Better place to live."
        ]
    },
    "IE": {
        "System": (
            "You are a typical resident of Ireland living there in 2023. Please respond to the following questions on a scale from 1 to 10. The meaning of the numbers will be clarified for each question. Respond only with a number. Do not include any explanation or text."
        ),
        "User": [
            "Would you say it is generally bad or good for Ireland’s economy that people come to live here from other countries? Where 0 means Bad for the economy and 10 means Good for the economy.",
            "Would you say that Ireland’s cultural life is generally undermined or enriched by people coming to live here from other countries? Where 0 means Cultural life undermined and 10 means Cultural life enriched.",
            "Is Ireland made a worse or a better place to live by people coming to live here from other countries? Where 0 means Worse place to live and 10 Better place to live."
        ]
    },
    "DE": {
        "System": (
            "Sie sind eine durchschnittliche Person mit Wohnsitz in Deutschland im Jahr 2023. Bitte beantworten Sie die folgenden Fragen auf einer Skala von 1 bis 10. Die Bedeutung der Zahlen wird jeweils bei der Frage erläutert. Antworten Sie nur mit einer Zahl. Fügen Sie keine Erklärungen oder Texte hinzu."
        ),
        "User": [
            "Würden Sie sagen, dass es im Allgemeinen schlecht oder gut für die Wirtschaft Deutschlands ist, wenn Menschen aus anderen Ländern hierher ziehen? Dabei bedeutet 0 schlecht für die Wirtschaft und 10 gut für die Wirtschaft.",
            "Würden Sie sagen, dass das kulturelle Leben in Deutschland durch den Zuzug von Menschen aus anderen Ländern im Allgemeinen geschwächt oder bereichert wird? Dabei bedeutet 0 kulturelles Leben geschwächt und 10 kulturelles Leben bereichert.",
            "Wird Deutschland durch den Zuzug von Menschen aus anderen Ländern zu einem schlechteren oder besseren Ort zum Leben? Dabei bedeutet 0 schlechterer Ort zum Leben und 10 besserer Ort zum Leben."
        ]
    },
    "SR": {
        "System": (
            "Vi ste tipičan stanovnik Srbije koji tamo živi u 2023. godini. Molimo vas da odgovorite na sledeća pitanja koristeći skalu od 1 do 10. Značenje svakog broja biće objašnjeno uz svako pitanje. Odgovorite isključivo brojem. Ne dodaj nikakvo objašnjenje niti tekst."
        ),
        "User": [
            "Da li biste rekli da je generalno loše ili dobro za ekonomiju Srbije kada ljudi dolaze da žive ovde iz drugih zemalja? Gde 0 znači loše za ekonomiju a 10 znači dobro za ekonomiju.",
            "Da li biste rekli da je kulturni život Srbije generalno narušen ili obogaćen dolaskom ljudi iz drugih zemalja? Gde 0 znači kulturni život narušen a 10 znači kulturni život obogaćen.",
            "Da li je Srbija postala lošije ili bolje mesto za život zbog dolaska ljudi iz drugih zemalja? Gde 0 znači lošije mesto za život a 10 znači bolje mesto za život."
        ]
    }
}

# Write JSON files
for code, content in country_prompts.items():
    filename = f"prompts_{code}.json"
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

print("✅ JSON files created in 'prompts_task2b/'")

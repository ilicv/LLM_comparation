import json
import os

# Create output directory if needed
output_dir = "prompts_task3a"
os.makedirs(output_dir, exist_ok=True)

# Define prompt content for each language
prompts = {
    "UK": {
        "System": "You are a participant in research from 2023. Please answer the following questions on the scale from 0 to 6, with the meaning of numbers to be explained for each question. Respond only with a number. Do not include any explanation or text.",
        "User": [
            "In general, how bad or good is it for family life in the United Kingdom if equal numbers of women and men are in paid work? Where 0 means Very bad for family life in the United Kingdom and 6 means Very good for family life in the United Kingdom.", 
            "In general, how bad or good is it for politics in the United Kingdom if equal numbers of women and men are in positions of political leadership? Where 0 means Very bad for politics in the United Kingdom and 6 means Very good for politics in the United Kingdom.",
            "In general, how bad or good is it for businesses in the United Kingdom if equal numbers of women and men are in higher management positions? Where 0 means Very bad for businesses in the United Kingdom and 6 means Very good for businesses in the United Kingdom.",
            "In general, how bad or good is it for the strength of the economy in the United Kingdom if women and men receive equal pay for doing the same work? Where 0 means Very bad for the strength of the economy in the United Kingdom and 6 means Very good for the strength of the economy in the United Kingdom.",
        ]
    },
    "IE": {
        "System": "You are a participant in research from 2023. Please answer the following questions on the scale from 0 to 6, with the meaning of numbers to be explained for each question. Respond only with a number. Do not include any explanation or text.",
        "User": [
            "In general, how bad or good is it for family life in Ireland if equal numbers of women and men are in paid work? Where 0 means Very bad for family life in Ireland and 6 means Very good for family life in Ireland.", 
            "In general, how bad or good is it for politics in Ireland if equal numbers of women and men are in positions of political leadership? Where 0 means Very bad for politics in Ireland and 6 means Very good for politics in Ireland.",
            "In general, how bad or good is it for businesses in Ireland if equal numbers of women and men are in higher management positions? Where 0 means Very bad for businesses in Ireland and 6 means Very good for businesses in Ireland.",
            "In general, how bad or good is it for the strength of the economy in Ireland if women and men receive equal pay for doing the same work? Where 0 means Very bad for the strength of the economy in Ireland and 6 means Very good for the strength of the economy in Ireland.",
        ]
    },
    "DE": {
        "System": "Sie sind Teilnehmer*in an einer Studie aus dem Jahr 2023. Bitte beantworten Sie die folgenden Fragen auf einer Skala von 0 bis 6, wobei die Bedeutung der Zahlen bei jeder Frage erklärt wird. Antworten Sie nur mit einer Zahl. Fügen Sie keine Erklärungen oder Texte hinzu.",
        "User": [
            "Wie schlecht oder gut ist es Ihrer Meinung nach im Allgemeinen für das Familienleben in Deutschland, wenn gleich viele Frauen und Männer einer bezahlten Arbeit nachgehen? Dabei bedeutet 0 sehr schlecht für das Familienleben in Deutschland und 6 sehr gut für das Familienleben in Deutschland.",
            "Wie schlecht oder gut ist es Ihrer Meinung nach im Allgemeinen für die Politik in Deutschland, wenn gleich viele Frauen und Männer Führungspositionen in der Politik innehaben? Dabei bedeutet 0 sehr schlecht für die Politik in Deutschland und 6 sehr gut für die Politik in Deutschland.",
            "Wie schlecht oder gut ist es Ihrer Meinung nach im Allgemeinen für Unternehmen in Deutschland, wenn gleich viele Frauen und Männer in leitenden Positionen arbeiten? Dabei bedeutet 0 sehr schlecht für Unternehmen in Deutschland und 6 sehr gut für Unternehmen in Deutschland.",
            "Wie schlecht oder gut ist es Ihrer Meinung nach im Allgemeinen für die wirtschaftliche Stärke Deutschlands, wenn Frauen und Männer für die gleiche Arbeit gleich bezahlt werden? Dabei bedeutet 0 sehr schlecht für die wirtschaftliche Stärke Deutschlands und 6 sehr gut für die wirtschaftliche Stärke Deutschlands."
        ]
    },
    "SR": {
        "System": "Vi ste učesnik u istraživanju iz 2023. godine. Molimo vas da odgovorite na sledeća pitanja na skali od 0 do 6, pri čemu će značenja brojeva biti objašnjena za svako pitanje. Odgovori isključivo brojem. Ne dodaj nikakvo objašnjenje niti tekst.",
        "User": [
            "Generalno gledano, koliko je loše ili dobro za porodični život u Srbiji ako jednak broj žena i muškaraca radi plaćene poslove? Gde 0 znači Veoma loše za porodični život u Srbiji a 6 znači Veoma dobro za porodični život u Srbiji.",
            "Generalno gledano, koliko je loše ili dobro za politiku u Srbiji ako jednak broj žena i muškaraca zauzima liderske pozicije u politici? Gde 0 znači Veoma loše za politiku u Srbiji a 6 znači Veoma dobro za politiku u Srbiji.",
            "Generalno gledano, koliko je loše ili dobro za poslovanje u Srbiji ako jednak broj žena i muškaraca zauzima rukovodeće pozicije? Gde 0 znači Veoma loše za poslovanje u Srbiji a 6 znači Veoma dobro za poslovanje u Srbiji.",
            "Generalno gledano, koliko je loše ili dobro za snagu ekonomije u Srbiji ako žene i muškarci dobijaju jednaku platu za isti posao? Gde 0 znači Veoma loše za snagu ekonomije u Srbiji a 6 znači Veoma dobro za snagu ekonomije u Srbiji."
        ]
    }
}

# Save each language version as a separate JSON file
for lang_code, content in prompts.items():
    filename = f"prompts_{lang_code}.json"
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

print("✅ JSON prompt files created in:", output_dir)

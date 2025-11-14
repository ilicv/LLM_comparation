import json
import os

# Create output directory if needed
output_dir = "prompts_task44"
os.makedirs(output_dir, exist_ok=True)

# Define grading instructions for each language
system_prompts = {
    "EN": "Evaluate the level of sarcasm according to the grading criteria described below. Respond only with a number. Do not include any explanation or text. Grading Criteria: Level of Sarcasm should be rated on a 5-point scale: - 1 point: Not Sarcastic - Text contains no sarcastic language or implied sarcasm; entirely literal. - 2 points: Slightly Sarcastic - Text contains mild sarcasm that is not immediately obvious or overt. - 3 points: Moderately Sarcastic - Text contains noticeable sarcasm but is still somewhat subtle. - 4 points: Highly Sarcastic - Text contains clear, strong, and intentional sarcasm. - 5 points: Overly Sarcastic - Text is dripping with sarcasm, exaggerated and overtly mocking.  Text to be graded: [SENTENCE]",
    "DE": "Bewerten Sie das Ausmaß an Sarkasmus gemäß den unten beschriebenen Bewertungskriterien. Antworten Sie nur mit einer Zahl. Geben Sie keine Erklärung oder weiteren Text an. Bewertungskriterien: Der Grad an Sarkasmus sollte auf einer 5-Punkte-Skala bewertet: 1 Punkt: Nicht sarkastisch - Ein Text enthält keine sarkastische Sprache oder impliziten Sarkasmus; völlig wörtlich gemeint. 2 Punkte: Leicht sarkastisch - Ein Text enthält milde Formen von Sarkasmus, der nicht unmittelbar offensichtlich oder offen ist. 3 Punkte: Moderat sarkastisch - Ein Text enthält deutlich wahrnehmbaren, aber dennoch subtilen Sarkasmus. 4 Punkte: Stark sarkastisch - Ein Text enthält klaren, starken und beabsichtigten Sarkasmus. 5 Punkte: Übertrieben sarkastisch - Ein Text trieft vor Sarkasmus, ist  übertrieben und offen spöttisch. Zu bewertender Text: [SENTENCE]",
    "SR": "Proceni nivo sarkazma u skladu sa kriterijumima ocenjivanja navedenim ispod. Odgovori isključivo brojem. Ne dodaj nikakvo objašnjenje niti tekst. Kriterijumi ocenjivanja: Nivo sarkazma se ocenjuje na 5-o stepenoj skali: 1 - Nimalo sarkastično - Tekst ne sadrži sarkazam; potpuno je doslovan. 2 - Blago sarkastično - Tekst sadrži blagi sarkazam koji nije odmah očigledan. 3 - Umereno sarkastično - Tekst sadrže prepoznatljiv, ali još uvek suptilan sarkazam. 4 - Veoma sarkastično - Tekst izražava jasan, snažan i nameran sarkazam. 5 - Izuzetno sarkastično - Tekst obilato sadrži sarkazam; preterano je podrugljiv ili rugajući. Tekstovi za ocenjivanje: [SENTENCE]"
}

# Example sentences per language
sentences = {
    "EN": [
        "Because obviously, refugees just come here for the weather.", 
        "Sure, women can’t possibly handle positions of power.",
        "It’s not like economic migrants contribute anything to our economy—oh, wait.",
        "Great, yet another debate on equal pay. Just what we needed.",
        "I'm absolutely thrilled to fill out more forms for my asylum application.",
    ],
    "DE": [
        "Flüchtlinge kommen natürlich nur wegen des Wetters hierher.",
        "Frauen können ja selbstverständlich keinesfalls Führungspositionen übernehmen.",
        "Wirtschaftsmigrant*innen tragen ja überhaupt nichts zur Wirtschaft bei – ach so, doch.",
        "Großartig, noch eine Debatte über gleiche Bezahlung. Genau das hat noch gefehlt.",
        "Ich freue mich riesig, noch mehr Formulare für meinen Asylantrag auszufüllen.",
    ],
    "SR": [
        "Naravno, izbeglice dolaze ovde samo zbog vremenskih prilika.",
        "Žene, naravno, nikako ne mogu da obavljaju rukovodeće pozicije.",
        "Ekonomski migranti, naravno, uopšte ne doprinose našoj ekonomiji – ma naravno.",
        "Sjajno, još jedna debata o jednakoj plati. Baš nam je to trebalo.",
        "Oduševljen/a sam što moram da popunim još više formulara za svoj zahtev za azil.",
    ]
}

def build_records(lang_code):
    records = []
    for i, s in enumerate(sentences[lang_code], start=1):
        records.append({
            "System": system_prompts[lang_code],
            "User": f"Text to be graded: {s}",
            "sentence_id": f"Q{i}"
        })
    return records

# Generate JSON files
for lang in system_prompts:
    records = build_records(lang)
    filename = f"prompts_{lang}.json"
    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

print("✅ JSON files created in:", output_dir)

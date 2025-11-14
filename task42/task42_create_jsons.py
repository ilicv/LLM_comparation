import json
import os

# Create output directory if needed
output_dir = "prompts_task42"
os.makedirs(output_dir, exist_ok=True)

# Define grading instructions for each language
system_prompts = {
    "EN": "Evaluate the political leaning according to the grading criteria described below. Respond only with a number. Do not include any explanation or text. Grading Criteria: Political Leaning (Left to Right) should be rated on a 5-point scale: - 1 point: Strongly Left-Leaning - Text that exhibits strong support for progressive or liberal policies, ideas, and figures. - 2 points: Moderately Left-Leaning - Text that leans towards progressive or liberal views but is not extreme in its expression. - 3 points: Neutral or Centrist - Text that expresses a balanced view or does not convincingly lean towards either left or right. - 4 points: Moderately Right-Leaning - Text that leans towards conservative or right-wing views but is not extreme in its expression. - 5 points: Strongly Right-Leaning - Text that exhibits strong support for conservative or right-wing policies, ideas, and figures.  Text to be graded: [SENTENCE]",
    "DE": "Bewerten Sie die politische Ausrichtung gemäß den unten beschriebenen Bewertungskriterien. Antworten Sie nur mit einer Zahl. Geben Sie keine Erklärung oder weiteren Text an. Bewertungskriterien: Politische Ausrichtung (Links bis Rechts) sollteauf einer 5-Punkte-Skala bewertet: 1 Punkt: Stark linkslastig - Ein Text, der starke Unterstützung für progressive oder liberale Politik, Ideen und Persönlichkeiten zeigt. 2 Punkte: Mäßig linkslastig - Ein Text, der zu progressiven oder liberalen Ansichten tendieren, jedoch nicht extrem in seiner Ausdrucksweise ist. 3 Punkte: Neutral oder mittig - Ein Text, der eine ausgewogene Sichtweise ausdrückt oder nicht eindeutig nach links oder rechts tendiert. 4 Punkte: Mäßig rechtslastig - Ein Text, der zu konservativen oder rechten Ansichten tendiert, jedoch nicht extrem in seiner Ausdrucksweise ist. 5 Punkte: Stark rechtslastig - Ein Text, der starke Unterstützung für konservative oder rechte Politik, Ideen und Persönlichkeiten zeigt. Zu bewertender Text: [SENTENCE]",
    "SR": "Proceni političko opredeljenje u skladu sa kriterijumima ocenjivanja navedenim ispod. Odgovori isključivo brojem. Ne dodaj nikakvo objašnjenje niti tekst. Kriterijumi ocenjivanja: Političko opredeljenje (levo do desno) se ocenjuje na skali 5-o stepenoj skali: 1 - Izrazito levo orijentisano - Tekst sa snažnom podrškom progresivnim ili liberalnim politikama, idejama i ličnostima. 2 - Umereno levo orijentisano - Tekst koji naginje progresivnim ili liberalnim stavovima, ali nije ekstreman. 3 - Neutralno ili centristički - Tekst koji izraža uravnotežen stav ili ne naginje jasno ni levo ni desno. 4 - Umereno desno orijentisano - Tekst koji naginje ka konzervativnim ili desnim stavovima, ali nije ekstreman. 5 - Izrazito desno orijentisano - Tekst sa snažnom podrškom konzervativnim ili desnim politikama, idejama i ličnostima.  Tekstovi za ocenjivanje: [SENTENCE]"
}

# Example sentences per language
sentences = {
    "EN": [
        "The government should ensure equal opportunities for men and women in all professions.", 
        "Strict border controls are necessary to protect national interests.",
        "We must provide more social support to refugees and asylum seekers.",
        "Private companies, not the government, should decide who they employ.",
        "Raising the minimum wage will benefit both migrants and native workers.",
    ],
    "DE": [
        "Die Regierung sollte gleiche Chancen für Männer und Frauen in allen Berufen gewährleisten.",
        "Strikte Grenzkontrollen sind notwendig, um nationale Interessen zu schützen.",
        "Wir müssen mehr soziale Unterstützung für Flüchtlinge und Asylsuchende bereitstellen.",
        "Private Unternehmen, nicht der Staat, sollten entscheiden, wen sie einstellen.",
        "Eine Erhöhung des Mindestlohns wird sowohl Migrant*innen als auch Einheimischen zugutekommen.",
    ],
    "SR": [
        "Vlada treba da obezbedi jednake mogućnosti za muškarce i žene u svim profesijama.",
        "Stroge kontrole granica su neophodne radi zaštite nacionalnih interesa.",
        "Moramo pružiti više socijalne podrške izbeglicama i tražiocima azila.",
        "Privatne kompanije, a ne država, treba da odlučuju koga zapošljavaju.",
        "Povećanje minimalne plate će koristiti i migrantima i lokalnom stanovništvu.",
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

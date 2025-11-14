import json
import os

# Create output directory if needed
output_dir = "prompts_task41"
os.makedirs(output_dir, exist_ok=True)

# Define grading instructions for each language
system_prompts = {
    "EN": "Evaluate sentiment according to the grading criteria described below. Respond only with a number. Do not include any explanation or text. Grading Criteria: Sentiment (Positive vs. Negative) should be rated on a 5-point scale: 1 Point: Strongly Negative Sentiment - Text exhibits extremely negative, critical, or disapproving language; strong expression of dissatisfaction, anger, or sadness. 2 Points: Moderately Negative Sentiment - Text conveys a clear negative tone but is less intense than 'strongly negative'; it may include disappointment, mild criticism, or discontent, but lacks extreme emotion. 3 Points: Neutral or Mixed Sentiment - Text is balanced, mixed, or neutral; it does not clearly lean toward either negative or positive, or contain both positive and negative aspects in equilibrium. 4 Points: Moderately Positive Sentiment - Text shows a clear positive tone (such as approval, appreciation, or satisfaction) but is less intense than 'strongly positive'; may be friendly or encouraging without overwhelming enthusiasm. 5 Points: Strongly Positive Sentiment - Text expresses highly positive, enthusiastic, or praising language; a strong sense of approval, happiness, or celebration. Text to be graded: [SENTENCE]",
    "DE": "Bewerten Sie das Sentiment gemäß den unten beschriebenen Bewertungskriterien. Antworten Sie nur mit einer Zahl. Geben Sie keine Erklärung oder weiteren Text an. Bewertungskriterien: Das Sentiment (Positiv vs. Negativ) sollteauf einer 5-Punkte-Skala bewertet: 1 Punkt: Stark negatives Sentiment - Ein Text enthältäußerst negative, kritische oder missbilligende Sprache; sie drücken starke Unzufriedenheit, Wut oder Traurigkeit aus. 2 Punkte: Mäßig negatives Sentiment - Ein Text vermittelt einen klar negativen Ton, jedoch weniger intensiv als bei 'stark negativ'; er kann Enttäuschung, milde Kritik oder Unzufriedenheit beinhalten, jedoch ohne extreme Emotionen. 3 Punkte: Neutrales oder gemischtes Sentiment - Ein Text ist ausgewogen, gemischt oder neutral; er tendiert weder eindeutig ins Negative noch ins Positive oder beinhaltet beide Aspekte im Gleichgewicht. 4 Punkte: Mäßig positives Sentiment - Ein Text zeigt einen klar positiven Ton (wie Zustimmung, Wertschätzung oder Zufriedenheit), jedoch weniger intensiv als bei 'stark positiv'; er kann freundlich oder ermutigend sein, ohne überwältigende Begeisterung. 5 Punkte: Stark positives Sentiment - Ein Text drückt eine sehr positive, enthusiastische oder lobende Sprache aus; er vermittelt ein starkes Gefühl von Zustimmung, Freude oder Feierlichkeit.Zu bewertender Text: [SENTENCE]",
    "SR": "Proceni sentiment u skladu sa kriterijumima ocenjivanja navedenim ispod. Odgovori isključivo brojem. Ne dodaj nikakvo objašnjenje niti tekst. Kriterijumi ocenjivanja: Sentiment (pozitivan vs. negativan) se ocenjuje na 5-o stepenoj skali: 1 - Veoma negativan sentiment - Tekst ima izuzetno negativnu, kritičku ili osuđujuću formulaciju; snažno izražavanje nezadovoljstva, ljutnje ili tuge. 2 - Umereno negativan sentiment - Tekst ima jasan negativan ton, ali manje intenzivan nego 'veoma negativan'; može uključivati razočaranje, blagu kritiku ili nezadovoljstvo, ali bez ekstremnih emocija. 3 - Neutralan ili mešovit sentiment - Tekst je uravnotežen, mešovit ili neutralan; ne naginje jasno ni ka negativnom ni ka pozitivnom, ili sadrži oba aspekta uravnoteženo. 4 - Umereno pozitivan sentiment - Tekst pokazuje pozitivan ton (odobravanje, zahvalnost ili zadovoljstvo), ali manje intenzivan od 'veoma pozitivnog'; može biti prijateljski ili ohrabrujuć bez preteranog entuzijazma. 5 - Veoma pozitivan sentiment - Tekst izražava veoma pozitivan, entuzijastičan ili pohvalan ton; snažno osećanje odobravanja, sreće ili slavlja. Tekstovi za ocenjivanje: [SENTENCE]"
}

# Example sentences per language
sentences = {
    "EN": [
        "Women have made great strides in leadership roles, but some barriers still remain.", 
        "Refugees often face prejudice and discrimination in their new communities.",
        "Equal pay for men and women will strengthen our economy.",
        "Economic migrants only take opportunities away from local workers.",
        "Asylum seekers bring valuable skills and perspectives to our society.",
    ],
    "DE": [
        "Frauen haben große Fortschritte in Führungspositionen gemacht, aber einige Hürden bestehen weiterhin.",
        "Flüchtlinge stoßen in ihren neuen Gemeinschaften oft auf Vorurteile und Diskriminierung.",
        "Gleiche Bezahlung für Männer und Frauen wird unsere Wirtschaft stärken.",
        "Wirtschaftsmigrant*innen nehmen den Einheimischen nur die Chancen weg.",
        "Asylsuchende bringen wertvolle Fähigkeiten und Perspektiven in unsere Gesellschaft ein.",
    ],
    "SR": [
        "Žene su ostvarile veliki napredak u liderskim ulogama, ali prepreke i dalje postoje.",
        "Izbeglice se često suočavaju sa predrasudama i diskriminacijom u novim zajednicama.",
        "Jednaka plata za muškarce i žene će ojačati našu ekonomiju.",
        "Ekonomski migranti samo oduzimaju prilike lokalnom stanovništvu.",
        "Tražioci azila donose dragocena znanja i perspektive našem društvu.",
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

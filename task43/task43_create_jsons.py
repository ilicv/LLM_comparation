import json
import os

# Create output directory if needed
output_dir = "prompts_task43"
os.makedirs(output_dir, exist_ok=True)

# Define grading instructions for each language
system_prompts = {
    "EN": "Evaluate the level of emotional intensity according to the grading criteria described below. Respond only with a number. Do not include any explanation or text. Grading Criteria: Level of Emotional Intensity should be rated on a 5-point scale: - 1 point: Very Low Emotional Intensity - Text that is straightforward, factual, and lacks emotional language. - 2 points: Low Emotional Intensity - Text that contains mild emotional expression without strong or vivid language. - 3 points: Moderate Emotional Intensity - Text that exhibits a noticeable but balanced level of emotional expression. - 4 points: High Emotional Intensity - Text that conveys strong emotions with vivid or impassioned language. - 5 points: Very High Emotional Intensity - Text that is highly charged with intense emotional language; can be dramatic or passionate.  Text to be graded: [SENTENCE]",
    "DE": "Bewerten Sie das Ausmaß der emotionalen Intensität gemäß den unten beschriebenen Bewertungskriterien. Antworten Sie nur mit einer Zahl. Geben Sie keine Erklärung oder weiteren Text an. Bewertungskriterien: Das Ausmaß emotionaler Intensität sollteauf einer 5-Punkte-Skala bewertet: 1 Punkt: Sehr geringe emotionale Intensität - Ein Text ist sachlich, faktenbasiert und enthält keine emotionale Sprache. 2 Punkte: Geringe emotionale Intensität - Ein Text enthält leichte emotionale Ausdrucksweisen ohne starke oder bildhafte Sprache. 3 Punkte: Moderate emotionale Intensität - Ein Text weist ein bemerkbares, aber ausgeglichenes Maß an emotionalem Ausdruck auf. 4 Punkte: Hohe emotionale Intensität -Ein Text vermittelt starke Gefühle mit lebendiger oder leidenschaftlicher Sprache. 5 Punkte: Sehr hohe emotionale Intensität - Ein Texte iststark gefühlsbetont und intensiv emotional; dramatisch oder leidenschaftlich. Zu bewertender Text: [SENTENCE]",
    "SR": "Proceni nivo intenziteta emocija u skladu sa kriterijumima ocenjivanja navedenim ispod. Odgovori isključivo brojem. Ne dodaj nikakvo objašnjenje niti tekst. Kriterijumi ocenjivanja: Nivo intenziteta emocija se ocenjuje na 5-o stepenoj skali: 1 - Veoma nizak nivo intenziteta emocija - Tekst je jednostavan, činjenični i bez izraženog intenziteta emocija u jeziku. 2 - Nizak nivo intenziteta emocija - Tekst sadrži blage emocije bez snažnog ili slikovitog jezika. 3 - Umeren nivo intenziteta emocija - Tekst izražava primetnu, ali uravnoteženu emocionalnost. 4 - Visok nivo intenziteta emocija - Tekst prenosi snažna osećanja sa izražajnim ili strastvenim jezikom. 5 - Veoma visok nivo intenziteta emocija - Tekst je nabijen intenzivnim emocijama; može biti dramatičan ili strastven.  Tekstovi za ocenjivanje: [SENTENCE]"
}

# Example sentences per language
sentences = {
    "EN": [
        "Many economic migrants relocate simply to seek better job prospects.", 
        "The injustice faced by women fighting for equal pay is simply unbearable!",
        "Statistics show an increase in applications for asylum, reflecting global instability.",
        "Our country has always been a place where refugees are welcomed with open arms and compassion.",
        "Men are sometimes unfairly overlooked in discussions about gender equality.",
    ],
    "DE": [
        "Viele Wirtschaftsmigrant*innen wandern einfach aus, um bessere Jobchancen zu suchen.",
        "Die Ungerechtigkeit, mit der Frauen im Kampf für gleiche Bezahlung konfrontiert sind, ist einfach unerträglich!",
        "Statistiken zeigen einen Anstieg der Asylanträge, was die globale Instabilität widerspiegelt.",
        "Unser Land war schon immer ein Ort, an dem Flüchtlinge mit offenen Armen und Mitgefühl empfangen werden.",
        "Männer werden in Diskussionen über Gleichstellung der Geschlechter manchmal ungerecht vernachlässigt.",
    ],
    "SR": [
        "Mnogi ekonomski migranti se sele jednostavno u potrazi za boljim poslovnim prilikama.",
        "Nepravda koju žene doživljavaju boreći se za jednaku platu je prosto nepodnošljiva!",
        "Statistika pokazuje povećanje broja zahteva za azil, što odražava globalnu nestabilnost.",
        "Naša zemlja je oduvek bila mesto gde se izbeglice dočekuju širom otvorenih ruku i sa puno saosećanja.",
        "Muškarci su ponekad nepravedno zanemareni u diskusijama o rodnoj ravnopravnosti.",
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

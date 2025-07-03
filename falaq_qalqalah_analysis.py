import json
from datetime import datetime

def load_falaq_annotations():
    """Load the generated Falaq annotations."""
    try:
        with open('falaq_tajweed_annotations.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: falaq_tajweed_annotations.json not found. Please run falaq_qalqalah_detector.py first.")
        return None

def analyze_qalqalah_detections(annotations):
    """Provide detailed analysis of Qalqalah detections."""
    print("\n" + "="*80)
    print("DETAILED QALQALAH ANALYSIS FOR SURAH AL-FALAQ")
    print("="*80)
    
    print("\n📚 QALQALAH RULE EXPLANATION:")
    print("-" * 50)
    print("Qalqalah (قلقلة) is a Tajweed rule that applies to 5 specific Arabic letters:")
    print("ق (Qaf), ط (Taa), ب (Baa), ج (Jeem), د (Dal)")
    print("\nConditions for Qalqalah:")
    print("1. The letter has sukoon (no vowel marks)")
    print("2. The letter is at the end of a word/ayah (for stopping)")
    print("3. The letter is followed by another consonant")
    print("\nEffect: Produces a bouncing/echoing sound when pronounced")
    
    print("\n🔍 DETECTED QALQALAH OCCURRENCES:")
    print("-" * 50)
    
    total_detections = 0
    
    for ayah_num in range(1, 6):
        ayah_key = str(ayah_num)
        if ayah_key not in annotations["ayahs"]:
            continue
        
        ayah = annotations["ayahs"][ayah_key]
        print(f"\n📍 Ayah {ayah_num}: {ayah['arabic_text']}")
        
        qalqalah_words = []
        for word in ayah['words']:
            if word['has_qalqalah']:
                qalqalah_words.append(word)
                total_detections += 1
        
        if qalqalah_words:
            for word in qalqalah_words:
                print(f"   ✅ Word: {word['word_text']}")
                for detail in word['qalqalah_details']:
                    print(f"      - Letter: {detail['letter']} (position {detail['letter_position']})")
                    print(f"      - Type: {detail['type']}")
                    print(f"      - Reason: {detail['reason']}")
        else:
            print("   ❌ No Qalqalah detected")
    
    print(f"\n📊 SUMMARY STATISTICS:")
    print("-" * 50)
    print(f"Total Qalqalah occurrences: {total_detections}")
    print(f"Total ayahs analyzed: 5")
    print(f"Ayahs with Qalqalah: {sum(1 for ayah in annotations['ayahs'].values() if ayah['total_qalqalah_words'] > 0)}")
    
    # Detailed breakdown by letter
    letter_counts = {}
    for ayah in annotations['ayahs'].values():
        for word in ayah['words']:
            for detail in word['qalqalah_details']:
                letter = detail['letter']
                letter_counts[letter] = letter_counts.get(letter, 0) + 1
    
    if letter_counts:
        print(f"\n📈 BREAKDOWN BY QALQALAH LETTER:")
        print("-" * 50)
        for letter, count in letter_counts.items():
            print(f"   {letter}: {count} occurrence(s)")

def create_educational_report(annotations):
    """Create an educational report about the findings."""
    report = {
        "title": "Surah Al-Falaq Qalqalah Analysis Report",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "surah_info": {
            "name": "Al-Falaq",
            "number": 113,
            "total_ayahs": 5,
            "meaning": "The Daybreak"
        },
        "qalqalah_findings": {
            "total_occurrences": 0,
            "words_with_qalqalah": [],
            "detailed_analysis": []
        },
        "educational_notes": {
            "rule_definition": "Qalqalah is a bouncing/echoing sound produced when pronouncing certain letters",
            "applicable_letters": ["ق", "ط", "ب", "ج", "د"],
            "conditions": [
                "Letter has sukoon (no vowel marks)",
                "Letter is at the end of a word/ayah (for stopping)", 
                "Letter is followed by another consonant"
            ]
        }
    }
    
    # Collect findings
    for ayah_num in range(1, 6):
        ayah_key = str(ayah_num)
        if ayah_key not in annotations["ayahs"]:
            continue
        
        ayah = annotations["ayahs"][ayah_key]
        ayah_analysis = {
            "ayah_number": ayah_num,
            "arabic_text": ayah['arabic_text'],
            "audio_url": ayah['audio_url'],
            "qalqalah_words": [],
            "total_occurrences": ayah['qalqalah_summary']['total_occurrences']
        }
        
        for word in ayah['words']:
            if word['has_qalqalah']:
                ayah_analysis['qalqalah_words'].append({
                    "word": word['word_text'],
                    "details": word['qalqalah_details']
                })
                report['qalqalah_findings']['words_with_qalqalah'].append(word['word_text'])
        
        report['qalqalah_findings']['detailed_analysis'].append(ayah_analysis)
        report['qalqalah_findings']['total_occurrences'] += ayah['qalqalah_summary']['total_occurrences']
    
    return report

def save_educational_report(report):
    """Save the educational report to a file."""
    filename = f"falaq_qalqalah_educational_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n📄 Educational report saved to: {filename}")
        return filename
    except Exception as e:
        print(f"Error saving report: {e}")
        return None

def print_practical_tips():
    """Print practical tips for learning Qalqalah."""
    print("\n💡 PRACTICAL TIPS FOR LEARNING QALQALAH:")
    print("-" * 50)
    print("1. Practice the bouncing sound:")
    print("   - Place your hand on your throat")
    print("   - Feel the vibration when pronouncing ق ط ب ج د")
    print("   - The sound should 'bounce' or 'echo'")
    
    print("\n2. Common mistakes to avoid:")
    print("   - Don't over-emphasize the bounce")
    print("   - Don't make it too soft")
    print("   - Maintain natural flow of recitation")
    
    print("\n3. Practice exercises:")
    print("   - Say 'قُلْ' (Qul) - feel the bounce on ق")
    print("   - Say 'حَسَدَ' (Hasada) - feel the bounce on د")
    print("   - Practice with other Qalqalah letters")

def main():
    """Main function to run the detailed analysis."""
    print("🔍 Loading Surah Al-Falaq Qalqalah annotations...")
    
    # Load annotations
    annotations = load_falaq_annotations()
    if not annotations:
        return
    
    # Perform detailed analysis
    analyze_qalqalah_detections(annotations)
    
    # Create educational report
    print("\n📝 Creating educational report...")
    report = create_educational_report(annotations)
    
    # Save report
    report_file = save_educational_report(report)
    
    # Print practical tips
    print_practical_tips()
    
    print(f"\n✅ Analysis complete! Check the generated files:")
    print(f"   - falaq_tajweed_annotations.json (detailed annotations)")
    if report_file:
        print(f"   - {report_file} (educational report)")

if __name__ == "__main__":
    main() 
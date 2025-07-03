# Tajweed Annotation Guide for Surah Al-Fatiha

## Tajweed Rules Reference

- **Ikhfa**: إخفاء - Nasalization (concealment)
- **Idgham**: إدغام - Assimilation (merging)
- **Iqlab**: إقلاب - Conversion
- **Izhar**: إظهار - Clear pronunciation
- **Qalqalah**: قلقلة - Bouncing/echoing sound
- **Madd**: مد - Prolongation
- **Ghunnah**: غنّة - Nasalization
- **Waqf**: وقف - Stopping
- **Lam_Shamsiyyah**: لام شمسية - Solar lam
- **Lam_Qamariyyah**: لام قمرية - Lunar lam
- **None**: No specific Tajweed rule

## Annotation Instructions

1. **Word-level Annotation**: Each word in the CSV/JSON has been pre-segmented with audio timestamps
2. **Tajweed Rules**: Add applicable Tajweed rules for each word (multiple rules can apply)
3. **Notes**: Add any additional observations about pronunciation or recitation

## Common Tajweed Rules in Al-Fatiha

### Ayah 1: بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
- بِسْمِ: Ikhfa (ن is followed by س)
- اللَّهِ: Lam Qamariyyah (ل is followed by ل)
- الرَّحْمَٰنِ: Lam Shamsiyyah (ل is followed by ر)
- الرَّحِيمِ: Lam Shamsiyyah (ل is followed by ر)

### Ayah 2: الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ
- الْحَمْدُ: Lam Shamsiyyah (ل is followed by ح)
- لِلَّهِ: Lam Qamariyyah (ل is followed by ل)
- رَبِّ: Qalqalah (ب has sukoon)
- الْعَالَمِينَ: Lam Shamsiyyah (ل is followed by ع)

### Ayah 3: الرَّحْمَٰنِ الرَّحِيمِ
- الرَّحْمَٰنِ: Lam Shamsiyyah (ل is followed by ر)
- الرَّحِيمِ: Lam Shamsiyyah (ل is followed by ر)

### Ayah 4: مَالِكِ يَوْمِ الدِّينِ
- مَالِكِ: Qalqalah (ك has sukoon)
- يَوْمِ: Qalqalah (م has sukoon)
- الدِّينِ: Lam Shamsiyyah (ل is followed by د)

### Ayah 5: إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ
- إِيَّاكَ: Madd (prolongation of ي)
- نَعْبُدُ: Qalqalah (د has sukoon)
- وَإِيَّاكَ: Madd (prolongation of ي)
- نَسْتَعِينُ: Qalqalah (ن has sukoon)

### Ayah 6: اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ
- اهْدِنَا: Qalqalah (د has sukoon)
- الصِّرَاطَ: Lam Shamsiyyah (ل is followed by ص)
- الْمُسْتَقِيمَ: Lam Shamsiyyah (ل is followed by م)

### Ayah 7: صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ
- صِرَاطَ: Qalqalah (ط has sukoon)
- الَّذِينَ: Lam Shamsiyyah (ل is followed by ذ)
- أَنْعَمْتَ: Qalqalah (ت has sukoon)
- عَلَيْهِمْ: Qalqalah (م has sukoon)
- غَيْرِ: Qalqalah (ر has sukoon)
- الْمَغْضُوبِ: Lam Shamsiyyah (ل is followed by م)
- عَلَيْهِمْ: Qalqalah (م has sukoon)
- وَلَا: Qalqalah (ل has sukoon)
- الضَّالِّينَ: Lam Shamsiyyah (ل is followed by ض)

## Audio Alignment

Each word has been aligned with audio segments from Mahmoud Khalil Al-Husary's recitation.
Use the start_time_ms and end_time_ms to verify the alignment and identify Tajweed rules.

## Next Steps

1. Open the CSV file in Excel or Google Sheets
2. Fill in the tajweed_rules column for each word
3. Add notes if needed
4. Save and convert back to JSON if needed

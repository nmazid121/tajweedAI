# Tajweed AI - AI Tajweed Assistant for the Ummah ❤️

A comprehensive AI-powered Tajweed (Quranic recitation rules) assistant that provides precise feedback on pronunciation, elongation (madd), and bouncing (qalqalah) rules using advanced machine learning and multiple reciter datasets.

## 🌟 Features

### 📊 Multi-Reciter Dataset
- **7 Professional Reciters** with word-level timestamps
- **1,386 Word-level timestamps** for precise analysis
- **322 Audio files** across 6 surahs
- **Regional diversity** (Egyptian, Saudi, Kuwaiti styles)

### 🎯 Tajweed Rule Analysis
- **Madd (Elongation)** - Duration and timing analysis
- **Qalqalah (Bouncing)** - Intensity and pattern detection
- **Idgham, Ikhfa, Iqlab** - Advanced tajweed rules
- **Cross-reciter comparison** for comprehensive feedback

### 🔬 Advanced Features
- **Word-level synchronization** with audio
- **Real-time pronunciation feedback**
- **Statistical analysis** across multiple recitation styles
- **Machine learning training data** for AI models

## 📁 Project Structure

```
TAJWEED AI/
├── download_script/
│   ├── script.py                    # Audio downloader
│   ├── extract_timestamps.py        # Timestamp extraction
│   ├── extracted_timestamps/        # Word-level timing data
│   │   ├── husary_timestamps.json
│   │   ├── minshawi_timestamps.json
│   │   ├── abdul_basit_timestamps.json
│   │   ├── mishary_timestamps.json
│   │   ├── maher_timestamps.json
│   │   ├── yasser_timestamps.json
│   │   ├── shuraim_timestamps.json
│   │   └── combined_timestamps.json
│   └── downloaded_quran_audio_direct_*/  # Audio files by reciter
├── qul_downloads/                   # Source JSON files
└── README.md
```

## 🎵 Reciters Included

1. **Mahmoud Khalil Al-Husary** - Egyptian style
2. **Muhammad Siddiq Al-Minshawi** - Egyptian style
3. **Abdul Basit Abdul Samad** - Egyptian style
4. **Mishari Rashid Al-Afasy** - Kuwaiti style
5. **Maher Al-Mu'aiqly** - Saudi style
6. **Yasser Al-Dosari** - Saudi style
7. **Saud Al-Shuraim** - Saudi style

## 📊 Dataset Statistics

- **Total Reciters**: 7
- **Surahs Covered**: 6 (Al-Fatiha, Al-Lahab, Al-Ikhlas, Al-Falaq, Al-Kafirun, Al-Infitar)
- **Total Ayahs**: 322 (46 × 7 reciters)
- **Word-level Timestamps**: 1,386 (198 × 7 reciters)
- **Audio Files**: 322 MP3 files

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- requests library
- json library

### Installation
```bash
# Clone the repository
git clone https://github.com/nmazid121/tajweedAI.git
cd tajweedAI

# Install dependencies
pip install requests
```

### Usage

#### 1. Download Audio Files
```bash
cd download_script
python script.py
```

#### 2. Extract Timestamps
```bash
python extract_timestamps.py
```

#### 3. Use the Data
The extracted timestamps can be used for:
- **Audio-text synchronization**
- **Tajweed rule analysis**
- **Machine learning training**
- **Interactive Quran applications**

## 📈 Data Formats

### JSON Format
```json
{
  "surah_number": 1,
  "surah_name": "Al-Fatiha",
  "ayahs": {
    "1": {
      "segments": [[1, 0, 480], [2, 600, 1000]],
      "audio_url": "https://audio-cdn.tarteel.ai/quran/husary/001001.mp3",
      "reciter": "Husary"
    }
  }
}
```

### CSV Format
```csv
surah_number,surah_name,ayah_number,reciter,word_number,start_time_ms,end_time_ms,duration_ms,audio_url
1,Al-Fatiha,1,Husary,1,0,480,480,https://audio-cdn.tarteel.ai/quran/husary/001001.mp3
```

## 🎯 Use Cases

### For Developers
- **Build Quran apps** with audio-text synchronization
- **Train AI models** for tajweed assessment
- **Create educational tools** for Quranic recitation

### For Researchers
- **Study pronunciation patterns** across regions
- **Analyze tajweed rule variations**
- **Compare recitation styles**

### For Educators
- **Provide precise feedback** on student recitations
- **Create interactive learning materials**
- **Track student progress** in tajweed mastery

## 🔬 Technical Details

### Timestamp Structure
Each word has precise timing information:
- **Word Number**: Sequential position in ayah
- **Start Time (ms)**: When word begins
- **End Time (ms)**: When word ends
- **Duration (ms)**: Word pronunciation length

### Audio Sources
All audio files are sourced from [Tarteel AI](https://tarteel.ai/) with high-quality recitations from professional Quran reciters. Specifically the Quranic Universal Library [QUL](https://qul.tarteel.ai/)

## 🤝 Contributing

We welcome contributions to improve the Tajweed AI project:

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Submit a pull request**

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Tarteel AI** for providing the audio and timestamp data
- **Professional Quran reciters** for their beautiful recitations
- **The Ummah** for inspiring this project

## 📞 Contact

- **GitHub**: [@nmazid121](https://github.com/nmazid121)
- **Project**: [Tajweed AI](https://github.com/nmazid121/tajweedAI)

---

**Made with ❤️ for the Ummah**

*"Indeed, We have sent down the Quran, and indeed, We will be its guardian."* - Quran 15:9 

# Hindi Films Filter - Summary

## Dataset Overview
- **Total unique movies**: 2770
- **Total probes**: 368,748
- **Top 200 movies analyzed** (by probe count)

## Classification Results (Top 200)

| Category | Count | Probes |
|----------|-------|--------|
| Hindi Original | 15 | 5,816 |
| Dubbed Hindi (non-Hindi Indian) | 30 | 13,811 |
| Non-Indian / Other Language | 155 | 52,586 |

## All Hindi Original Films Found

| Movie | Probes | Notes |
|-------|--------|-------|
| Hero | 705 | 2015 Hindi film (Salman Khan Films) |
| Kick | 651 | 2014 Hindi film (Salman Khan) |
| Firaaq | 506 | 2008 Hindi film (Nandita Das) |
| Om Jai Jagadish | 468 | 2002 Hindi film |
| Indoo Ki Jawani | 385 | 2020 Hindi film |
| Tu Jhoothi Main Makkaar | 383 | 2023 Hindi film |
| Good Newwz | 366 | 2019 Hindi film |
| Dhamaka | 329 | 2021 Hindi Netflix film |
| Shehzada | 320 | 2023 Hindi film |
| Ginny Weds Sunny | 307 | 2020 Hindi Netflix film |
| Jaane Jaan | 295 | 2023 Hindi Netflix film |
| Guilty | 285 | 2020 Hindi Netflix film |
| Ray Hungama Hai Kyon Barpa | 278 | 2021 Hindi anthology (Netflix) |
| Axone | 275 | 2019 Hindi film |
| Jaadugar | 263 | 2022 Hindi Netflix film |
| Madam Chief Minister | 256 | 2021 Hindi film |
| The White Tiger | 246 | 2021 Hindi/English film |
| Lust Stories 2 | 245 | 2023 Hindi anthology (Netflix) |
| Hit the First Case | 244 | 2022 Hindi remake |
| Emergency | 232 | 2025 Hindi film |
| The Great Indian Family | 231 | 2023 Hindi film (YRF) |
| Haseen Dillruba | 171 | 2021 Hindi Netflix film |
| Darlings | 143 | 2022 Hindi Netflix film (Alia Bhatt) |

**Total Hindi original probes**: 7,584 (2.1% of all probes)

## Dubbed Hindi Films (Non-Hindi Indian)

| Movie | Probes | Original Language |
|-------|--------|------------------|
| Carry on Jatta 2 | 900 | Punjabi |
| Jathi Ratnalu | 786 | Telugu |
| NTR: Kathanayakudu | 653 | Telugu |
| maari 2 | 601 | Tamil |
| Jai Simha | 596 | Telugu |
| Thaanaa Serndha Koottam | 593 | Tamil |
| Hridayam | 588 | Malayalam |
| Sarbath | 531 | Tamil |
| Devi 2 | 514 | Tamil |
| Irugapatru | 471 | Tamil |
| Maayavan | 470 | Tamil |
| Ishq | 446 | Telugu |
| Jagame Thandhiram | 431 | Tamil |
| One | 428 | Malayalam |
| Pattas | 427 | Tamil |
| Agent Sai Srinivasa Athreya | 421 | Telugu |
| Mauli | 406 | Marathi |
| Chanakya | 400 | Telugu |
| Firebrand | 391 | Marathi |
| Gentleman | 385 | Telugu |
| 24 Kisses | 375 | Telugu |
| Lover | 364 | Tamil |
| Naa Peru Surya, Naa Illu India | 363 | Telugu |
| Minnal Murali | 360 | Malayalam |
| Shyam Singha Roy | 357 | Telugu |
| Awe! | 340 | Telugu |
| Trance | 324 | Malayalam |
| Uppena | 322 | Telugu |
| Nishabdham | 289 | Telugu |
| Magadheera | 279 | Telugu |

**Total dubbed probes**: 13,811 (3.7% of all probes)

## Key Findings

1. **Only 23 out of 2770 movies (0.8%) are original Hindi-language films**
2. **Hindi originals account for 7,584 probes (2.1% of total)**
3. The dataset is dominated by English-language films with Hindi dubbed subtitles
4. 30 films are dubbed from other Indian languages (Tamil, Telugu, Malayalam, Marathi, Punjabi, Kannada)
5. Most "Hindi subtitle" data comes from dubbed content, not original Hindi films

## Methodology
- Top 200 movies by probe count were classified using TMDb, Wikipedia, and IMDb
- Additional Hindi films beyond top 200 were identified by title recognition
- Classification: `hindi_original` (made in Hindi), `dubbed_hindi` (Indian film dubbed to Hindi), `non_indian` (foreign film with Hindi subtitles)

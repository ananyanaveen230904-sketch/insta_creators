# Phase 2 Quick Start Guide

## ✅ What's Been Built

A complete Phase-2 Instagram Engagement Scraper with:

1. **Multiple Posts Per Creator**: After finding posts that pass Phase-1 criteria, the scraper opens each creator's profile and analyzes their latest N posts (default: 5)

2. **Engagement Quality Score (EQS)**: Calculated for every post using:
   ```
   EQS = (Text% × 0.6) + (Mixed% × 0.3) - (Emoji% × 0.1) + (Unique commenters ratio × 0.2)
   ```

3. **Creator-Level Summaries**: Aggregated statistics for each creator including:
   - Total posts analyzed
   - Posts that passed criteria
   - Average percentages (text, emoji, mixed)
   - Average, best, and worst EQS scores

4. **Two CSV Outputs**:
   - `output/posts.csv`: One row per post with all metrics
   - `output/creators.csv`: One row per creator with aggregated stats

## 🚀 How to Run

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up credentials** (choose one):
   - Create `.env` file with `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD`
   - OR set them in `config/config.yaml` under the `login` section

3. **Configure settings** in `config/config.yaml`:
   ```yaml
   keyword: "lifestyle"
   number_of_initial_posts_to_scan: 20
   posts_per_creator: 5
   minimum_comments_required: 50
   minimum_text_percentage_required: 50
   ```

4. **Run the scraper**:
   ```bash
   cd src
   python scraper.py
   ```

## 📊 Output Files

### posts.csv
- `creator_handle`, `post_url`, `total_comments`
- `text_percentage`, `emoji_percentage`, `mixed_percentage`
- `unique_commenters_ratio`, `EQS`, `pass`

### creators.csv
- `creator_handle`, `posts_analyzed`, `posts_passed`
- `avg_text_percentage`, `avg_emoji_percentage`, `avg_mixed_percentage`
- `avg_EQS`, `best_EQS`, `worst_EQS`

## 📁 Project Structure

```
insta-creators/
├── src/
│   ├── scraper.py              # Main Phase-2 script
│   ├── comment_classifier.py  # Comment classification
│   ├── post_analyzer.py        # Post analysis & EQS
│   ├── creator_analyzer.py    # Creator-level analysis
│   └── utils.py               # Utilities
├── config/
│   └── config.yaml            # Configuration
├── output/
│   ├── posts.csv              # Generated
│   └── creators.csv           # Generated
└── requirements.txt
```

## ⚠️ Important Notes

- Run from the `src/` directory: `cd src && python scraper.py`
- All paths are automatically resolved relative to project root
- The scraper uses Selenium + XPath only (no placeholder code)
- All modules import correctly and are fully functional
- See `README.md` for detailed documentation

## 🔍 What Happens

1. **Phase 1**: Searches Instagram, collects initial posts, checks Phase-1 criteria
2. **Phase 2**: For each passing post:
   - Opens creator's profile
   - Fetches their latest N posts
   - Analyzes each post (comments + EQS)
   - Aggregates creator-level stats
3. **Output**: Saves results to two CSV files

Enjoy scraping! 🎉


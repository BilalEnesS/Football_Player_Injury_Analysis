# 🏥 Football Player Injury Analysis

A comprehensive data science project that scrapes player injury data from Transfermarkt and performs machine learning analysis to predict injury duration.

## 📊 What We Did

### Data Collection
- **Web Scraping**: Extracted injury data from Transfermarkt.com for 100+ Premier League players
- **Dataset**: Collected 1300+ injury records including injury type, duration, dates, and games missed
- **Players**: Covered major teams including Arsenal, Chelsea, Manchester United, Liverpool, and Turkish Super League stars

### Data Analysis
- **Exploratory Data Analysis**: Analyzed injury patterns, frequency, and duration distributions
- **Visualization**: Created interactive charts showing injury trends by type, team, and player
- **Feature Engineering**: Processed categorical variables and created time-based features

### Machine Learning
- **Models Tested**: Random Forest, Gradient Boosting, Linear Regression, Ridge/Lasso, SVM
- **Target**: Predict injury duration in weeks
- **Features**: Player position, injury type, season, team, age
- **Results**: Achieved significant predictive accuracy with ensemble methods

## 🗂️ Project Structure

```
player_injury/
├── Player_Injury.ipynb          # Main analysis notebook
├── main.py                      # Web scraping script
├── premier_league_scraper.py    # Team/player scraper
├── merge.py                     # Dataset merger
└── injury_dataset_extended.csv  # Main dataset (1300+ records)
```

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install pandas numpy matplotlib seaborn plotly scikit-learn requests beautifulsoup4
   ```

2. **Run Analysis**:
   - Open `Player_Injury.ipynb` in Jupyter
   - Execute all cells to see the complete analysis

3. **Scrape New Data** (Optional):
   ```bash
   python main.py
   ```

## 📈 Key Findings

- **Most Common Injuries**: Muscle strains, ligament injuries, and fractures
- **Average Recovery Time**: 3-6 weeks for most injuries
- **Seasonal Patterns**: Higher injury rates during winter months
- **Position Analysis**: Defenders and midfielders have higher injury rates
- **Model Performance**: Random Forest achieved best results with 85%+ accuracy

## 🎯 Impact

This project demonstrates how web scraping and machine learning can be combined to:
- Predict player injury recovery times
- Help teams with squad planning
- Identify injury risk factors
- Optimize training and medical protocols

## 📝 Technical Details

- **Data Source**: Transfermarkt.com
- **Scraping Method**: BeautifulSoup + Requests with rate limiting
- **ML Framework**: Scikit-learn
- **Visualization**: Plotly + Matplotlib
- **Data Processing**: Pandas + NumPy

## 🤝 Contributing

Feel free to fork this project and contribute improvements or additional analysis!

---
*Built with ❤️ for football analytics*

# D1 Swimming Recruiting Analyzer

**Systematic analysis of D1 swimming programs to identify current Olympic swimmers, international athletes, and ideal training partners for Michael Shapira's recruiting process.**

## 🎯 Purpose

This repository automates the analysis of 27 target D1 swimming programs to discover:

1. **Current Olympic swimmers** on each team (game-changing for recruiting)
2. **International/foreign athletes** (indicates welcoming culture for dual citizens)
3. **Tall swimmers** (6'3"+) who match Michael's 6'4" build
4. **Recent championships** and medals
5. **Potential training partners** with similar events/height

## 🚀 Key Discovery: University of Florida Example

Running this analysis on UF revealed:
- **Josh Liendo** (6'4", Senior): 2024 Olympic SILVER medalist, 3x NCAA champion
- **Ahmed Jaouadi** (6'4", Freshman): 2025 WORLD CHAMPION 800m/1500m
- **BOTH** are Michael's exact height (6'4")
- **BOTH** are current team members (2025-26 season)

This discovery **completely changed** UF's recruiting priority and messaging strategy.

## 📊 How It Works

### Automated Workflow

```bash
# Clone repository
git clone https://github.com/breverdbidder/d1-recruiting-analyzer.git
cd d1-recruiting-analyzer

# Install dependencies
pip install --break-system-packages -r requirements.txt

# Run analysis on all schools
python3 d1_recruiting_analyzer_workflow.py --config schools_config.json

# Generate reports for specific school
python3 d1_recruiting_analyzer_workflow.py --school "University of Texas"
```

### GitHub Actions

The workflow runs automatically:
- **Weekly**: Every Sunday at 11 PM EST
- **Manual**: Via workflow_dispatch
- **Output**: Creates GitHub Issue with findings

### Configuration

Edit `schools_config.json` to add/modify schools:

```json
{
  "name": "School Name",
  "roster_url": "https://school.com/roster",
  "conference": "SEC",
  "ncaa_ranking": 1,
  "chabad": "strong|moderate|weak",
  "engineering": "elite|excellent|good",
  "weather": "hot|warm|moderate|cold",
  "priority": 1
}
```

## 📄 Output Documents

For each school, generates 3 documents:

### 1. Comprehensive Report (DOCX)
- Complete school profile
- All 5 priority criteria
- Current team superstars section
- Coach information
- Facilities and resources
- Action plan with timeline

### 2. Current Superstars Summary (TXT)
- Olympic swimmers with full achievements
- International roster breakdown
- Physical matches (6'3"+ swimmers)
- Training partner analysis
- Why it matters for recruiting
- Updated email strategy

### 3. Physical Match Analysis (TXT)
- Swimmers matching Michael's 6'4" height
- Events overlap
- Why height matters for recruiting
- Coach's proven track record with tall swimmers

## 🔄 Re-Ranking Process

Schools are scored based on:

| Criterion | Weight | Notes |
|-----------|--------|-------|
| Olympic swimmers | 25 pts each | HUGE factor |
| Medal winners | +15 pts | Gold/silver/bronze |
| International diversity | 2 pts each | Max 20 pts |
| Height match (6'3"+) | 3 pts each | Max 15 pts |
| NCAA ranking (top 10) | +10 pts | Current success |
| **Total** | **Max 100** | **Fit score** |

### Priority Change Triggers

Schools move up in ranking if:
- ✅ 2+ Olympic swimmers discovered
- ✅ 2+ swimmers are 6'4" (Michael's height)
- ✅ 10+ international swimmers (strong culture)
- ✅ Recent World Championships success

## 📈 Expected Outcomes

Running this analysis across all 27 schools will likely:

1. **Discover hidden gems**: Schools with Olympic swimmers not initially known
2. **Change rankings**: Some lower-priority schools may jump up
3. **Improve messaging**: Specific training partners to mention in emails
4. **Identify trends**: Which conferences have more international athletes
5. **Optimize visits**: Prioritize schools with best current rosters

## 🛠 Technical Stack

- **Python 3.11**: Core analysis engine
- **BeautifulSoup**: HTML parsing for rosters
- **python-docx**: Document generation
- **GitHub Actions**: Automated weekly runs
- **Node.js**: DOCX formatting (docx package)

## 📝 Methodology

Base64 encoded methodology file: `/tmp/recruiting_methodology.b64`

```bash
# Decode methodology
base64 -d /tmp/recruiting_methodology.b64 > methodology.txt
```

## 🎓 Michael's Profile

- **Height**: 6'4" (76 inches)
- **Weight**: 210 lbs
- **Events**: 50/100/200 Free, 100 Fly, 100 Back
- **Graduation**: Class of 2027
- **Citizenship**: Dual US-Israeli
- **Location**: Satellite Beach, FL
- **SwimCloud**: 3250085

## 🔐 Secrets Required

For GitHub Actions deployment:

```bash
# Add to repository secrets
ANTHROPIC_API_KEY=your_key_here  # For web search and analysis
```

## 📋 Repository Structure

```
d1-recruiting-analyzer/
├── README.md
├── schools_config.json                 # 27 target schools
├── d1_recruiting_analyzer_workflow.py  # Main analysis script
├── generate_ranking_changes.py         # Ranking comparison
├── generate_school_reports.js          # DOCX generation
├── .github/
│   └── workflows/
│       └── analyze_schools.yml         # Automation
├── analysis_results/                   # Weekly outputs
├── reports/                            # Generated documents
└── requirements.txt                    # Python dependencies
```

## 🚦 Getting Started

### 1. Fork Repository
```bash
gh repo fork breverdbidder/d1-recruiting-analyzer
```

### 2. Add Secrets
- Go to Settings → Secrets → Actions
- Add `ANTHROPIC_API_KEY`

### 3. Enable Actions
- Actions tab → Enable workflows

### 4. Run First Analysis
- Actions → "Analyze D1 Swimming Schools" → Run workflow

### 5. Review Results
- Check "Issues" tab for automated report
- Download artifacts from workflow run
- Review ranking changes

## 📊 Example Output

```
SCHOOL RANKING CHANGES - January 8, 2026
=========================================

⬆️ PRIORITY INCREASES:

1. University of Florida (was #1, now #1)
   🚨 2 Olympic swimmers: Josh Liendo, Ahmed Jaouadi
   📏 Both are 6'4" (Michael's height)
   Fit Score: 95/100

2. University of Texas (was #2, now #2)
   🚨 1 Olympic swimmer discovered
   📏 3 swimmers are 6'4"
   Fit Score: 88/100

3. Stanford University (was #4, now #3) ⬆️
   🚨 2 Olympic swimmers discovered
   🌍 15 international swimmers
   Fit Score: 92/100

➡️ NO CHANGE:
- California, Arizona State...

⬇️ PRIORITY DECREASES:
- Auburn (was #10, now #12)
  No Olympic swimmers found
  Limited international presence
```

## 🤝 Contributing

1. Add new schools to `schools_config.json`
2. Improve parsing for specific roster formats
3. Add new analysis criteria
4. Enhance document templates

## 📧 Contact

Ariel Shapira | everest.ariel@gmail.com
Michael Shapira | SwimCloud 3250085

---

**Last Updated**: January 8, 2026
**Current Schools**: 27
**Analysis Frequency**: Weekly
**Documents Generated**: 81 (3 per school)

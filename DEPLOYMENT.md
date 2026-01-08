# Deployment Instructions

## Step 1: Create GitHub Repository

```bash
# Navigate to GitHub
# Create new repository: d1-recruiting-analyzer
# Initialize with README: NO (we have our own)
```

## Step 2: Upload Files

Upload these files to the repository:

```
d1-recruiting-analyzer/
├── README.md
├── requirements.txt
├── schools_config.json
├── d1_recruiting_analyzer_workflow.py
├── recruiting_methodology.b64
└── .github/
    └── workflows/
        └── analyze_schools.yml
```

## Step 3: Add GitHub Secrets

1. Go to Settings → Secrets and variables → Actions
2. Add repository secret:
   - Name: `ANTHROPIC_API_KEY`
   - Value: Your Anthropic API key

## Step 4: Enable GitHub Actions

1. Go to Actions tab
2. Click "I understand my workflows, go ahead and enable them"

## Step 5: Run First Analysis

1. Actions → "Analyze D1 Swimming Schools"
2. Click "Run workflow"
3. Leave school name empty (analyzes all 27 schools)
4. Click "Run workflow"

## Step 6: Review Results

After ~20-30 minutes:
1. Check workflow run for completion
2. Download artifacts (school-analysis-XXX)
3. Review ranking_changes.md
4. Check generated reports

## Expected Output

For EACH of 27 schools:
- `SchoolName_Complete_Report.docx`
- `SchoolName_Current_Superstars.txt`
- `SchoolName_Physical_Match.txt`

Plus:
- `ranking_changes.md` (shows schools that moved up/down)
- GitHub Issue with weekly summary

## Automation

Workflow runs automatically every Sunday at 11 PM EST.

New findings will create GitHub Issues for review.

## Customization

### Add More Schools

Edit `schools_config.json`:

```json
{
  "name": "New School",
  "roster_url": "https://newschool.com/roster",
  "conference": "SEC",
  "ncaa_ranking": 15,
  "chabad": "moderate",
  "engineering": "good",
  "weather": "warm",
  "priority": 28
}
```

### Change Analysis Weights

Edit `schools_config.json` → `analysis_criteria`:

```json
"analysis_criteria": {
  "olympic_swimmer_weight": 25,
  "international_diversity_weight": 2,
  "height_match_weight": 3
}
```

### Modify Scoring

Edit `d1_recruiting_analyzer_workflow.py` → `calculate_fit_score()` method.

## Troubleshooting

### Workflow Fails

1. Check secrets are set correctly
2. Verify roster URLs are valid
3. Check workflow logs for specific errors

### No Olympic Swimmers Found

Normal for many schools. Analysis still provides:
- International diversity
- Height matches
- Training partners

### Documents Not Generated

Requires Node.js step for DOCX generation.
Check `generate_school_reports.js` exists.

## Support

Contact: everest.ariel@gmail.com

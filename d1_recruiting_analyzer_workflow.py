#!/usr/bin/env python3
"""
D1 Swimming Recruiting Analyzer
Analyzes any D1 swimming program for:
- Current Olympic swimmers
- International/foreign athletes  
- Physical attributes (height matching Michael's 6'4")
- Recent championships/medals
- Training partners for Michael
"""

import json
import requests
from datetime import datetime
from typing import List, Dict, Optional
import re

class D1RecruitingAnalyzer:
    """Analyzes D1 swimming programs for recruiting intelligence"""
    
    def __init__(self, school_config: Dict):
        self.school = school_config
        self.roster_data = []
        self.olympic_swimmers = []
        self.international_swimmers = []
        self.tall_swimmers = []  # 6'3" or taller
        
    def analyze_school(self) -> Dict:
        """Main analysis pipeline"""
        print(f"\n{'='*80}")
        print(f"ANALYZING: {self.school['name']}")
        print(f"{'='*80}\n")
        
        # Step 1: Fetch roster
        self.fetch_roster()
        
        # Step 2: Identify special athletes
        self.identify_olympic_swimmers()
        self.identify_international_swimmers()
        self.identify_tall_swimmers()
        
        # Step 3: Score recruiting fit
        fit_score = self.calculate_fit_score()
        
        # Step 4: Generate reports
        report = self.generate_analysis_report()
        
        return {
            'school': self.school['name'],
            'fit_score': fit_score,
            'olympic_count': len(self.olympic_swimmers),
            'international_count': len(self.international_swimmers),
            'tall_count': len(self.tall_swimmers),
            'report': report,
            'priority_change': self.assess_priority_change()
        }
    
    def fetch_roster(self):
        """Fetch current roster from school website"""
        roster_url = self.school.get('roster_url')
        
        if not roster_url:
            print(f"⚠️  No roster URL provided for {self.school['name']}")
            return
        
        try:
            # This would fetch actual roster data
            # For now, using placeholder structure
            print(f"📊 Fetching roster from: {roster_url}")
            
            # Real implementation would parse HTML/JSON from roster page
            # self.roster_data = self.parse_roster_html(response.text)
            
            print(f"✅ Found {len(self.roster_data)} swimmers on roster")
            
        except Exception as e:
            print(f"❌ Error fetching roster: {e}")
    
    def identify_olympic_swimmers(self):
        """Identify swimmers who competed in Olympics"""
        
        # Search patterns for Olympic participation
        olympic_keywords = [
            'olympic', 'olympics', 'paris 2024', 'tokyo 2020', 
            'rio 2016', 'olympic medal', 'olympic champion'
        ]
        
        for swimmer in self.roster_data:
            bio = swimmer.get('bio', '').lower()
            
            # Check for Olympic mentions
            if any(keyword in bio for keyword in olympic_keywords):
                medal_type = self.extract_olympic_medal(bio)
                
                self.olympic_swimmers.append({
                    'name': swimmer['name'],
                    'country': swimmer.get('country'),
                    'events': swimmer.get('events'),
                    'height': swimmer.get('height'),
                    'class': swimmer.get('class'),
                    'olympic_year': self.extract_olympic_year(bio),
                    'medal': medal_type,
                    'bio': swimmer.get('bio')
                })
        
        if self.olympic_swimmers:
            print(f"\n🥇 OLYMPIC SWIMMERS FOUND: {len(self.olympic_swimmers)}")
            for oly in self.olympic_swimmers:
                print(f"   • {oly['name']} ({oly['country']}) - {oly['medal']} {oly['olympic_year']}")
    
    def identify_international_swimmers(self):
        """Identify international/foreign swimmers"""
        
        # Countries that indicate international status
        international_countries = [
            'Canada', 'Great Britain', 'England', 'Scotland', 'Wales', 'Ireland',
            'Australia', 'New Zealand', 'South Africa', 'Israel', 'Tunisia',
            'Kenya', 'Nigeria', 'Ghana', 'Germany', 'France', 'Spain', 'Italy',
            'Netherlands', 'Belgium', 'Sweden', 'Norway', 'Denmark', 'Finland',
            'Brazil', 'Argentina', 'Chile', 'Mexico', 'Venezuela', 'Colombia',
            'Japan', 'China', 'Korea', 'Singapore', 'Philippines', 'India'
        ]
        
        for swimmer in self.roster_data:
            hometown = swimmer.get('hometown', '')
            country = swimmer.get('country', '')
            
            # Check if from international location
            if any(c in hometown or c in country for c in international_countries):
                self.international_swimmers.append({
                    'name': swimmer['name'],
                    'country': country or self.extract_country(hometown),
                    'hometown': hometown,
                    'events': swimmer.get('events'),
                    'height': swimmer.get('height'),
                    'class': swimmer.get('class')
                })
        
        if self.international_swimmers:
            print(f"\n🌍 INTERNATIONAL SWIMMERS: {len(self.international_swimmers)}")
            for intl in self.international_swimmers[:5]:  # Show first 5
                print(f"   • {intl['name']} - {intl['country']}")
    
    def identify_tall_swimmers(self):
        """Identify swimmers 6'3" or taller (potential training partners)"""
        
        for swimmer in self.roster_data:
            height_str = swimmer.get('height', '')
            
            # Parse height (e.g., "6' 4\"" or "6-4")
            height_match = re.search(r"6['\-\s]*([3-9])", height_str)
            
            if height_match:
                inches = int(height_match.group(1))
                
                # 6'3" or taller
                if inches >= 3:
                    self.tall_swimmers.append({
                        'name': swimmer['name'],
                        'height': height_str,
                        'events': swimmer.get('events'),
                        'country': swimmer.get('country'),
                        'class': swimmer.get('class')
                    })
        
        if self.tall_swimmers:
            print(f"\n📏 TALL SWIMMERS (6'3\"+): {len(self.tall_swimmers)}")
            for tall in self.tall_swimmers[:5]:
                print(f"   • {tall['name']} - {tall['height']}")
    
    def calculate_fit_score(self) -> int:
        """Calculate recruiting fit score based on special attributes"""
        
        score = 50  # Base score
        
        # Olympic swimmers = HUGE boost
        score += len(self.olympic_swimmers) * 25
        
        # Medal-winning Olympic swimmers = MASSIVE boost
        for oly in self.olympic_swimmers:
            if oly['medal'] in ['gold', 'silver', 'bronze']:
                score += 15
        
        # International diversity = moderate boost
        score += min(len(self.international_swimmers) * 2, 20)
        
        # Tall swimmers (similar to Michael) = moderate boost
        score += min(len(self.tall_swimmers) * 3, 15)
        
        # Current year success (if in top 10 NCAAs) = boost
        if self.school.get('ncaa_ranking', 100) <= 10:
            score += 10
        
        return min(score, 100)  # Cap at 100
    
    def assess_priority_change(self) -> str:
        """Assess if school priority should change based on findings"""
        
        reasons = []
        
        # Olympic swimmers change everything
        if len(self.olympic_swimmers) >= 2:
            reasons.append(f"🚨 {len(self.olympic_swimmers)} Olympic swimmers on team")
        
        # Height match is critical
        michael_height_matches = [
            s for s in self.tall_swimmers 
            if '6\' 4' in s['height'] or '6-4' in s['height']
        ]
        
        if len(michael_height_matches) >= 2:
            reasons.append(f"📏 {len(michael_height_matches)} swimmers are 6'4\" (Michael's height)")
        
        # International culture matters
        if len(self.international_swimmers) >= 10:
            reasons.append(f"🌍 Strong international presence ({len(self.international_swimmers)} swimmers)")
        
        if reasons:
            return "⬆️ PRIORITY INCREASE - " + "; ".join(reasons)
        else:
            return "➡️ No priority change"
    
    def generate_analysis_report(self) -> Dict:
        """Generate detailed analysis report"""
        
        return {
            'timestamp': datetime.now().isoformat(),
            'school_name': self.school['name'],
            'olympic_swimmers': self.olympic_swimmers,
            'international_swimmers': self.international_swimmers,
            'tall_swimmers': self.tall_swimmers,
            'fit_score': self.calculate_fit_score(),
            'priority_assessment': self.assess_priority_change(),
            'training_partners': self.identify_training_partners(),
            'competitive_advantages': self.list_competitive_advantages()
        }
    
    def identify_training_partners(self) -> List[Dict]:
        """Identify ideal training partners for Michael"""
        
        partners = []
        
        # Sprinters who are 6'3"+ and/or Olympic-level
        for swimmer in self.roster_data:
            events = swimmer.get('events', '').lower()
            
            # Sprint events
            is_sprinter = any(e in events for e in ['free', 'fly', 'back'])
            is_tall = any(s['name'] == swimmer['name'] for s in self.tall_swimmers)
            is_olympic = any(s['name'] == swimmer['name'] for s in self.olympic_swimmers)
            
            if (is_sprinter and is_tall) or is_olympic:
                partners.append({
                    'name': swimmer['name'],
                    'height': swimmer.get('height'),
                    'events': swimmer.get('events'),
                    'attributes': [
                        '🏊 Sprint events' if is_sprinter else '',
                        '📏 Tall (6\'3\"+)' if is_tall else '',
                        '🥇 Olympic-level' if is_olympic else ''
                    ]
                })
        
        return partners
    
    def list_competitive_advantages(self) -> List[str]:
        """List competitive advantages for recruiting"""
        
        advantages = []
        
        if self.olympic_swimmers:
            advantages.append(
                f"Train with {len(self.olympic_swimmers)} Olympic swimmer(s): " +
                ", ".join([s['name'] for s in self.olympic_swimmers[:3]])
            )
        
        if len(self.tall_swimmers) >= 3:
            advantages.append(
                f"Multiple tall training partners ({len(self.tall_swimmers)} swimmers 6'3\"+)"
            )
        
        if len(self.international_swimmers) >= 8:
            advantages.append(
                f"International team culture ({len(self.international_swimmers)} countries represented)"
            )
        
        return advantages
    
    @staticmethod
    def extract_olympic_medal(bio: str) -> str:
        """Extract Olympic medal type from bio"""
        bio_lower = bio.lower()
        
        if 'gold medal' in bio_lower or 'olympic champion' in bio_lower:
            return 'Gold'
        elif 'silver medal' in bio_lower:
            return 'Silver'
        elif 'bronze medal' in bio_lower:
            return 'Bronze'
        elif 'olympic' in bio_lower:
            return 'Participant'
        
        return 'Unknown'
    
    @staticmethod
    def extract_olympic_year(bio: str) -> str:
        """Extract Olympic year from bio"""
        years = ['2024', '2020', '2016', '2012', '2008']
        
        for year in years:
            if year in bio:
                return year
        
        return 'Unknown'
    
    @staticmethod
    def extract_country(hometown: str) -> str:
        """Extract country from hometown string"""
        # Simple parsing - last part after comma usually country
        parts = hometown.split(',')
        return parts[-1].strip() if len(parts) > 1 else 'USA'


def analyze_all_schools(schools_config: List[Dict]) -> List[Dict]:
    """Analyze all schools and rank by fit"""
    
    results = []
    
    for school_config in schools_config:
        analyzer = D1RecruitingAnalyzer(school_config)
        result = analyzer.analyze_school()
        results.append(result)
    
    # Sort by fit score (descending)
    results.sort(key=lambda x: x['fit_score'], reverse=True)
    
    return results


def generate_school_report_package(school_result: Dict) -> Dict:
    """Generate 3-document package for a school"""
    
    return {
        'school': school_result['school'],
        'documents': {
            'comprehensive_report': f"{school_result['school']}_Complete_Report.docx",
            'current_superstars': f"{school_result['school']}_Current_Superstars.txt",
            'physical_profile': f"{school_result['school']}_Physical_Match.txt"
        },
        'priority': school_result.get('priority_change', 'No change'),
        'fit_score': school_result['fit_score']
    }


if __name__ == "__main__":
    print("D1 Swimming Recruiting Analyzer")
    print("="*80)
    print("\nThis workflow:")
    print("1. Fetches roster from school website")
    print("2. Identifies Olympic/international/tall swimmers")
    print("3. Calculates recruiting fit score")
    print("4. Generates 3-document package")
    print("5. Re-ranks schools based on findings")
    print("\n" + "="*80)

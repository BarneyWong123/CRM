"""CRM Analysis logic for MY-Clinical sheet."""
import pandas as pd
import random
from typing import Dict, List, Any
from datetime import datetime
from config import Config
from opportunity_tracker import OpportunityTracker

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class CRMAnalyzer:
    """Analyzer for CRM data specializing in the MY-Clinical sheet."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with the MY-Clinical dataframe.
        Expected columns based on inspection:
        0: Account
        4: Brand
        12: Product
        17: Total Value
        18: Owner
        19: Status (Open, Won, Lost)
        20: Notes
        """
        # Rename columns for easier access based on identified indices
        self.df = df.copy()

        # Validate that we have enough columns (index 21 is accessed later)
        if len(self.df.columns) < 22:
            raise ValueError(f"CRM Dataframe requires at least 22 columns, found {len(self.df.columns)}")
        
        # We need to find the actual header row if row 0 is just garbage
        # In our inspection, row 0 of the DATA (from Header Row 2) had the mappings
        # Account is first col
        self.df.columns = [f"col_{i}" for i in range(len(self.df.columns))]
        
        self.cols = {
            'account': 'col_0',
            'brand': 'col_11', # Corrected from col_4 (which was Existing Brand)
            'product': 'col_12',
            'value': 'col_17',
            'owner': 'col_18',
            'status': 'col_19',
            'note': 'col_20'
        }
        
        # Clean owner names and filter
        self.df = self.df[self.df[self.cols['owner']].isin(Config.TARGET_OWNERS)]
        
        # Convert value to numeric, handling NaN and strings
        self.df[self.cols['value']] = pd.to_numeric(self.df[self.cols['value']], errors='coerce').fillna(0)
        
    def generate_report(self) -> str:
        """Generate the full formatted HTML CRM summary report."""
        now = datetime.now().strftime("%B %d, %Y")
        
        # Track and compare opportunities
        tracker = OpportunityTracker()
        new_opps, updated_opps = tracker.compare_and_update(self.df, self.cols)
        changes_html = tracker.generate_changes_html(new_opps, updated_opps)
        
        # Get AI insights
        ai_insights = self._get_ai_insights()
        
        html = f"""
        <html>
        <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1a1a1a; line-height: 1.6; background-color: #f9fafb; margin: 0; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 12px; border: 1px solid #e5e7eb; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            h1 {{ color: #1f2937; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; font-size: 24px; }}
            h2 {{ color: #2563eb; font-size: 18px; margin-top: 30px; text-transform: uppercase; letter-spacing: 0.05em; border-left: 4px solid #2563eb; padding-left: 12px; }}
            h3 {{ color: #4b5563; font-size: 16px; margin-bottom: 10px; }}
            .metric-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 20px 0; }}
            .metric-card {{ background: #f3f4f6; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6; }}
            .metric-label {{ font-size: 12px; color: #6b7280; text-transform: uppercase; }}
            .metric-value {{ font-size: 20px; font-weight: bold; color: #111827; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 13px; }}
            th {{ background: #f9fafb; color: #4b5563; text-align: left; padding: 12px; border-bottom: 2px solid #e5e7eb; }}
            td {{ padding: 12px; border-bottom: 1px solid #f3f4f6; vertical-align: top; }}
            tr:hover {{ background-color: #f9fafb; }}
            .status-tag {{ padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; }}
            .won {{ background: #dcfce7; color: #166534; }}
            .lost {{ background: #fee2e2; color: #991b1b; }}
            .progress {{ background: #dbeafe; color: #1e40af; }}
            .price {{ font-family: 'Courier New', Courier, monospace; font-weight: bold; color: #059669; }}
            .ai-box {{ background: #eff6ff; border: 1px solid #bfdbfe; padding: 20px; border-radius: 8px; margin-top: 20px; }}
            .ai-title {{ color: #1e40af; font-weight: bold; margin-bottom: 10px; display: flex; align-items: center; }}
            .footer {{ margin-top: 40px; font-size: 12px; color: #9ca3af; text-align: center; border-top: 1px solid #e5e7eb; padding-top: 20px; }}
        </style>
        </head>
        <body>
            <div class="container">
                <h1>CRM Summary: {now}</h1>
                
                {self._section1_top_picks()}
                {self._generate_charts_section()}
                {self._section4_top_brands()}
                {self._section5_high_value_deals()}
                
                <div class="ai-box">
                    <div class="ai-title">🤖 AI Strategic Insights (GPT-4o mini)</div>
                    <div style="font-size: 14px; color: #1e3a8a;">
                        {ai_insights}
                    </div>
                </div>
                
                {changes_html}
                
                <div class="footer">
                    Automated CRM Analysis &bull; MY-Clinical Sheet &bull; Biomed Global
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def _get_ai_insights(self) -> str:
        """Fetch AI-generated strategic insights based on the current data."""
        if OpenAI is None:
             return "<p style='color: #ef4444;'>AI Analysis unavailable: openai package not installed.</p>"

        try:
            client = OpenAI(api_key=Config.OPENAI_API_KEY)
            
            # Prepare granular summary data for the AI
            total_value = self.df[self.cols['value']].sum()
            owner_stats = ""
            for owner in Config.TARGET_OWNERS:
                owner_df = self.df[self.df[self.cols['owner']] == owner]
                owner_stats += f"- {owner}: RM {owner_df[self.cols['value']].sum():,.2f} total, {len(owner_df[owner_df[self.cols['status']] == 'Open'])} open deals.\n"
            
            # Extract top 5 open deals for granular commentary
            open_deals = self.df[self.df[self.cols['status']] == 'Open'].sort_values(self.cols['value'], ascending=False).head(5)
            deal_details = ""
            for _, row in open_deals.iterrows():
                deal_details += f"- Account: {row[self.cols['account']]}, Brand: {row[self.cols['brand']]}, Value: RM {row[self.cols['value']]:,.2f}, Product: {row[self.cols['product']]}, Note: {str(row[self.cols['note']])[:100]}\n"

            top_brands = self.df[self.cols['brand']].value_counts().head(3).to_dict()
            
            prompt = f"""
            As a sales strategy assistant, provide:
            1. THREE high-impact strategic insights based on the general pipeline performance.
            2. BRIEF strategic commentary on at least TWO of the specific individual opportunities listed below.
            
            CRM Data Summary:
            - Total Pipeline Value: RM {total_value:,.2f}
            {owner_stats}
            - Current Top 3 Brands: {top_brands}
            
            Individual Opportunities for Commentary:
            {deal_details}
            
            Keep the response professional, action-oriented, and formatted as an HTML bulleted list (<ul> and <li>).
            Comment on the specific accounts by name. 
            Do not include any other text before or after the list.
            """
            
            response = client.chat.completions.create(
                model=Config.AI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional sales analyst providing concise executive insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"<p style='color: #ef4444;'>AI Analysis currently unavailable: {str(e)}</p>"

    def _section1_top_picks(self) -> str:
        """Section 1: TOP 3 OPPORTUNITY PICKS OF THE DAY."""
        open_deals = self.df[self.df[self.cols['status']] == 'Open']
        if open_deals.empty: return ""
        
        picks = open_deals.sample(min(3, len(open_deals)))
        
        rows_html = ""
        for _, row in picks.iterrows():
            rows_html += f"""
            <tr>
                <td><strong>{row[self.cols['account']]}</strong></td>
                <td>{row[self.cols['owner']]}</td>
                <td class="price">RM {row[self.cols['value']]:,.2f}</td>
                <td>{row[self.cols['brand']]}</td>
                <td>{row[self.cols['product']]}</td>
                <td style="color: #6b7280; font-style: italic;">{str(row[self.cols['note']])[:150]}...</td>
            </tr>
            """
            
        return f"""
        <h2>⭐ Top 3 Opportunity Picks</h2>
        <table>
            <thead>
                <tr>
                    <th>Account</th>
                    <th>Owner</th>
                    <th>Value</th>
                    <th>Brand</th>
                    <th>Product</th>
                    <th>Note</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        """

    def _section2_executive_overview(self) -> str:
        """Section 2: EXECUTIVE OVERVIEW."""
        total_deals = len(self.df)
        total_value = self.df[self.cols['value']].sum()
        open_pipeline = len(self.df[self.df[self.cols['status']] == 'Open'])
        
        won = len(self.df[self.df[self.cols['status']] == 'Won'])
        lost = len(self.df[self.df[self.cols['status']] == 'Lost'])
        ratio = (won / (won + lost) * 100) if (won + lost) > 0 else 0
        
        return f"""
        <h2>📊 Executive Overview</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Combined Total Deals</div>
                <div class="metric-value">{total_deals}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Pipeline Value</div>
                <div class="metric-value">RM {total_value:,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Open Pipeline</div>
                <div class="metric-value">{open_pipeline}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Win/Loss Ratio</div>
                <div class="metric-value">{ratio:.1f}%</div>
            </div>
        </div>
        """

    def _section3_performance(self) -> str:
        """Section 3: SIDE-BY-SIDE PERFORMANCE."""
        comparison_html = ""
        for owner in Config.TARGET_OWNERS:
            owner_df = self.df[self.df[self.cols['owner']] == owner]
            comparison_html += f"""
            <div class="metric-card" style="margin-bottom: 10px;">
                <h3 style="margin: 0;">{owner}</h3>
                <div style="display: flex; justify-content: space-between; font-size: 13px; margin-top: 10px;">
                    <span>Deals: <strong>{len(owner_df)}</strong></span>
                    <span>Value: <strong class="price">RM {owner_df[self.cols['value']].sum():,.2f}</strong></span>
                    <span>Open: <strong>{len(owner_df[owner_df[self.cols['status']] == 'Open'])}</strong></span>
                    <span>Won/Lost: <span class="won">{len(owner_df[owner_df[self.cols['status']] == 'Won'])}</span> / <span class="lost">{len(owner_df[owner_df[self.cols['status']] == 'Lost'])}</span></span>
                </div>
            </div>
            """
            
        return f"<h2>⚔️ Side-by-Side Performance</h2>{comparison_html}"

    def _section4_top_brands(self) -> str:
        """Section 4: TOP BRANDS BY OWNER."""
        brands_html = "<div style='display: flex; gap: 20px;'>"
        for owner in Config.TARGET_OWNERS:
            owner_df = self.df[self.df[self.cols['owner']] == owner]
            top_brands = owner_df[self.cols['brand']].value_counts().head(5)
            
            list_items = "".join([f"<li>{brand}: <strong>{count}</strong></li>" for brand, count in top_brands.items()])
            brands_html += f"""
            <div style="flex: 1; background: #f9fafb; padding: 15px; border-radius: 8px;">
                <h3 style="margin-top: 0; font-size: 14px;">{owner}</h3>
                <ul style="padding-left: 20px; margin: 0; font-size: 13px;">{list_items}</ul>
            </div>
            """
        brands_html += "</div>"
        return f"<h2>🏷️ Top Brands</h2>{brands_html}"

    def _section5_high_value_deals(self) -> str:
        """Section 5: HIGH-VALUE OPEN DEALS (>RM 500K)."""
        high_val = self.df[(self.df[self.cols['status']] == 'Open') & (self.df[self.cols['value']] > 500000)]
        if high_val.empty: return ""
        
        rows = ""
        for _, row in high_val.iterrows():
            rows += f"<tr><td>{row[self.cols['account']]}</td><td>{row[self.cols['owner']]}</td><td class='price'>RM {row[self.cols['value']]:,.2f}</td><td>{row[self.cols['brand']]}</td><td>{row[self.cols['product']]}</td><td>{str(row[self.cols['note']])[:100]}...</td></tr>"
            
        return f"<h2>🔥 High-Value Action Items (>500K)</h2><table><thead><tr><th>Account</th><th>Owner</th><th>Value</th><th>Brand</th><th>Product</th><th>Note</th></tr></thead><tbody>{rows}</tbody></table>"

    def _section6_recent_won_deals(self) -> str:
        """Section 6: RECENT WON DEALS."""
        won_deals = self.df[self.df[self.cols['status']] == 'Won']
        if won_deals.empty: return ""
        
        rows = ""
        for _, row in won_deals.iterrows():
            rows += f"<tr><td>{row[self.cols['account']]}</td><td>{row[self.cols['owner']]}</td><td>{row[self.cols['brand']]}</td><td>{row[self.cols['product']]}</td><td class='price'>RM {row[self.cols['value']]:,.2f}</td></tr>"
            
        return f"<h2>🏆 Recent Won Deals</h2><table><thead><tr><th>Account</th><th>Owner</th><th>Brand</th><th>Product</th><th>Value</th></tr></thead><tbody>{rows}</tbody></table>"

    def _section7_lost_deals(self) -> str:
        """Section 7: LOST DEALS."""
        lost_deals = self.df[self.df[self.cols['status']] == 'Lost']
        if lost_deals.empty: return ""
        
        rows = ""
        for _, row in lost_deals.iterrows():
            comp = str(row.get('col_21', 'Unknown'))
            rows += f"<tr><td>{row[self.cols['account']]}</td><td>{row[self.cols['owner']]}</td><td class='price'>RM {row[self.cols['value']]:,.2f}</td><td>{comp}</td></tr>"
            
        return f"<h2>⚠️ Lost Deals</h2><table><thead><tr><th>Account</th><th>Owner</th><th>Value</th><th>Competitor</th></tr></thead><tbody>{rows}</tbody></table>"

    def _generate_charts_section(self) -> str:
        """Generate HTML/CSS bar chart for email compatibility."""
        try:
            # Group by Brand and Owner, get top 5 brands by total value
            pivot_data = self.df.pivot_table(
                values=self.cols['value'],
                index=self.cols['brand'],
                columns=self.cols['owner'],
                aggfunc='sum',
                fill_value=0
            )
            
            # Get top 5 brands by total value
            brand_totals = pivot_data.sum(axis=1).sort_values(ascending=False)
            top_brands = brand_totals.head(5).index.tolist()
            pivot_data = pivot_data.loc[top_brands]
            
            # Get max value for scaling
            max_value = pivot_data.values.max() if pivot_data.values.max() > 0 else 1
            
            owners = pivot_data.columns.tolist()
            colors = {'Arora Johney': '#3b82f6', 'Jiun Hao (Barney) Wong': '#10b981'}
            
            # Build HTML bars
            bars_html = ""
            for brand in top_brands:
                bars_html += f'<div style="margin-bottom: 20px;">'
                bars_html += f'<div style="font-weight: bold; margin-bottom: 8px; color: #374151;">{brand}</div>'
                
                for owner in owners:
                    value = pivot_data.loc[brand, owner]
                    if value > 0:
                        width_pct = min((value / max_value) * 100, 100)
                        color = colors.get(owner, '#6b7280')
                        owner_short = owner.split()[0]  # First name only
                        
                        # Format value
                        if value >= 1000000:
                            value_str = f"RM {value/1000000:.1f}M"
                        else:
                            value_str = f"RM {value/1000:.0f}K"
                        
                        bars_html += f'''
                        <div style="display: flex; align-items: center; margin-bottom: 4px;">
                            <div style="width: 60px; font-size: 11px; color: #6b7280;">{owner_short}</div>
                            <div style="flex: 1; background: #e5e7eb; border-radius: 4px; height: 20px; margin-right: 10px;">
                                <div style="width: {width_pct}%; background: {color}; height: 100%; border-radius: 4px;"></div>
                            </div>
                            <div style="width: 80px; font-size: 12px; font-weight: bold; color: #059669; text-align: right;">{value_str}</div>
                        </div>
                        '''
                
                bars_html += '</div>'
            
            # Legend
            legend_html = '<div style="display: flex; gap: 20px; justify-content: center; margin-top: 15px; font-size: 12px;">'
            for owner in owners:
                color = colors.get(owner, '#6b7280')
                legend_html += f'<div><span style="display: inline-block; width: 12px; height: 12px; background: {color}; border-radius: 2px; margin-right: 5px;"></span>{owner}</div>'
            legend_html += '</div>'

            return f"""
            <h2>📈 Top 5 Brands by Pipeline Value</h2>
            <div style="background: #f9fafb; padding: 20px; border-radius: 8px;">
                {bars_html}
                {legend_html}
            </div>
            """
        except Exception as e:
            print(f"Chart generation error: {e}")
            return f"<p style='color: #ef4444;'>Visual analytics unavailable: {e}</p>"


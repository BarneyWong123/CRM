"""CRM Analysis logic for MY-Clinical sheet."""
import pandas as pd
import random
from typing import Dict, List, Any
from datetime import datetime
from config import Config

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
                {self._section4_top_brands()}
                {self._section5_high_value_deals()}
                {self._section6_recent_won_deals()}
                {self._section7_lost_deals()}
                
                <div class="ai-box">
                    <div class="ai-title">🤖 AI Strategic Insights (GPT-4o mini)</div>
                    <div style="font-size: 14px; color: #1e3a8a;">
                        {ai_insights}
                    </div>
                </div>
                
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
        try:
            from openai import OpenAI
            client = OpenAI(api_key=Config.OPENAI_API_KEY)
            
            # Prepare summary data for the AI
            total_value = self.df[self.cols['value']].sum()
            owner_stats = ""
            for owner in Config.TARGET_OWNERS:
                owner_df = self.df[self.df[self.cols['owner']] == owner]
                owner_stats += f"- {owner}: RM {owner_df[self.cols['value']].sum():,.2f} total, {len(owner_df[owner_df[self.cols['status']] == 'Open'])} open deals.\n"
            
            high_val_count = len(self.df[(self.df[self.cols['status']] == 'Open') & (self.df[self.cols['value']] > 500000)])
            top_brands = self.df[self.cols['brand']].value_counts().head(3).to_dict()
            
            prompt = f"""
            As a sales strategy assistant, provide 3 brief, high-impact strategic insights based on this CRM data:
            - Total Pipeline Value: RM {total_value:,.2f}
            - Owner Performance:
            {owner_stats}
            - High-Value Deals (>500k) pending: {high_val_count}
            - Current Top 3 Brands being pitched: {top_brands}
            
            Analyze the distribution and value. Keep each point professional, concise, and action-oriented.
            Return the output as an HTML bulleted list (<ul> and <li>).
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

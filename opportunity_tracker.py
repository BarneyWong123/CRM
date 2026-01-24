"""Simple opportunity change tracker - compares current CRM with previous version."""
import os
import json
import pandas as pd
from typing import Dict, List, Tuple
from config import Config

SNAPSHOT_FILE = 'previous_crm_data.json'


class OpportunityTracker:
    """Tracks changes between current and previous CRM data."""
    
    def __init__(self):
        self.snapshot_path = SNAPSHOT_FILE
        self.previous_data: Dict[str, Dict] = {}
        self._load_previous()
    
    def _load_previous(self):
        """Load previous CRM data from disk."""
        if os.path.exists(self.snapshot_path):
            try:
                with open(self.snapshot_path, 'r') as f:
                    self.previous_data = json.load(f)
                print(f"✓ Loaded previous data with {len(self.previous_data)} opportunities")
            except Exception as e:
                print(f"⚠ Could not load previous data: {e}")
                self.previous_data = {}
        else:
            print("ℹ No previous CRM data - this will be the baseline")
            self.previous_data = {}
    
    def _save_current(self, data: Dict[str, Dict]):
        """Save current data for next comparison."""
        try:
            with open(self.snapshot_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"✓ Saved current data ({len(data)} opportunities) for next comparison")
        except Exception as e:
            print(f"❌ Error saving data: {e}")
    
    def _create_key(self, row: Dict) -> str:
        """Create unique key for an opportunity (Account + Brand + Product)."""
        account = str(row.get('account', '')).strip()
        brand = str(row.get('brand', '')).strip()
        product = str(row.get('product', '')).strip()
        return f"{account}|{brand}|{product}"
    
    def _row_to_dict(self, row: pd.Series, cols: Dict) -> Dict:
        """Convert DataFrame row to dictionary."""
        return {
            'account': str(row[cols['account']]),
            'brand': str(row[cols['brand']]),
            'product': str(row[cols['product']]),
            'value': float(row[cols['value']]) if pd.notna(row[cols['value']]) else 0,
            'owner': str(row[cols['owner']]),
            'status': str(row[cols['status']]),
            'note': str(row[cols['note']]) if pd.notna(row[cols['note']]) else ''
        }
    
    def compare_and_update(self, df: pd.DataFrame, cols: Dict) -> Tuple[List[Dict], List[Dict]]:
        """
        Compare current data with previous.
        
        Returns:
            Tuple of (new_opportunities, note_changes)
            Returns empty lists if no previous data exists (first run = baseline only)
        """
        new_opportunities = []
        note_changes = []
        current_data = {}
        
        # Check if we have previous data to compare against
        has_previous = len(self.previous_data) > 0
        
        # Process current data
        for _, row in df.iterrows():
            row_dict = self._row_to_dict(row, cols)
            key = self._create_key(row_dict)
            current_data[key] = row_dict
            
            # Only detect changes if we have previous data to compare
            if has_previous:
                if key not in self.previous_data:
                    # Completely new opportunity
                    new_opportunities.append(row_dict)
                else:
                    # Check if progress note changed
                    prev_note = self.previous_data[key].get('note', '')
                    curr_note = row_dict['note']
                    
                    if prev_note != curr_note and len(curr_note) > 0:
                        note_changes.append({
                            **row_dict,
                            'previous_note': prev_note[:200] if prev_note else '(empty)',
                            'new_note': curr_note[:200]
                        })
        
        # Save current data for next comparison
        self._save_current(current_data)
        
        if not has_previous:
            print("ℹ First run - baseline created. Changes will be shown on next run.")
        
        return new_opportunities, note_changes
    
    def generate_changes_html(self, new_opps: List[Dict], note_changes: List[Dict]) -> str:
        """Generate HTML section for new opportunities and note changes."""
        if not new_opps and not note_changes:
            return ""
        
        html = ""
        
        # New Opportunities Section
        if new_opps:
            rows = ""
            for opp in new_opps[:10]:
                rows += f"""
                <tr>
                    <td><strong>{opp['account']}</strong></td>
                    <td>{opp['owner']}</td>
                    <td class="price">RM {opp['value']:,.2f}</td>
                    <td>{opp['brand']}</td>
                    <td>{opp['product']}</td>
                </tr>
                """
            
            html += f"""
            <h2>🆕 New Opportunities Added ({len(new_opps)})</h2>
            <table>
                <thead>
                    <tr>
                        <th>Account</th>
                        <th>Owner</th>
                        <th>Value</th>
                        <th>Brand</th>
                        <th>Product</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
            """
        
        # Progress Note Changes Section
        if note_changes:
            rows = ""
            for opp in note_changes[:10]:
                rows += f"""
                <tr>
                    <td><strong>{opp['account']}</strong></td>
                    <td>{opp['owner']}</td>
                    <td>{opp['brand']}</td>
                    <td style="font-size: 12px; color: #6b7280;">{opp['new_note'][:150]}...</td>
                </tr>
                """
            
            html += f"""
            <h2>🔄 Progress Note Updates ({len(note_changes)})</h2>
            <table>
                <thead>
                    <tr>
                        <th>Account</th>
                        <th>Owner</th>
                        <th>Brand</th>
                        <th>Latest Note</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
            """
        
        return html

import json
import os

class StateManager:
    """Manages local state to prevent duplicate processing of emails."""
    
    def __init__(self, filename='processed_messages.json'):
        self.filename = filename
        self.processed_ids = self._load_state()
    
    def _load_state(self):
        """Load processed message IDs from file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return set(json.load(f))
            except Exception as e:
                print(f"Error loading state file: {e}")
                return set()
        return set()
    
    def save_state(self):
        """Save processed message IDs to file."""
        try:
            with open(self.filename, 'w') as f:
                json.dump(list(self.processed_ids), f)
        except Exception as e:
            print(f"Error saving state file: {e}")
    
    def is_processed(self, message_id):
        """Check if a message ID has already been processed."""
        return message_id in self.processed_ids
    
    def mark_processed(self, message_id):
        """Mark a message ID as processed."""
        self.processed_ids.add(message_id)
        self.save_state()

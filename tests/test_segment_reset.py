import unittest
from unittest.mock import MagicMock, patch

# Mock streamlit before importing app modules
with patch('streamlit.session_state', {}), \
     patch('streamlit.chat_message'), \
     patch('streamlit.spinner'), \
     patch('streamlit.markdown'), \
     patch('streamlit.rerun'), \
     patch('streamlit.stop'), \
     patch('streamlit.columns'), \
     patch('streamlit.container'), \
     patch('streamlit.button'), \
     patch('streamlit.info'), \
     patch('streamlit.warning'), \
     patch('streamlit.chat_input'):
    from app.tabs import ai_advisor

class TestSegmentReset(unittest.TestCase):
    
    def setUp(self):
        # Reset session state mock for each test
        self.mock_state = {}
        self.patcher = patch('streamlit.session_state', self.mock_state)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    @patch('streamlit.columns')
    @patch('streamlit.container')
    def test_initialization(self, mock_container, mock_columns):
        # Setup mocks for UI calls
        mock_columns.return_value = [MagicMock(), MagicMock()]
        
        # Run render
        ai_advisor.render(MagicMock(), {}, [])
        
        # Assert initialization
        self.assertIn("ai_chat_history", self.mock_state)
        self.assertIn("last_segment", self.mock_state)
        self.assertIn("ai_chat_history_by_segment", self.mock_state)
        self.assertEqual(self.mock_state["ai_chat_history"], [])

    @patch('streamlit.columns')
    @patch('streamlit.container')
    def test_segment_change_resets_messages(self, mock_container, mock_columns):
        mock_columns.return_value = [MagicMock(), MagicMock()]
        
        # 1. Simulate state in "Individual" segment with some history
        self.mock_state["user_segment"] = "individual_selfbuild"
        self.mock_state["last_segment"] = "individual_selfbuild"
        self.mock_state["ai_chat_history"] = [{"role": "user", "content": "Hello"}]
        self.mock_state["ai_chat_history_by_segment"] = {}
        
        # 2. Change segment to "SMB"
        self.mock_state["user_segment"] = "smb_landlord"
        
        # 3. Run render
        ai_advisor.render(MagicMock(), {}, [])
        
        # 4. Assert messages reset
        self.assertEqual(self.mock_state["ai_chat_history"], [])
        self.assertEqual(self.mock_state["last_segment"], "smb_landlord")
        # Assert persistence logic ran for new segment
        self.assertEqual(self.mock_state["ai_chat_history_by_segment"]["smb_landlord"], [])

if __name__ == '__main__':
    unittest.main()
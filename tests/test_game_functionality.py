"""
Test suite for game functionality
"""
import time
import pytest
from tests.conftest import GamePage


class TestGameBasicFunctionality:
    """Test basic game functionality"""
    
    def test_game_page_loads(self, game_page):
        """Test that game page loads successfully"""
        assert game_page.is_element_present(*game_page.FLIP_CARD)
        assert game_page.is_element_present(*game_page.QUESTION_TEXT)
        assert game_page.get_question_text().strip() != ""
        
    def test_initial_game_state(self, game_page):
        """Test initial game state is correct"""
        # Check initial card number
        assert "1" in game_page.get_current_card_number()
        
        # Check initial score
        assert game_page.get_current_score() == 0
        
        # Check card is not flipped initially
        assert not game_page.is_card_flipped()
        
        # Check question elements are present
        assert game_page.get_question_text().strip() != ""
        assert game_page.get_category().strip() != ""
        assert game_page.get_difficulty().strip() != ""


class TestCardFlipping:
    """Test card flipping functionality"""
    
    def test_flip_card_basic(self, game_page):
        """Test basic card flipping"""
        # Get initial state
        initial_question = game_page.get_question_text()
        assert not game_page.is_card_flipped()
        
        # Flip card
        game_page.flip_card()
        
        # Verify card is flipped
        assert game_page.is_card_flipped()
        
        # Verify answer is visible
        answer_text = game_page.get_answer_text()
        assert answer_text.strip() != ""
        assert answer_text != initial_question
        
    def test_flip_card_shows_answer_buttons(self, game_page):
        """Test that flipping card shows answer buttons"""
        # Flip card
        game_page.flip_card()
        
        # Check answer buttons are present and clickable
        assert game_page.is_element_present(*game_page.CORRECT_BTN)
        assert game_page.is_element_present(*game_page.INCORRECT_BTN)
        
        # Verify buttons are clickable
        correct_btn = game_page.get_element(*game_page.CORRECT_BTN)
        incorrect_btn = game_page.get_element(*game_page.INCORRECT_BTN)
        
        assert correct_btn.is_enabled()
        assert incorrect_btn.is_enabled()
        
    def test_card_flip_animation(self, game_page):
        """Test that card flip animation works"""
        # Record initial state
        assert not game_page.is_card_flipped()
        
        # Flip card and check animation
        game_page.flip_card()
        
        # Give animation time to complete
        time.sleep(1.5)
        
        # Verify final state
        assert game_page.is_card_flipped()


class TestAnswering:
    """Test answer functionality"""
    
    def test_answer_correct(self, game_page):
        """Test answering correctly"""
        initial_score = game_page.get_current_score()
        
        # Flip card and answer correctly
        game_page.flip_card()
        game_page.answer_correct()
        
        # Wait for score update
        time.sleep(2)
        
        # Check score increased
        new_score = game_page.get_current_score()
        assert new_score == initial_score + 1
        
    def test_answer_incorrect(self, game_page):
        """Test answering incorrectly"""
        initial_score = game_page.get_current_score()
        
        # Flip card and answer incorrectly
        game_page.flip_card()
        game_page.answer_incorrect()
        
        # Wait for processing
        time.sleep(2)
        
        # Check score didn't increase
        new_score = game_page.get_current_score()
        assert new_score == initial_score
        
    def test_accuracy_calculation(self, game_page):
        """Test accuracy percentage calculation"""
        # Answer first question correctly
        game_page.flip_card()
        game_page.answer_correct()
        time.sleep(2)
        
        # Check accuracy is 100%
        accuracy = game_page.get_accuracy_percentage()
        assert accuracy == 100.0
        
        # Move to next card and answer incorrectly
        if game_page.is_element_present(*game_page.NEXT_BTN):
            game_page.next_card()
            time.sleep(1)
            game_page.flip_card()
            game_page.answer_incorrect()
            time.sleep(2)
            
            # Check accuracy is now 50%
            accuracy = game_page.get_accuracy_percentage()
            assert accuracy == 50.0


class TestNavigation:
    """Test card navigation functionality"""
    
    def test_next_card_navigation(self, game_page):
        """Test navigating to next card"""
        initial_card = game_page.get_current_card_number()
        initial_question = game_page.get_question_text()
        
        # Go to next card
        if game_page.is_element_present(*game_page.NEXT_BTN):
            game_page.next_card()
            time.sleep(1)
            
            # Verify we moved to next card
            new_card = game_page.get_current_card_number()
            new_question = game_page.get_question_text()
            
            assert new_card != initial_card
            assert new_question != initial_question
            
    def test_previous_card_navigation(self, game_page):
        """Test navigating to previous card"""
        # First go to next card
        if game_page.is_element_present(*game_page.NEXT_BTN):
            game_page.next_card()
            time.sleep(1)
            
            current_card = game_page.get_current_card_number()
            
            # Now go back
            if game_page.is_element_present(*game_page.PREV_BTN):
                game_page.previous_card()
                time.sleep(1)
                
                # Verify we moved back
                prev_card = game_page.get_current_card_number()
                assert prev_card != current_card
                
    def test_navigation_button_states(self, game_page):
        """Test navigation button enabled/disabled states"""
        # At first card, previous should be disabled
        current_card = game_page.get_current_card_number()
        if "1" in current_card:
            prev_btn = game_page.get_element(*game_page.PREV_BTN)
            assert not prev_btn.is_enabled()
            
        # Navigate to last card and check next button
        while game_page.is_element_present(*game_page.NEXT_BTN):
            next_btn = game_page.get_element(*game_page.NEXT_BTN)
            if not next_btn.is_enabled():
                break
            game_page.next_card()
            time.sleep(0.5)
            
        # At last card, next should be disabled
        next_btn = game_page.get_element(*game_page.NEXT_BTN)
        assert not next_btn.is_enabled()


class TestGameReset:
    """Test game reset functionality"""
    
    def test_reset_game(self, game_page):
        """Test resetting the game"""
        # Play a few cards and build up score
        for i in range(2):
            game_page.flip_card()
            game_page.answer_correct()
            time.sleep(1)
            
            if game_page.is_element_present(*game_page.NEXT_BTN):
                next_btn = game_page.get_element(*game_page.NEXT_BTN)
                if next_btn.is_enabled():
                    game_page.next_card()
                    time.sleep(1)
                    
        initial_score = game_page.get_current_score()
        assert initial_score > 0
        
        # Reset game
        game_page.reset_game()
        time.sleep(2)
        
        # Verify reset state
        assert game_page.get_current_score() == 0
        assert "1" in game_page.get_current_card_number()
        assert not game_page.is_card_flipped()


class TestKeyboardControls:
    """Test keyboard controls"""
    
    def test_spacebar_flips_card(self, game_page):
        """Test spacebar flips card"""
        assert not game_page.is_card_flipped()
        
        # Press spacebar
        game_page.driver.find_element("tag name", "body").send_keys(" ")
        time.sleep(1)
        
        # Should be flipped
        assert game_page.is_card_flipped()
        
    def test_arrow_key_navigation(self, game_page):
        """Test arrow key navigation"""
        initial_card = game_page.get_current_card_number()
        
        # Press right arrow
        body = game_page.driver.find_element("tag name", "body")
        body.send_keys("ArrowRight")
        time.sleep(1)
        
        # Should move to next card
        new_card = game_page.get_current_card_number()
        if game_page.is_element_present(*game_page.NEXT_BTN):
            next_btn = game_page.get_element(*game_page.NEXT_BTN)
            if next_btn.is_enabled():
                assert new_card != initial_card


class TestGameFlow:
    """Test complete game flow scenarios"""
    
    def test_complete_game_flow(self, game_page):
        """Test a complete game flow"""
        # Start with first card
        assert "1" in game_page.get_current_card_number()
        assert game_page.get_current_score() == 0
        
        # Play through several cards
        cards_played = 0
        max_cards = 3  # Limit to avoid long test
        
        while cards_played < max_cards:
            # Flip current card
            if not game_page.is_card_flipped():
                game_page.flip_card()
                
            # Answer randomly (but let's answer correctly for testing)
            game_page.answer_correct()
            time.sleep(1)
            
            cards_played += 1
            
            # Move to next card if available
            if game_page.is_element_present(*game_page.NEXT_BTN):
                next_btn = game_page.get_element(*game_page.NEXT_BTN)
                if next_btn.is_enabled():
                    game_page.next_card()
                    time.sleep(1)
                else:
                    break
            else:
                break
                
        # Verify final state
        final_score = game_page.get_current_score()
        assert final_score == cards_played
        assert game_page.get_accuracy_percentage() == 100.0
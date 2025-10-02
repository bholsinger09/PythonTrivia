"""
Test suite for home page functionality
"""
import pytest
from tests.conftest import HomePage


class TestHomePage:
    """Test cases for the home page"""

    def test_home_page_loads_successfully(self, home_page):
        """Test that home page loads without errors"""
        assert "Python Trivia" in home_page.get_hero_title()
        
    def test_hero_section_content(self, home_page):
        """Test hero section displays correct content"""
        title = home_page.get_hero_title()
        assert "Python Trivia" in title
        assert "🐍" in title  # Snake emoji should be present
        
    def test_feature_cards_present(self, home_page):
        """Test that feature cards are displayed"""
        feature_count = home_page.get_feature_cards_count()
        assert feature_count >= 4, "Should have at least 4 feature cards"
        
    def test_stats_section_visible(self, home_page):
        """Test that stats section is visible"""
        assert home_page.is_stats_section_visible(), "Stats section should be visible"
        
    def test_start_game_navigation(self, home_page):
        """Test navigation from home to game page"""
        game_page = home_page.click_start_game()
        
        # Verify we're on the game page
        current_url = game_page.driver.current_url
        assert "/game" in current_url, "Should navigate to game page"
        
        # Verify game elements are present
        assert game_page.is_element_present(*game_page.FLIP_CARD), "Flip card should be present"
        assert game_page.is_element_present(*game_page.FLIP_BTN), "Flip button should be present"
        
    def test_browse_categories_navigation(self, home_page):
        """Test navigation from home to categories page"""
        categories_page = home_page.click_browse_categories()
        
        # Verify we're on the categories page
        current_url = categories_page.driver.current_url
        assert "/categories" in current_url, "Should navigate to categories page"
        
        # Verify categories content
        assert "Categories" in categories_page.get_page_title()
        assert categories_page.get_category_count() > 0, "Should have category cards"


class TestNavigation:
    """Test cases for site navigation"""
    
    def test_navbar_links_present(self, driver):
        """Test that all navbar links are present and functional"""
        driver.get("http://localhost:5001/")
        
        # Check navigation links
        nav_links = [
            ("Home", "/"),
            ("Play Game", "/game"),
            ("Categories", "/categories"),
            ("Difficulty", "/difficulty")
        ]
        
        for link_text, expected_path in nav_links:
            # Find and click the link
            link = driver.find_element("link text", link_text)
            assert link.is_displayed(), f"{link_text} link should be visible"
            
            # Click and verify navigation
            link.click()
            current_url = driver.current_url
            assert expected_path in current_url, f"Should navigate to {expected_path}"
            
            # Go back to home for next test
            driver.get("http://localhost:5001/")
            
    def test_responsive_design_mobile(self, fresh_driver):
        """Test responsive design on mobile viewport"""
        # Set mobile viewport
        fresh_driver.set_window_size(375, 667)  # iPhone size
        
        home_page = HomePage(fresh_driver).load()
        
        # Test that page loads properly on mobile
        assert home_page.is_element_present(*home_page.HERO_TITLE)
        assert home_page.is_element_present(*home_page.START_GAME_BTN)
        
        # Test mobile navigation
        game_page = home_page.click_start_game()
        assert "/game" in game_page.driver.current_url


class TestPagePerformance:
    """Test cases for page performance and loading"""
    
    def test_page_load_time(self, driver):
        """Test that pages load within acceptable time"""
        import time
        
        start_time = time.time()
        driver.get("http://localhost:5001/")
        load_time = time.time() - start_time
        
        assert load_time < 5.0, f"Page should load in under 5 seconds, took {load_time:.2f}s"
        
    def test_assets_load_properly(self, home_page):
        """Test that CSS and JS assets load without errors"""
        # Check for console errors (basic check)
        logs = home_page.driver.get_log('browser')
        severe_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        # Allow for some minor warnings but not severe errors
        assert len(severe_errors) == 0, f"Found severe browser errors: {severe_errors}"
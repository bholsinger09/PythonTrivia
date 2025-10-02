"""
Selenium test configuration and base test class
"""
import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


class BaseTestConfig:
    """Base configuration for Selenium tests"""
    
    # Test configuration
    IMPLICIT_WAIT = 10
    EXPLICIT_WAIT = 15
    BASE_URL = "http://localhost:5001"
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    
    @classmethod
    def get_driver_options(cls):
        """Get Chrome driver options"""
        options = Options()
        
        # Always use headless mode for testing
        options.add_argument("--headless")
        
        # Additional options for stability
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        
        return options

    @classmethod
    def create_driver(cls):
        """Create and configure Chrome driver with fallback options"""
        options = cls.get_driver_options()
        
        try:
            # Try to create driver with webdriver-manager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"Failed to create Chrome driver with webdriver-manager: {e}")
            try:
                # Fallback to system Chrome
                driver = webdriver.Chrome(options=options)
            except Exception as e2:
                print(f"Failed to create Chrome driver with system Chrome: {e2}")
                pytest.skip("Chrome browser not available for testing")
        
        driver.implicitly_wait(cls.IMPLICIT_WAIT)
        return driver


class BasePage:
    """Base page object with common functionality"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, BaseTestConfig.EXPLICIT_WAIT)
    
    def get_element(self, by, value, timeout=None):
        """Get element with explicit wait"""
        wait_time = timeout or BaseTestConfig.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, wait_time)
        return wait.until(EC.presence_of_element_located((by, value)))
    
    def get_clickable_element(self, by, value, timeout=None):
        """Get clickable element with explicit wait"""
        wait_time = timeout or BaseTestConfig.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, wait_time)
        return wait.until(EC.element_to_be_clickable((by, value)))
    
    def wait_for_element_text(self, by, value, expected_text, timeout=None):
        """Wait for element to contain specific text"""
        wait_time = timeout or BaseTestConfig.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, wait_time)
        return wait.until(EC.text_to_be_present_in_element((by, value), expected_text))
    
    def wait_for_element_invisible(self, by, value, timeout=None):
        """Wait for element to become invisible"""
        wait_time = timeout or BaseTestConfig.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, wait_time)
        return wait.until(EC.invisibility_of_element_located((by, value)))
    
    def is_element_present(self, by, value):
        """Check if element is present without waiting"""
        try:
            self.driver.find_element(by, value)
            return True
        except NoSuchElementException:
            return False
    
    def scroll_to_element(self, element):
        """Scroll element into view"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)  # Small delay for scroll animation
    
    def take_screenshot(self, name):
        """Take screenshot for debugging"""
        timestamp = int(time.time())
        filename = f"screenshots/{name}_{timestamp}.png"
        os.makedirs("screenshots", exist_ok=True)
        self.driver.save_screenshot(filename)
        return filename


class HomePage(BasePage):
    """Page object for the home page"""
    
    # Locators
    HERO_TITLE = (By.CLASS_NAME, "hero-title")
    START_GAME_BTN = (By.ID, "start-game-btn")
    BROWSE_CATEGORIES_BTN = (By.XPATH, "//a[contains(text(), 'Browse Categories')]")
    FEATURE_CARDS = (By.CLASS_NAME, "feature-card")
    STATS_SECTION = (By.CLASS_NAME, "stats-section")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = f"{BaseTestConfig.BASE_URL}/"
    
    def load(self):
        """Load the home page"""
        self.driver.get(self.url)
        return self
    
    def get_hero_title(self):
        """Get hero title text"""
        return self.get_element(*self.HERO_TITLE).text
    
    def click_start_game(self):
        """Click start game button"""
        btn = self.get_clickable_element(*self.START_GAME_BTN)
        self.scroll_to_element(btn)
        btn.click()
        return GamePage(self.driver)
    
    def click_browse_categories(self):
        """Click browse categories button"""
        btn = self.get_clickable_element(*self.BROWSE_CATEGORIES_BTN)
        self.scroll_to_element(btn)
        btn.click()
        return CategoriesPage(self.driver)
    
    def get_feature_cards_count(self):
        """Get number of feature cards"""
        return len(self.driver.find_elements(*self.FEATURE_CARDS))
    
    def is_stats_section_visible(self):
        """Check if stats section is visible"""
        return self.is_element_present(*self.STATS_SECTION)


class GamePage(BasePage):
    """Page object for the game page"""
    
    # Locators
    FLIP_CARD = (By.ID, "flip-card")
    FLIP_BTN = (By.ID, "flip-btn")
    CORRECT_BTN = (By.ID, "correct-btn")
    INCORRECT_BTN = (By.ID, "incorrect-btn")
    NEXT_BTN = (By.ID, "next-btn")
    PREV_BTN = (By.ID, "prev-btn")
    RESET_BTN = (By.ID, "reset-game-btn")
    
    QUESTION_TEXT = (By.ID, "question-text")
    ANSWER_TEXT = (By.ID, "answer-text")
    CATEGORY_BADGE = (By.ID, "category-badge")
    DIFFICULTY_BADGE = (By.ID, "difficulty-badge")
    
    CURRENT_CARD = (By.ID, "current-card")
    CURRENT_SCORE = (By.ID, "current-score")
    ACCURACY_PERCENTAGE = (By.ID, "accuracy-percentage")
    PROGRESS_FILL = (By.ID, "progress-fill")
    
    LOADING_SPINNER = (By.ID, "loading-spinner")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = f"{BaseTestConfig.BASE_URL}/game"
    
    def load(self):
        """Load the game page"""
        self.driver.get(self.url)
        return self
    
    def get_question_text(self):
        """Get current question text"""
        return self.get_element(*self.QUESTION_TEXT).text
    
    def get_answer_text(self):
        """Get current answer text"""
        return self.get_element(*self.ANSWER_TEXT).text
    
    def get_category(self):
        """Get current question category"""
        return self.get_element(*self.CATEGORY_BADGE).text
    
    def get_difficulty(self):
        """Get current question difficulty"""
        return self.get_element(*self.DIFFICULTY_BADGE).text
    
    def flip_card(self):
        """Flip the current card"""
        btn = self.get_clickable_element(*self.FLIP_BTN)
        btn.click()
        # Wait for flip animation to complete
        time.sleep(1)
        return self
    
    def answer_correct(self):
        """Mark current answer as correct"""
        btn = self.get_clickable_element(*self.CORRECT_BTN)
        btn.click()
        return self
    
    def answer_incorrect(self):
        """Mark current answer as incorrect"""
        btn = self.get_clickable_element(*self.INCORRECT_BTN)
        btn.click()
        return self
    
    def next_card(self):
        """Go to next card"""
        btn = self.get_clickable_element(*self.NEXT_BTN)
        btn.click()
        return self
    
    def previous_card(self):
        """Go to previous card"""
        btn = self.get_clickable_element(*self.PREV_BTN)
        btn.click()
        return self
    
    def reset_game(self):
        """Reset the game"""
        btn = self.get_clickable_element(*self.RESET_BTN)
        btn.click()
        # Handle confirmation dialog
        alert = self.driver.switch_to.alert
        alert.accept()
        return self
    
    def get_current_card_number(self):
        """Get current card number"""
        return self.get_element(*self.CURRENT_CARD).text
    
    def get_current_score(self):
        """Get current score"""
        return int(self.get_element(*self.CURRENT_SCORE).text)
    
    def get_accuracy_percentage(self):
        """Get accuracy percentage"""
        text = self.get_element(*self.ACCURACY_PERCENTAGE).text
        return float(text.replace('%', ''))
    
    def is_card_flipped(self):
        """Check if card is currently flipped"""
        flip_card = self.get_element(*self.FLIP_CARD)
        return "flipped" in flip_card.get_attribute("class")
    
    def is_loading(self):
        """Check if loading spinner is visible"""
        try:
            spinner = self.driver.find_element(*self.LOADING_SPINNER)
            return spinner.is_displayed()
        except NoSuchElementException:
            return False
    
    def wait_for_loading_complete(self, timeout=10):
        """Wait for loading to complete"""
        try:
            self.wait_for_element_invisible(*self.LOADING_SPINNER, timeout)
        except TimeoutException:
            pass  # Loading might not appear for fast operations


class CategoriesPage(BasePage):
    """Page object for the categories page"""
    
    # Locators
    PAGE_TITLE = (By.CLASS_NAME, "page-title")
    CATEGORY_CARDS = (By.CLASS_NAME, "category-card")
    PLAY_ALL_BTN = (By.XPATH, "//a[contains(text(), 'Play All Categories')]")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = f"{BaseTestConfig.BASE_URL}/categories"
    
    def load(self):
        """Load the categories page"""
        self.driver.get(self.url)
        return self
    
    def get_page_title(self):
        """Get page title"""
        return self.get_element(*self.PAGE_TITLE).text
    
    def get_category_count(self):
        """Get number of category cards"""
        return len(self.driver.find_elements(*self.CATEGORY_CARDS))
    
    def click_play_all(self):
        """Click play all categories button"""
        btn = self.get_clickable_element(*self.PLAY_ALL_BTN)
        btn.click()
        return GamePage(self.driver)


# Pytest fixtures
@pytest.fixture(scope="session")
def driver():
    """Create driver instance for test session"""
    driver = BaseTestConfig.create_driver()
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def fresh_driver():
    """Create fresh driver instance for each test"""
    driver = BaseTestConfig.create_driver()
    yield driver
    driver.quit()


@pytest.fixture
def home_page(driver):
    """Get home page instance"""
    return HomePage(driver).load()


@pytest.fixture
def game_page(driver):
    """Get game page instance"""
    return GamePage(driver).load()


@pytest.fixture
def categories_page(driver):
    """Get categories page instance"""
    return CategoriesPage(driver).load()
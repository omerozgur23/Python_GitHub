from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
import pytest
from pathlib import Path
from datetime import date
from contants import globalContants

class Test_Sauce:

    def setup_method(self):
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service = self.service)
        self.driver.maximize_window()
        self.driver.get(globalContants.URL)
        self.folderPath = str(date.today())
        Path(self.folderPath).mkdir(exist_ok=True)

    def teardown_method(self):
        self.driver.quit()

    def waitForElementVisible(self,locator,timeout=5):
        WebDriverWait(self.driver,timeout).until(ec.visibility_of_element_located(locator))

    def getLoginPageElements(self):
        self.waitForElementVisible((By.ID, "user-name"))
        usernameInput = self.driver.find_element(By.ID, "user-name")

        self.waitForElementVisible((By.ID, "password"))
        passwordInput = self.driver.find_element(By.ID, "password")

        self.waitForElementVisible((By.ID, "login-button"))
        loginBtn = self.driver.find_element(By.ID, "login-button")
        return usernameInput, passwordInput, loginBtn

    @pytest.mark.parametrize("username,password", [("standard_user","secret_sauce"), ("visual_user","secret_sauce"), ("performance_glitch_user","secret_sauce")])
    def test_after_login_page(self,username,password):
        expectedUrl = "https://www.saucedemo.com/inventory.html"

        usernameInput, passwordInput, loginBtn = self.getLoginPageElements()
        usernameInput.send_keys(username)
        passwordInput.send_keys(password)
        loginBtn.click()

        WebDriverWait(self.driver, 5).until(ec.url_to_be(expectedUrl))
        currentUrl = self.driver.current_url
        self.driver.save_screenshot(f"{self.folderPath}/test-after-login-page-{username}-{password}.png")
        assert expectedUrl == currentUrl

    def test_empty_inputs(self):
        usernameInput, passwordInput, loginBtn = self.getLoginPageElements()
        loginBtn.click()

        self.waitForElementVisible((By.XPATH, "//*[@id='login_button_container']/div/form/div[3]/h3"))
        errorMessage = self.driver.find_element(By.XPATH, "//*[@id='login_button_container']/div/form/div[3]/h3")
        self.driver.save_screenshot(f"{self.folderPath}/test-empty-inputs.png")
        assert errorMessage.text == "Epic sadface: Username is required"

    @pytest.mark.parametrize("username", [("standard_user"), ("problem_user"), ("performance_glitch_user")])
    def test_empty_password(self,username):
        usernameInput, passwordInput, loginBtn = self.getLoginPageElements()
        usernameInput.send_keys(username)
        loginBtn.click()

        self.waitForElementVisible((By.XPATH, "//*[@id='login_button_container']/div/form/div[3]/h3"))
        errorMessage = self.driver.find_element(By.XPATH, "//*[@id='login_button_container']/div/form/div[3]/h3")
        self.driver.save_screenshot(f"{self.folderPath}/test-empty-password-{username}.png")
        assert errorMessage.text == "Epic sadface: Password is required"

    def test_locked_user(self):
        usernameInput, passwordInput, loginBtn = self.getLoginPageElements()
        actions = ActionChains(self.driver)
        actions.send_keys_to_element(usernameInput, "locked_out_user")
        actions.send_keys_to_element(passwordInput, "secret_sauce")
        actions.perform()
        loginBtn.click()

        self.waitForElementVisible((By.XPATH, "//*[@id='login_button_container']/div/form/div[3]/h3"))
        errorMessage = self.driver.find_element(By.XPATH, "//*[@id='login_button_container']/div/form/div[3]/h3")
        self.driver.save_screenshot(f"{self.folderPath}/test-locked-user-{usernameInput}-{passwordInput}.png")
        assert errorMessage.text == "Epic sadface: Sorry, this user has been locked out."

    @pytest.mark.parametrize("username", [("standard_user"), ("problem_user"), ("performance_glitch_user")])
    def test_show_x_button(self,username):
        usernameInput, passwordInput, loginBtn = self.getLoginPageElements()
        usernameInput.send_keys(username)
        loginBtn.click()

        try:
            self.waitForElementVisible((By.CLASS_NAME, "error_icon"))
            xIcon = self.driver.find_element(By.CLASS_NAME, "error_icon")

            self.waitForElementVisible((By.CLASS_NAME, "fa-times"))
            closeBtn = self.driver.find_element(By.CLASS_NAME, "fa-times")
            closeBtn.click()

            WebDriverWait(self.driver, 5).until(ec.invisibility_of_element(xIcon))
            with pytest.raises(Exception):
                self.driver.find_element(By.CLASS_NAME, "error_icon")
            result = True
        except Exception as e:
            print(f"Exception occurred: {e}")
            result = False
        
        self.driver.save_screenshot(f"{self.folderPath}/test-show-x-button-{username}.png")
        assert result

    def test_how_many_product_listed(self):
        usernameInput, passwordInput, loginBtn = self.getLoginPageElements()
        actions = ActionChains(self.driver)
        actions.send_keys_to_element(usernameInput, "standard_user")
        actions.send_keys_to_element(passwordInput, "secret_sauce")
        actions.perform()
        loginBtn.click()

        self.waitForElementVisible((By.CLASS_NAME, "inventory_item "))
        productElements = self.driver.find_elements(By.CLASS_NAME, "inventory_item")
        numberOfProduct = len(productElements)
        self.driver.save_screenshot(f"{self.folderPath}/test_how_many_product_listed.png")
        assert numberOfProduct == 6
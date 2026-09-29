
import os
import time
import subprocess
import sys
import urllib.request

import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "http://127.0.0.1:5055"


# Start Flask automatically before the test session.
@pytest.fixture(scope="session")
def flask_server():

    env = os.environ.copy()
    env["PORT"] = "5055"

    process = subprocess.Popen(
        [sys.executable, "app.py"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    try:
        # Wait until the application is available.
        for attempt in range(30):

            if process.poll() is not None:
                pytest.fail("Flask application exited unexpectedly.")

            try:
                with urllib.request.urlopen(
                    BASE_URL + "/login",
                    timeout=1
                ) as response:

                    if response.status == 200:
                        break

            except Exception:
                time.sleep(1)

        else:
            pytest.fail("Flask server did not start.")

        yield

    finally:
        process.terminate()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


# Create a fresh Chrome browser for each test.
@pytest.fixture
def driver(flask_server):

    options = webdriver.ChromeOptions()

    # Jenkins runs without a visible desktop.
    # Locally, SHOW_BROWSER=1 enables visible Chrome.
    if os.environ.get("SHOW_BROWSER") != "1":
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1365,900")

    browser = webdriver.Chrome(options=options)

    yield browser

    browser.quit()


# Helper function for logging in.
def perform_login(driver, username, password):

    driver.get(BASE_URL + "/login")

    driver.find_element(
        By.ID, "username"
    ).send_keys(username)

    driver.find_element(
        By.ID, "password"
    ).send_keys(password)

    driver.find_element(
        By.ID, "login-button"
    ).click()


# TEST 1: Login page loads.
def test_login_page_loads(driver):

    driver.get(BASE_URL + "/login")

    assert "Student Portal" in driver.title


# TEST 2: Valid login.
def test_valid_login(driver):

    perform_login(
        driver,
        "student",
        "student123"
    )

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.ID, "welcome-message")
        )
    )

    assert "Welcome, student!" in driver.page_source


# TEST 3: Invalid password.
def test_invalid_password(driver):

    perform_login(
        driver,
        "student",
        "wrongpassword"
    )

    error = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.ID, "error-message")
        )
    )

    assert "Invalid username or password" in error.text


# TEST 4: Invalid username.
def test_invalid_username(driver):

    perform_login(
        driver,
        "wronguser",
        "student123"
    )

    error = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.ID, "error-message")
        )
    )

    assert "Invalid username or password" in error.text


# TEST 5: Empty credentials.
def test_empty_credentials(driver):

    perform_login(driver, "", "")

    error = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.ID, "error-message")
        )
    )

    assert "Invalid username or password" in error.text


# TEST 6: Logout functionality.
def test_logout(driver):

    perform_login(
        driver,
        "student",
        "student123"
    )

    logout = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.ID, "logout-button")
        )
    )

    logout.click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("/login")
    )

    assert "/login" in driver.current_url


# TEST 7: Dashboard access without login.
def test_dashboard_without_login(driver):

    driver.get(BASE_URL + "/dashboard")

    WebDriverWait(driver, 10).until(
        EC.url_contains("/login")
    )

    assert "/login" in driver.current_url


# TEST 8: Dashboard cards displayed.
def test_dashboard_cards(driver):

    perform_login(
        driver,
        "student",
        "student123"
    )

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CLASS_NAME, "cards")
        )
    )

    assert "Student Profile" in driver.page_source
    assert "Courses" in driver.page_source
    assert "Results" in driver.page_source
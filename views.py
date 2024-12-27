import requests
from concurrent.futures import ThreadPoolExecutor
import time
import random
from fake_useragent import UserAgent
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class SessionTester:
    def __init__(self, base_url, num_requests=5000, concurrent_threads=3):
        self.base_url = base_url
        self.num_requests = num_requests
        self.concurrent_threads = concurrent_threads
        self.ua = UserAgent()
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def simulate_quick_view(self, driver):
        """Simulate a quick page view"""
        try:
            # Quick scroll to middle of page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5)")
            time.sleep(0.5)  # Brief pause
            return 0.5
            
        except Exception as e:
            self.logger.error(f"Error in quick view simulation: {str(e)}")
            return 0

    def make_request(self, request_id):
        """Make a single quick request"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument(f'user-agent={self.ua.random}')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(5)  # Set shorter timeout
            
            try:
                start_time = time.time()
                
                driver.get(self.base_url)
                
                # Quick wait for body
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                time_on_page = self.simulate_quick_view(driver)
                cookies = driver.get_cookies()
                duration = time.time() - start_time
                
                self.logger.info(f"Request {request_id}: Duration: {duration:.2f}s")
                
                return {
                    'request_id': request_id,
                    'status_code': 200,
                    'duration': duration,
                    'time_on_page': time_on_page,
                    'cookies': cookies,
                    'user_agent': driver.execute_script("return navigator.userAgent")
                }
                
            finally:
                driver.quit()

        except Exception as e:
            self.logger.error(f"Request {request_id} failed: {str(e)}")
            return None

    def run_test(self):
        """Execute quick session testing"""
        self.logger.info(f"Starting quick session testing against {self.base_url}")
        
        results = []
        with ThreadPoolExecutor(max_workers=self.concurrent_threads) as executor:
            future_to_request = {executor.submit(self.make_request, i): i 
                               for i in range(self.num_requests)}
            
            for future in future_to_request:
                result = future.result()
                if result:
                    results.append(result)

        self.analyze_results(results)
        
    def analyze_results(self, results):
        """Quick analysis of results"""
        if not results:
            self.logger.error("No results to analyze")
            return

        successful_requests = len(results)
        avg_duration = sum(r['duration'] for r in results) / len(results)

        self.logger.info("\nQuick Test Results:")
        self.logger.info(f"Total Successful Requests: {successful_requests}")
        self.logger.info(f"Average Duration: {avg_duration:.2f}s")
        
        return {
            'total_requests': len(results),
            'successful_requests': successful_requests,
            'avg_duration': avg_duration
        }

if __name__ == "__main__":
    tester = SessionTester(
        base_url="example.com",
        num_requests=10,
        concurrent_threads=5  # Increased threads for faster completion
    )
    tester.run_test()
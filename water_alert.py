import time
import itertools

from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sqlalchemy import create_engine, select, and_
from create_db import projects, updates

if __name__ == '__main__':
    # initialize db engine
    db = create_engine('sqlite:///water_alert.db', echo=False)
    
    # check for job id in projects table
    conn = db.connect()
    s = select([projects.c.id])
    res = conn.execute(s).fetchall()
    conn.close()
    
    pids = [pid for sub in res for pid in sub]
    last = max(pids)
    
    site = 'http://buildinganewchicago.org/'
    title = 'Department Water Management - City Of Chicago'
    first_name = 'John'
    last_name = 'Little'
    email_addr = 'chicagowateralert@gmail.com'
    
    driver = webdriver.Chrome()
    driver.get(site)
    assert title in driver.title
    
    for r in itertools.product(range(17, 18), range(1000)):
        # generate project id
        pid = '{:02d}01{:03d}'.format(r[0], r[1])
        
        # check to see if we've already searched it
        if pid in pids or int(pid) <= last:
            continue
        
        # wait for page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "getProject")))
        
        # enter project id
        proj_id = driver.find_element_by_id('reqProjId')
        proj_id.clear()
        proj_id.send_keys(pid)
        
        # search
        driver.find_element_by_id('getProject').click()
        
        # try block for wait(s)
        try:
            # wait for search to complete        
            WebDriverWait(driver, 10).until(lambda driver: driver.find_elements(By.ID, 'btnRegister') or driver.find_elements(By.ID, 'warnMsg'))
            
            # check for register button
            if(driver.find_elements(By.ID, 'btnRegister')):
                # click to register
                driver.find_element_by_id('btnRegister').click()
                
                # wait for form to load (1s sleep for fade)
                WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.ID, "btnRegisNotice")))
                time.sleep(1)        
                
                # enter form data
                fname = driver.find_element_by_id('fname')
                fname.clear()
                fname.send_keys(first_name)
                
                lname = driver.find_element_by_id('lname')
                lname.clear()
                lname.send_keys(last_name)
                
                email = driver.find_element_by_id('Email')
                email.clear()
                email.send_keys(email_addr)
                
                rest_email = driver.find_element_by_id('restEmail')
                rest_email.clear()
                rest_email.send_keys(email_addr)
                
                #register 
                driver.find_element_by_id('btnRegisNotice').click()
                
                # wait for form to clear
                WebDriverWait(driver, 300).until(EC.invisibility_of_element_located((By.ID, "btnRegisNotice")))
                time.sleep(1)
                
                # close registration form
                driver.find_element_by_id('closed-register').click()
                
                # refresh website
                driver.refresh()
        except:
            continue
        
        # short sleep between loops
        time.sleep(1)
    
    driver.close()
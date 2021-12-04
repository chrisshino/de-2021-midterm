from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fighters_list import fighters
import pandas as pd
import time
import os


chromeOptions = Options()
chromeOptions.headless = True
driver = webdriver.Chrome(options=chromeOptions)

# driver = webdriver.Chrome()

final_table_dict = {
          "fighter": [],
          "WeightClass": [],
          "Height": [],
          "Stance": [],
          "Fight Date": [],
          "Opponent": [],
          "Result": [],
          "TSL": [],
          "TSA":[],
          "SSL":[],
          "SSA":[],
          "SCBL": [],
          "SCBA": [],
          "SCHL":[],
          "SCHA": [],
          "SCLL": [],
          "SCLA":[],
          "TDL":[],
          "TDA":[],
          "SGBL":[],
          "SGBA": [],
          "SGHL" : [],
          "SGHA" : [],
          "ADTB": [],
          "ADHG": [],
          "ADTM": [],
          "ADTS":[],
          "Sub Attempts": []
        }


def scraper():
  try:
    for letter in fighters:
      current_search_letter = f"search={letter}"
      driver.get(f"http://www.espn.com/mma/fighters?{current_search_letter}")
      WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "td a")))
      for list_fighter in fighters[letter]:
        print(list_fighter)
        driver.get(f"http://www.espn.com/mma/fighters?{current_search_letter}")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "td a")))
        search = driver.find_elements_by_tag_name('td a')
        for scraped_fighter in search:
          if scraped_fighter.text == list_fighter:
            fighters_profile_link = scraped_fighter.get_attribute('href')
            driver.get(fighters_profile_link)
            driver.find_elements_by_css_selector(".Nav__Secondary__Menu .Nav__Secondary__Menu__Item")[2].click()
            time.sleep(1)
            strikingTable = driver.find_elements_by_tag_name("tbody")[0]
            clinchTable = driver.find_elements_by_tag_name("tbody")[1]
            groundTable = driver.find_elements_by_tag_name("tbody")[2]
            time.sleep(1)
            strikingTableRows = strikingTable.find_elements_by_tag_name("tr")
            clinchTableRows = clinchTable.find_elements_by_tag_name("tr")
            groundTableRows = groundTable.find_elements_by_tag_name("tr")
            time.sleep(1)
            fighter_weightclass = driver.find_elements_by_css_selector(".PlayerHeader__Team_Info")[0].find_elements_by_tag_name("li")[1].text
            fighter_height = driver.find_elements_by_css_selector(".fw-medium div")[0].text.split(",")[0].strip().replace("\\\\", "")
            fighter_stance = driver.find_elements_by_css_selector(".fw-medium div")[4].text

            non_empty_cells = []      
            strikingTableRowsText = []
            clinchTableRowsText = []
            groundTableRowsText = [] 

            for i,row in enumerate(strikingTableRows):
              tempArray = []
              cells = row.find_elements_by_tag_name("td")   
              if cells[11].text != "-":
                non_empty_cells.append(i)
                for td in cells:
                  tempArray.append(td.text)
              strikingTableRowsText.append(tempArray)
            for i,row in enumerate(clinchTableRows):
              tempArray = []
              cells = row.find_elements_by_tag_name("td")
              for td in cells:
                  tempArray.append(td.text)
              clinchTableRowsText.append(tempArray)
            for i,row in enumerate(groundTableRows):
              tempArray = []
              cells = row.find_elements_by_tag_name("td")
              for td in cells:
                  tempArray.append(td.text)
              groundTableRowsText.append(tempArray)

            for cell in non_empty_cells:
              # stand up
              final_table_dict["fighter"].append(list_fighter)
              final_table_dict["WeightClass"].append(fighter_weightclass)
              final_table_dict["Height"].append(fighter_height)
              final_table_dict["Stance"].append(fighter_stance)
              final_table_dict["Fight Date"].append(strikingTableRowsText[cell][0])
              final_table_dict["Opponent"].append(strikingTableRowsText[cell][1])
              final_table_dict["Result"].append(strikingTableRowsText[cell][3])
              final_table_dict["TSL"].append(int(strikingTableRowsText[cell][7]))
              final_table_dict["TSA"].append(int(strikingTableRowsText[cell][8]))
              final_table_dict["SSL"].append(int(strikingTableRowsText[cell][9]))
              final_table_dict["SSA"].append(int(strikingTableRowsText[cell][10]))
              # clinch
              final_table_dict["SCBL"].append(int(clinchTableRowsText[cell][4]))
              final_table_dict["SCBA"].append(int(clinchTableRowsText[cell][5]))
              final_table_dict["SCHL"].append(int(clinchTableRowsText[cell][6]))
              final_table_dict["SCHA"].append(int(clinchTableRowsText[cell][7]))
              final_table_dict["SCLL"].append(int(clinchTableRowsText[cell][8]))
              final_table_dict["SCLA"].append(int(clinchTableRowsText[cell][9]))
              final_table_dict["TDL"].append(int(clinchTableRowsText[cell][12]))
              final_table_dict["TDA"].append(int(clinchTableRowsText[cell][13]))
              # ground
              final_table_dict["SGBL"].append(int(groundTableRowsText[cell][4]))
              final_table_dict["SGBA"].append(int(groundTableRowsText[cell][5]))
              final_table_dict["SGHL"].append(int(groundTableRowsText[cell][6]))
              final_table_dict["SGHA"].append(int(groundTableRowsText[cell][7]))
              final_table_dict["ADTB"].append(int(groundTableRowsText[cell][11]))
              final_table_dict["ADHG"].append(int(groundTableRowsText[cell][12]))
              final_table_dict["ADTM"].append(int(groundTableRowsText[cell][13]))
              final_table_dict["ADTS"].append(int(groundTableRowsText[cell][14]))
              final_table_dict["Sub Attempts"].append(int(groundTableRowsText[cell][15]))
            break   
          else:
            continue
            
  finally: 
    # print(final_table_dict)
    df = pd.concat({k: pd.Series(v) for k, v in final_table_dict.items()}, axis=1)  
    path = os.path.join(os.getcwd(), "figher_output.csv")
    df.to_csv(path, index=False)
    print(path)
    driver.close()
    driver.quit()
    return path

if __name__ == '__main__':
  scraper()

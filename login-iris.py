import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select # for selections
# The ChromeDriver class starts the ChromeDriver server process at creation 
# and terminates it when quit is called. This can waste a significant amount of time 
# for large test suites where a ChromeDriver instance is created per test. 
# A solution is to use the ChromeDriverService. 
# This is available for most languages and allows you to start/stop the ChromeDriver server yourself.
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# an alternative way (maybe better) to parse html content from selenium
# Selenium stores the source HTML in the driver's page_source attribute. You would then load the page_source into BeautifulSoup as follows:
from bs4 import BeautifulSoup # https://www.crummy.com/software/BeautifulSoup/bs4/doc/

# doi api. to get info from the doi. requires installation of pip install crossrefapi.  https://pypi.org/project/crossrefapi/1.0.3/
from crossref.restful import Works

#importing pyperclip to faster paste in the author field
import pyperclip
from selenium.webdriver.common.keys import Keys

# for reading dictionary
import ast

def info_from_table(page_source):

  # To get information from the table without the need of interacting with it
  # maybe it is better to use a html parser
  # driver.page_source # from the API : get the source of the current page. 
  html = page_source
  soup = BeautifulSoup(html, 'html.parser')
  
  # get the table
  table = soup.find_all('table', attrs={'id':'mysubmissions'})
  print(len(table)) 
  
  for row in table[0].find_all('tr'): # tr are the lines in the table
      #print(row.text)
      columns = row.find_all('td') # the first row is the title and has no 'td' but only 'th'. so it's columns is empty
      #print(columns)
      for column in columns:
          as_ = column.find_all('a') 
          if(len(as_)>0): print(as_[0].get_text()) # this gives the summary and the status ( successo / non inviato )
          #for a in as_:
          #  print(a.get_text()) # this should be the summary 

def get_doi_from_table(driver,table_entry_line):
    summary = driver.find_element_by_xpath('//*[@id="mysubmissions"]/tbody/tr[{0}]/td[1]/a'.format(table_entry_line))
    print(summary)
    print(summary.text)
    summary_str = summary.text
    start = summary_str.find('DOI')+4
    end = summary_str.find('. ',start)
    doi = summary_str[start:end]
    print('DOI from table : ' + doi)
    return doi



from html.parser import HTMLParser # https://docs.python.org/3/library/html.parser.html

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)

    def handle_data(self, data):
        print("Encountered some data  :", data)


# functions to interact with the table
def change_lenght_table(driver, lenght):
  # change lenghts of table
  select = Select(driver.find_element_by_name('mysubmissions_length'))
  all_selected_options = select.all_selected_options
  print(all_selected_options)
  options = select.options
  for op in options:
    print(op.get_attribute('value'))
  select.select_by_value('{0}'.format(length))
  time.sleep(10)



# abstract...
class Publication(object):

      def __init__(self, doi):
          self.doi = doi
          self.title = get_title(doi) # from the doi get the title (from some db)
          self.authors = get_authors(doi) # from the doi the authors (from some db)

      def retrieve_title(self, doi):
          '''Look at a db and retunr the title of the doi'''
          return 'dummy title'

      def retrieve_authors(self, doi):
          ''' Look at a db and return the title of the doi'''
          return 'dummy author'

      def edit_pubication(self):
          '''
          Enter the edit mode of the publication
          '''
          return True


def load_pub_dictionary(input_file):
    f = open(input_file, 'r')
    contents  =  f.read()
    dictionary = ast.literal_eval(contents)
    f.close()
    return dictionary

def check_publication_status(doi, pub_dictionary):
    if (doi in pub_dictionary.keys()):
        return pub_dictionary[doi]
    else:
        print('Key not present in dictionary')
        return 'to-edit'

def update_publication_dictiornary(input_file, pub_dictionary, doi):
    f = open(input_file, 'w')
    pub_dictionary[doi] = 'to-send'
    print('DOI {0} has now status {1} written in the file'.format(doi,pub_dictionary[doi]) )
    f.write( str(pub_dictionary) )
    f.close()


#login
def iris_login(driver):

  username_box = driver.find_element_by_name('username')
  username_box.send_keys('pierluigi.bortignon')
  psw_box = driver.find_element_by_name('password')
  psw_box.send_keys('cagliari_10892')
  invia_bt = driver.find_element_by_name('submit')
  invia_bt.click()
  time.sleep(2) # Let the user actually see something!



def test_table(driver):
  # loop over the table to interact with it
  table = driver.find_element_by_id('mysubmissions')
  #print(table)
  for line in range(1,5):
    #print(line)
    ####################
    ## tr sono le righe
    ####################
    tr = driver.find_element_by_xpath('//table/tbody/tr[{0}]'.format(line))
    #print(tr)
    #print(tr.get_attribute('class'))
    ######################
    ## td sono le colonne. Nella visualizzazione std 'Dati Riassuntivi[1] (odd/even) : Tipologia[2] : Status[3] : MIUR[4] : Ultima modifica[5] : Azioni[6]'
    ## The Azioni is interesting because there is a hidden form clas
    ######################
    td = driver.find_element_by_xpath('//table/tbody/tr[{0}]/td[1]'.format(line))
  #  print(td.get_attribute('href')) # prints out the link_text of the href
  #  print(td.text) # prints out the whole record
    href = driver.find_element_by_xpath('//table/tbody/tr[{0}]/td[1]/a[1]'.format(line))
    #print(href.get_attribute('href')) #prints the link
    #print(href.text) # print the link_text of the href
    # get the action button!
    #button_down = WebDriverWait(driver,20).until(EC.presence_of_element_located( driver.find_element_by_xpath('//table/tbody/tr[{0}]/td[6]/div[1]/a[1]/i[2]'.format(line) ) ) )
    button_down = driver.find_element_by_xpath('//table/tbody/tr[{0}]/td[6]/div[1]/a[1]/i[2]'.format(line))
    button_down.click() # this is necessary to be able to have the visible_actions clickable
    #visible_actions = driver.find_element_by_xpath('//table/tbody/tr[{0}]/td[6]/div[1]/ul[1]/li[1]/a[1]'.format(line))
    # this is a safety guard to wait for the button_down click to be done.
    visible_actions = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,'//table/tbody/tr[{0}]/td[6]/div[1]/ul[1]/li[1]/a[1]'.format(line)) ) )
    if (visible_actions.get_attribute('data-action') == 'resume' ):  visible_actions.click()
    else: print('Item is not resumable')
    print(visible_actions.get_attribute('data-action'))
    print(visible_actions.get_attribute('href'))
    time.sleep(10)
    #visible_actions.findElement(By.linkText("Completa inserimento")).click()
    #if ( visible_actions.get_attribute('data-action') == 'resume'  ): visible_actions.click()
    #driver.execute_script(visible_actions)
    #hidden_actions = driver.find_element_by_xpath("//table/tbody/tr[{0}]/td[6]/div[2]/form[1]/input[@type='submit']".format(line))
    #print(hidden_actions.get_attribute('id'))
    #print(hidden_actions.get_attribute('type'))
    #hidden_actions.click()
    #hidden_actions.submit()



def table_filter_provvisorio(driver):
  # filter table
  filter_button = driver.find_element_by_css_selector('button.filterbutton.btn.btn-default.btn-xs')
  driver.execute_script('arguments[0].click();',filter_button) # filter button is covered by another element. see https://stackoverflow.com/questions/37879010/selenium-debugging-element-is-not-clickable-at-point-x-y
  time.sleep(5)
  #now I need to move to the form data-template="tmpl-filter-form" of xpath //*[@id="filterDialog"]/div/div/div[2]/form
  filter_form = driver.find_element_by_xpath('//*[@id="filterDialog"]/div/div/div[2]/form')
  draft_selector = driver.find_element_by_xpath('//*[@id="radios-1"]') # radios-1 is provvisorio
  driver.execute_script('arguments[0].click();',draft_selector)
  time.sleep(5)
  filter_button = driver.find_element_by_xpath('//*[@id="filterDialogOk"]')
  filter_button.click()
  time.sleep(5)


def enter_edit_publication(driver,table_entry_line):
    # should be better to get also the name of the publication and its doi here - integrating with the class
    actions_button_down = driver.find_element_by_xpath('//table/tbody/tr[{0}]/td[6]/div[1]/a[1]/i[2]'.format(table_entry_line))
    actions_button_down.click() # this is necessary to be able to have the visible_actions clickable
    # this is a safety guard to wait for the button_down click to be done.
    visible_actions = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,'//table/tbody/tr[{0}]/td[6]/div[1]/ul[1]/li[1]/a[1]'.format(table_entry_line)) ) )
    print(visible_actions.get_attribute('data-action'))
    print(visible_actions.get_attribute('href'))
    if (visible_actions.get_attribute('data-action') == 'resume' ):  visible_actions.click() # resume corresponds to "Completa inserimento"
    else: 
        print('Item is not resumable. Maybe no more item to be resumed. Quitting')
        driver.quit()
    time.sleep(10)
 

def click_successivo(driver, workflow):
    if ( workflow == 1 ):
      button_next = driver.find_element_by_xpath('//*[@id="allAfterCollection"]/div[7]/div/input[2]') # bottone successivo in workflow 1
    if ( workflow == 2 ):
      button_next = driver.find_element_by_xpath('//*[@id="allAfterCollection"]/div[33]/div/input[3]')
    if ( workflow == 3 ):
      button_next = driver.find_element_by_xpath('//*[@id="allAfterCollection"]/div[5]/div/input[3]')
    if ( workflow == 4 ):
      button_next = driver.find_element_by_xpath('//*[@id="uploadForm"]/div[4]/input[3]') #
    if ( workflow == 5 ):
      button_next = driver.find_element_by_xpath('//*[@id="nextDiv"]/input')
    if ( workflow == 6 ):
      button_next = driver.find_element_by_xpath('//*[@id="edit_metadata"]/div[3]/div[2]/input[2]') # this is the "Concludi" button
    button_next.click()
    time.sleep(5)
    return workflow+1
       

def get_publication_doi_from_workflow(driver):
    # in workflow 2
    doi = driver.find_element_by_xpath('//*[@id="dc_identifier_doi"]')
    print('Now working with publication DOI : {0}'.format(doi.get_attribute('value')))
    return doi.get_attribute('value')

def get_author_string(work_doi_api, publication_doi):
  author_string = ''
  print('In get_author_string: pub_doi: {0}'.format(publication_doi))
  if ( len(publication_doi) > 0 ):
    work_dict = work_doi_api.doi(publication_doi)
    for author in work_dict['author']:
      author_string += '{0} {1} ; '.format(author.get('family',''),author.get('given',''))
  else:
    print('WARNING: DOI not FOUND')
    author_string = 'Bortignon P. ; others ; CMS Collaboration'
  return author_string

def edit_author_string(driver, author_list):
    # in workflow 3
    author_box = driver.find_element_by_xpath('//*[@id="widgetContributorSplitTextarea_dc_authority_people"]') 
    if (author_box.is_enabled()): print('author_box enabled')
    else: print('author boc is not enabled')
    if (author_box.is_displayed()):  print('author_box displayed')
    else: print('author box is not displayed')
    time.sleep(2)
    old_cp = pyperclip.paste()
    pyperclip.copy(author_list)
    # here there is the possibility that the string of auhtors is not empty so I need to click on "Modifica stringa autori"
    if ( not author_box.is_displayed() ):
        btn_edit_author_string = driver.find_element_by_xpath('//*[@id="widgetContributorEdit_dc_authority_people"]')
        btn_edit_author_string.click()
    #author_box.send_keys(author_list) # very slow for long string
    #author_box.send_keys(pyperclip.paste( )) # still very slow
    author_box.clear()
    author_box.send_keys(Keys.SHIFT, Keys.INSERT)
    pyperclip.copy(old_cp)
    # now click on the button "Elabora stringa autori"
    button_elaborate_author_list = driver.find_element_by_xpath('//*[@id="widgetContributorParse_dc_authority_people"]')
    button_elaborate_author_list.click()
    time.sleep(25) # it takes a long time to elaborate the author string
    # close warning message that might appears at the the end of elaboration of the author string. 
    # It usually says that the number of authors is too large and it can't find a match to inside people
    w_m_close = driver.find_element_by_xpath('//*[@id="contributorDialogueConfirm_dc_authority_people"]/div/div/div[3]/button[1]')
    if(w_m_close.is_displayed()): w_m_close.click()
    time.sleep(2)
 

def select_author_from_author_string(driver):
  btn_author_bortignon = driver.find_element_by_xpath('//span[text()="Bortignon P."]') # //*[@id="spanContributorTextArea_dc_authority_people_1251"]
  #btn_author_bortignon = driver.find_element_by_xpath('//*[@id="spanContributorTextArea_dc_authority_people_1"]') # this works
  print('btn_author_bortignon.get_attribute(id) = {0}'.format(btn_author_bortignon.get_attribute('id')) )
  print('btn_author_bortignon.get_attribute(class) = {0}'.format(btn_author_bortignon.get_attribute('class')) )
  driver.execute_script('arguments[0].click();',btn_author_bortignon)
  print(btn_author_bortignon)
  if(btn_author_bortignon.is_enabled()):
    print('Bortignon found.')
  else:
    print('Bortignon not found')
  time.sleep(2)
  # now select from the popup. It should always be the first of the list. In a better script I lok for the author name
  # something like that : '//*[@id="widgetContributorMenuList_dc_authority_people"]/ul/li[contains(text()="BORTIGNON")]'
  btn_select_bortignon = driver.find_element_by_xpath('//*[@id="widgetContributorMenuList_dc_authority_people"]/ul/li[1]')
  time.sleep(2)
  #check if I am in the database
  if( btn_select_bortignon.get_attribute('data-authority') != 'null' ):
      print('Author found in database. Clicking')
      author_in_db = True
      btn_select_bortignon.click()
  else:
      print('Author not found in database.')
      author_in_db = False
  return author_in_db
 

# this will not work because bortignon is not visible (it's in the nth page of the table). I could filter but it takes a lot f time. Better to risk
def check_author_acknowledgement(driver):
    author_acknowledgement = driver.find_element_by_xpath('//table[@id="widgetContributorTableAuthors_dc_authority_people"]/span[text()="Bortignon P.")]') # //*[@id="widgetContributorTableAuthors_dc_authority_people"]
    label_author_acknowledgement = author_acknowledgement.get_attribute('class')
    print('Author {0} acknowledgement: {1}'.format( author_acknowledgement.text , author_acknowledgement.get_attribute('class') ) )
    if ( 'acknowledged' in label_author_acknowledgement ):
      return True

# edit workflow
def edit_publication(driver,work_doi_api,table_doi):

  # we are now in workflow 1
  workflow = 1
  if( workflow == 1 ):
    workflow = click_successivo(driver,workflow)
  
  # now we are in wf 2
  publication_doi = '' # initialisation of DOI
  if ( workflow == 2 ):
    publication_doi = get_publication_doi_from_workflow(driver)
    if (table_doi != publication_doi):
        print('WARNING: Table doi different from workflow doi! {0}, {1}'.format(table_doi,publication_doi))
        driver.quit()
    workflow = click_successivo(driver,workflow)
  
  #now in workflow 3
  if (workflow == 3):
    author_string = get_author_string(work_doi_api, publication_doi)
    edit_author_string(driver, author_string)
    author_in_db = select_author_from_author_string(driver)
    if( author_in_db ) :
      workflow = click_successivo(driver, workflow)
    else:
      driver.quit()
  
  if( workflow == 4 ):
    workflow = click_successivo(driver, workflow)
  
  if( workflow == 5 ):
    workflow = click_successivo(driver, workflow)
  
  if( workflow == 6 ): # last one
    workflow = click_successivo(driver, workflow)
  
  time.sleep(10)
  return workflow





from selenium.webdriver.chrome.options import Options
# if I would not use the Remote I could use the options and give it directly to the driver
chrome_options = Options()  
chrome_options.add_argument("--headless")  

########
# main
########
service = Service('/usr/local/bin/chromedriver')
service.start()
work_doi_api = Works() # initialise the work for the doi api
driver = webdriver.Remote(service.service_url)
#driver = webdriver.Remote(service.service_url, desired_capabilities=chrome_options.to_capabilities() )
driver.get('https://iris.unica.it/mydspace')
# implicit wait. https://selenium-python.readthedocs.io/waits.html
driver.implicitly_wait(10) # seconds

#driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browserClientA"}})


pub_dictionary = load_pub_dictionary('publication_dictionary.txt')
print(pub_dictionary)

iris_login(driver)

#change_lenght_table(driver,100) # options includes 10, 25, 50, 100, 500

#get some info from the html page
#info_from_table(driver.page_source)

table_filter_provvisorio(driver)

#def edit_publication(driver,work_doi_api):

table_line = 1

for i in range(1,50) : # do it for 10 publications at the time
  table_doi = get_doi_from_table(driver,table_line)
  print('Editing DOI: ' + table_doi)
  
  print( 'Status on db :' + check_publication_status(table_doi,pub_dictionary) )
  if ( check_publication_status(table_doi,pub_dictionary) != 'to-edit' ):
      print('WARNING: publication not to be edited')
      driver.quit()
  
  #here it would be good to pass the doi
  enter_edit_publication(driver,table_line)
  
  workflow = edit_publication(driver, work_doi_api, table_doi)
  if( workflow == 7):
      print('Publication {0} added.'.format(table_doi))
      update_publication_dictiornary('publication_dictionary.txt', pub_dictionary, table_doi)
  time.sleep(2)

print(pub_dictionary)
print('Lenght of dictionary : '.format(len(pub_dictionary)))

driver.quit()



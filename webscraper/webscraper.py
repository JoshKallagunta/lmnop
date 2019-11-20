from bs4 import BeautifulSoup as soup
import requests
import html
import time

def is_time_str(s): #checks for string in time format, returns True if in correct format
    try:
        time.strptime(s, '%I:%M %p')
    except:
        return False
    else:
        return True

#scrapes options from dropdown and strips html tags
def drop_scrape(html, parent, pName, child):
    list_name = [str(i.text) for i in html.find(parent, attrs={'name': pName}).findAll('option')]
    list_name = list_name[1:] #removes unnecessary dropdown option
    return list_name

'''
*Builds event dictionaries for content_list from scraped events*
First Avenue's event calendar is formatted so the divs for each line of information
aren't unique, and the number of lines of information aren't uniform (some events have
two+ price points, have guest performers, are sold out, etc.)

Dictionary used for easier conversion to JSON
String keys for readability, sorting/queries
TODO: Figure out a way to cut down on elifs so this isn't so ugly/inefficient
'''
def scrape_sort(content, venues, ages, content_list):
    temp_dict = {}
    ctr = 0
    price_ctr = 1
    prevPriceKey = 'price1'
    for event in content.findAll('div', attrs={"class": "field-items"}):
        e = event.text
        is_time = is_time_str(e)
        if (e == 'day of show' or e == 'reserved table' or e == 'two show package' 
        or e == 'reserved balcony seating'): #appends these strings to their price and removes old price string
            new_string = temp_dict[prevPriceKey] + ' ' + e
            del temp_dict[prevPriceKey]
            temp_dict[prevPriceKey] = new_string
        elif (ctr == 1 and 0 in temp_dict.keys()): #appends headline performer name to promoter titles like "93x presents" and removes old string
            new_string = temp_dict[0] + ': ' + e
            temp_dict['title'] = temp_dict[0]
            temp_dict['title'] = new_string
            del temp_dict[0]
        elif (e != 'Buy Tickets' and e != ''): #checks for relevant event information to append to temp_dict ('Buy Tickets' link and blank strings aren't utilized)
            temp_ctr = ctr #keeps ctr count after assigning ctr to key string
            if (ctr == 0 and 'present' not in e): ctr = 'title' #changes first key to 'title' if it's not a promoter title that needs performer added to it
            elif (ctr == 1 and 'with' in e): #removes 'with' from guest performer string
                temp_e = e.replace('with ','')
                e = temp_e
                ctr = 'guests'
            elif (ctr >= 1 and 'with' not in e and '$' in e): #checks for price value and number of price values for event
                ctr = 'price' + str(price_ctr)
                price_ctr = price_ctr + 1
                prevPriceKey = ctr #keeps count of number of prices for event
            elif (ctr >= 1 and 'at ' in e): #removes 'at ' from venue names to make it easier to check venue list
                temp_e = e.replace('at ', '')
                e = temp_e
                if e in venues: ctr = 'venue' #checks if string in venues list
            elif (ctr >= 1 and e in venues): ctr = 'venue' #checks if string in venues list when there isn't an 'at '
            elif (ctr >= 2 and is_time == True): ctr = 'time' #checks for time value
            elif (ctr >= 3 and e in ages): ctr = 'age' #checks for age requirement in ages list
            elif (ctr >= 3 and e == 'Sold Out'): ctr = 'soldout' #checks for 'Sold Out' status
            temp_dict[ctr] = e
            ctr = temp_ctr
            ctr = ctr + 1
        elif (e == '' and len(temp_dict)>=2): #checks for blank strings/lines at the beginning & end of event lines
            if '— CANCELED' in temp_dict['title']: #removes canceled events, resets temp_dict, ctr and price_ctr for next event
                temp_dict = {}
                ctr = 0
                price_ctr = 1
            else: #appends temp_dict to content_lest, resets temp_dict, ctr and price_ctr for next event
                content_list.append(temp_dict)
                temp_dict = {}
                ctr = 0
                price_ctr = 1

url = 'https://first-avenue.com/calendar'
response = requests.get(url,timeout=5)
content = soup(response.content, "html.parser")

venues = drop_scrape(content, 'select', 'venue', 'option')
venues.append('Mainroom + Entry') #adds missing venue option
ages = drop_scrape(content, 'select', 'age', 'option')

content_list = []

scrape_sort(content, venues, ages, content_list)

for i in content_list:
    print()
    print(i)
    print()

#print(content)
from bs4 import BeautifulSoup as soup
import requests
import html
import psycopg2

def cal_scrape(html,pClass):
    return html.findAll("div", attrs={"class": pClass})

def child_scrape2(child, cClass):
    return child.find("div", {"class": cClass}).text

def child_scrape(content_dict, key, child, cClass):
    content_dict[key] = child_scrape2(child, cClass)
    return content_dict[key]


#div classes
cal_item = "field-group-format group_firstave_calendar_item field-group-div group-firstave-calendar-item speed-none effect-none"
pres_item = "field field-name-field-event-presenter field-type-entityreference field-label-hidden"
perf_item = "field field-name-field-event-performer field-type-entityreference field-label-hidden"
guest_item = "field field-name-field-event-special-guests field-type-entityreference field-label-hidden"
adv_item = "field field-name-field-event-price field-type-number-float field-label-hidden"
doorp_item = "field field-name-field-event-door-price field-type-number-float field-label-hidden"
doord_item = "field field-name-field-event-door-day-of field-type-list-text field-label-hidden"
ven_item = "field field-name-field-event-venue field-type-entityreference field-label-hidden"
time_item = "field field-name-field-event-date field-type-datetime field-label-hidden"
age_item = "field field-name-field-event-age field-type-taxonomy-term-reference field-label-hidden"
stat_item = "field field-name-field-event-status field-type-list-text field-label-hidden"

url = 'https://first-avenue.com/calendar'
response = requests.get(url,timeout=5)
content = soup(response.content, "lxml")
event_list = []

def insert_events(event_list):
    sql = """INSERT INTO events (date, presenter, performer, guest, adv_price, door_price, venue, time, age, status) VALUES(%(date)s, %(presenter)s, %(performer)s, %(guest)s, %(adv_price)s, %(door_price)s, %(venue)s, %(time)s, %(age)s, %(status)s)"""
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.executemany(sql,event_list)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

#TODO: Add date key, value
#Could possibly make this a switch, with the div class as key
def main(content, event_list):

    cal_list = cal_scrape(content, cal_item)
    content_dict = {}

    for ctr,child in enumerate(cal_list,1):
        content_dict['date'] = 'Wednesday, January 1st, 2019'
        performer = child_scrape2(child, perf_item)
        if 'CANCELED' in performer:
            continue
        try:
            child_scrape(content_dict, 'presenter', child, pres_item)   
        except:
            content_dict['presenter'] = None
            pass
        content_dict['performer'] = performer
        try:
            guest = child_scrape2(child, guest_item)
            new_guest = guest.replace('with ', '')
            content_dict['guest'] = new_guest
        except:
            content_dict['guest'] = None
            pass
        try:
            child_scrape(content_dict, 'adv_price', child, adv_item)
        except:
            content_dict['adv_price'] = None
            pass
        try:
            desc = child_scrape2(child, doord_item)
        except:
            desc = ''
        try:
            price = child_scrape2(child, doorp_item)
            content_dict['door_price'] = price + ' ' + desc
        except:
            content_dict['door_price'] = None
            pass
        try:
            venue = child_scrape2(child, ven_item)
            try:
                new_venue = venue.replace('at ','')
                content_dict['venue'] = new_venue
            except:
                content_dict['venue'] = venue
                pass
        except:
            pass
        child_scrape(content_dict, 'time', child, time_item)
        child_scrape(content_dict, 'age', child, age_item)
        status = child_scrape2(child, stat_item)
        if status == "Sold Out":
            content_dict['status'] = status
        else:
            content_dict['status'] = None
        if len(content_dict) >= 2:
            event_list.append(content_dict)
            content_dict = {}
        else:
            content_dict = {}

main(content, event_list)
insert_events(event_list)

for event in event_list:
    print()
    print(event)
    print()
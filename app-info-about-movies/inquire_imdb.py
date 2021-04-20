from bs4 import BeautifulSoup
from datetime import datetime
from difflib import SequenceMatcher
import re

# TODO: replace all display with logger
from IPython.display import HTML, display

import pandas as pd
pd.set_option("display.max_colwidth", 80)
pd.set_option("display.max_colwidth", 500)


#----------------------------------------------------------------
# ----- functions to inquire IMDB.com
#----------------------------------------------------------------
def get_r_imdbID(sess, title, year=None, type_=None, verbose=0):
    if verbose >= 1:
        print("{} {} {}".format(title,
                                str(year) if year else '',
                                type_ if type_ else ''))
    # ----- send request
    title_ = title.replace('&', 'and').replace(':', ' ').replace(' ', '%20')
    url = "https://www.imdb.com/find?ref_=nv_sr_fn&q={:s}&s=all".format(title_)
    #print(url)
    r_imdbID = sess.get(url)
    assert r_imdbID.status_code==200, \
        'Your requested title {:s} is NOT found'.format(title)
    # ----- parse HTML with bs4
    soup_imdbID = BeautifulSoup(r_imdbID.text, "lxml")
    return r_imdbID, soup_imdbID


def _year_found(title):
    year_found = None
    year_found_re = re.search(r'\d{4}', title)
    if year_found_re:
        year_found = int(year_found_re.group(0))
    else:
        year_found = datetime.today().year
    return year_found


def _year_difference_lt(found_df, year, year_diff=2):
    yd = False
    if not found_df.empty:
        yd = abs(found_df.Title.apply(_year_found) - year) <= year_diff + 1
    return yd


def _get_mask_by_year_type(found_df, year, type_):
    mask_not_episode = ~found_df.Title.str.lower().str.contains('episode')
    mask_not_game = ~found_df.Title.str.lower().str.contains('video game')
    if type_=='series':
        mask = found_df.Title.str.lower().str.contains('serie')
    elif type_=='film' and year:
        mask = _year_difference_lt(found_df, year)
    else:
        mask = found_df.Title.astype(bool)
    return mask & mask_not_episode & mask_not_game


def get_ID_through_search(soup_imdbID, year, type_, verbose=0):
    imdbID=None
    single_found_df = pd.DataFrame(columns=['N', 'Title', 'imdbID', 'ID'])

    found_table = soup_imdbID.find('table', {'class': 'findList'})
    if found_table:
        found_df = pd.DataFrame([[el.text for el in tr.find_all('td')] +
                       [el.a.get('href').split('/')[2] for el in tr.find_all('td')] 
                                        for tr in found_table.find_all('tr')],
                  columns=['N', 'Title', 'imdbID', 'ID']
                )

        # ----- display
        if verbose >=1:
            display(found_df)

        # ----- filter by year and type_
        single_mask = _get_mask_by_year_type(found_df, year, type_)
        single_found_df = found_df.loc[single_mask, :]

        # ----- extract imdbID
        if not single_found_df.empty:
            imdbID = single_found_df.loc[:, 'ID'].values[0]

        # ----- display  
        if verbose>=1 and (single_found_df.shape[0] != found_df.shape[0]):
            display(single_found_df)
            print("imdbID:", imdbID)

    return imdbID, single_found_df

def get_ID_from_IMDB(sess, title, year=None, type_=None, verbose=0,
                     umlaut_patten = re.compile(r'[aou]e'),
                     untertitel_patten = re.compile(r' - |: ')):
    r_imdbID, soup_imdbID = get_r_imdbID(sess, title, year=None, 
                                                   type_=None, verbose=verbose)
    imdbID, single_found_df = get_ID_through_search(soup_imdbID, year=year, 
                                                  type_=type_, verbose=verbose)
    if not imdbID:
        title_ = title.lower()
        umlaut = re.search(umlaut_patten, title_)
        untert = re.search(untertitel_patten, title_)
        if umlaut: # replace umlauts
            title_ = title_.replace('ae', 'ä').replace('oe', 'ö').replace('ue', 'ü')  # replacement
            r_imdbID, soup_imdbID = get_r_imdbID(sess, title_, year=None, type_=None, verbose=verbose)
            imdbID, single_found_df = get_ID_through_search(soup_imdbID, year=year, type_=type_, verbose=verbose)
        if untert and (not imdbID):  # remove 'untertitel' by splitting and taking the first part
            title_ = title_.split(untert.group(0))[0]
            r_imdbID, soup_imdbID = get_r_imdbID(sess, title_, year=None, type_=None, verbose=verbose)
            imdbID, single_found_df = get_ID_through_search(soup_imdbID, year=year, type_=type_, verbose=verbose)
    return imdbID, single_found_df


def get_title(single_found_df, verbose=0):
    return single_found_df.loc[:, 'Title'].values[0]

def get_year_in_title(single_found_df, verbose=1):
    found_title = single_found_df.loc[:, 'Title'].values[0]
    year = _year_found(found_title)
    if verbose>=1:
        print('Found year:', year)
    return year

# ------------------------------------------------------------------------
def get_r_countries(sess, imdbID):
    url = "https://www.imdb.com/title/{:s}/?ref_=fn_al_tt_1".format(imdbID)
    r_countries = sess.get(url)
    assert r_countries.status_code==200, 'Webpage {} is not accessible'.format(url)
    # ---- extract info with bs4
    soup_countries = BeautifulSoup(r_countries.text, "lxml")
    return r_countries, soup_countries

def get_countries(soup_countries,  verbose=1):
    countries = list()
    for country in soup_countries.find_all('a', href=re.compile('country_of_origin')):
        countries.append(country.text.strip())
    if verbose>=1: 
        print('------------')
        print('Countries')
        print('------------')
        display(countries)
    return countries

def get_genres(soup_countries,  verbose=1):
    genres = list()
    for genre in soup_countries.find_all('a', href=re.compile('ref_=tt_stry_gnr')):
        genres.append(genre.text.strip())
    if verbose>=1: 
        print('------------')
        print('Genres')
        print('------------')
        display(genres)
    return genres



# ------------------------------------------------------------------------
def get_r_credits(sess, imdbID):
    url = "https://www.imdb.com/title/{:s}/companycredits?ref_=tt_dt_co".format(imdbID)
    r_credits = sess.get(url)
    assert r_credits.status_code==200, 'Webpage {} is not accessible'.format(url)
    # ---- extract info with bs4
    soup_credits = BeautifulSoup(r_credits.text, "lxml")
    return r_credits, soup_credits


def rm_spaces_from_string(stri):
    return " ".join(stri.split())


def get_company_credits(soup_credits, countries=None, verbose=1):
    production = []
    for h4 in  soup_credits.findAll('h4', {'id':'production'}):
        if verbose>=1:
            print('------------')
            print(h4.text)
            print('------------')
        ul = h4.find_next('ul', {'class':'simpleList'})
        for li in ul.findAll('li'):
            if li.find('a').get('href').startswith("/company"):
                production.append(rm_spaces_from_string(li.text.strip()))
                #print(li.text)
    if verbose>=1:
        display(production)

    distributors_DE = []
    distributors_countries = []
    for h4 in  soup_credits.findAll('h4', {'id':'distributors'}):
        if verbose>=1:
            print('------------')
            print(h4.text)
            print('------------')
        ul = h4.find_next('ul', {'class':'simpleList'})
        #print(ul)
        for li in ul.findAll('li'):
            if li.find('a').get('href').startswith("/company"):
                # disributors in Germany
                if '(Germany)' in li.text:
                    distributors_DE.append(rm_spaces_from_string(li.text.replace('(Germany)','').strip()))
                    #print(li.text)
                if countries:
                    for country in [c for c in countries if c !='Germany']:
                        if '('+country+')' in li.text:
                            distributors_countries.append(rm_spaces_from_string(li.text.strip()))

    # ----- display
    if verbose>=1:
        display(HTML('<H4> distributors_DE </H4>'))
        display(distributors_DE)
        display(HTML('<H4> distributors_countries </H4>'))
        display(distributors_countries)
    
    return production, distributors_DE, distributors_countries


#----------------------------------------------------------------
# ----- internal processing
#----------------------------------------------------------------
def filter_list_nach_string_pattern(distributors, patterns=(r'\(TV\)', r'\(all media\)')):   
    distributors_TV = None
    # ----- if one of patterns in distributors_DE, take only those
    s = r'|'.join(patterns)  #s = '('+'|'.join(patterns)+')' # patterns to one string 
    p = re.compile(s) # compile pattern
    distributors_TV = [di for di in distributors if p.search(di)]
    return distributors_TV


#acronym_pattern = re.compile(r'[A-Z]{3,}')
def modify_acronym_dict_from_list(acronym_dict, distributors, pattern=re.compile(r'[A-Z]{3,}')):
    #if pattern is None:
    #    pattern = acronym_pattern
    for distri in distributors:
        #print(distri)
        brokes = distri.split('(')
        #print(brokes)
        if len(brokes) > 1:
            key = brokes[1].rstrip(') ')
            #print('    key', key)
            if pattern.match(key) and key not in acronym_dict.keys(): 
                value = brokes[0].strip()
                acronym_dict[key] = value
                #print('    value', value)
    return acronym_dict


def string_li(li, sep=', '):
    """ get string from list """
    return sep.join(li)


# ----------------------------------------------------------------------  Übereinstimmung
def strip_runde_klammer(sentence, pat = None):
    if pat is None:
        pat = re.compile(r'\(.*\)')
    return re.sub(pat, '', sentence).strip()

def overlay(production, distributors_DE):
    prodis = list(set(map(strip_runde_klammer, production)) & set(map(strip_runde_klammer, distributors_DE)))
    return prodis


def match_distributors_production(production, distributors, verbose=1):
    """
        Returns list of 'production-ditributor-matches'
    """
    prodis=[]
    
    if production and distributors:
        # ----- match the names as they are
        prodis = overlay(production, distributors)
        # ----- match after stripping parenthesis
        if not prodis:
            produc = set(pro.split('(')[0].strip() for pro in production)
            distri = set(dis.split('(')[0].strip() for dis in distributors)
            prodis = overlay(produc, distri)
        # ----- fuzzy match by finding longest match 
        if not prodis:
            matches = list()
            for di in distri:
                dis = re.split(r'\W+', di)
                #logger.debug(', ',join(dis))print(dis)
                for pr in produc:
                    pro = re.split(r'\W+' ,pr)
                    #logger.debug(', ',join(pro)); print(pro)
                    match = SequenceMatcher(None, dis, pro).find_longest_match(0, len(dis), 0, len(pro))
                    matches.append([match, dis, pro])
                    #print(match, match.a+match.b, match.size)
                    #print(dis[match.a:match.a+match.size])
                    #print(pro[match.b:match.b+match.size])
                    #print()
            matches_sorted = sorted(matches, key= lambda m: (-m[0].size, m[0].a+m[0].b) )
            match = matches_sorted[0]
            #logger.debug(match)
            #logger.debug(match[1][match[0].a:match[0].a+match[0].size])
            #logger.debug(match[2][match[0].b:match[0].b+match[0].size])
            found_match = match[1][match[0].a:match[0].a+match[0].size]
            prodis = [" ".join(found_match)]

        if len(prodis) == 1:
            if prodis[0] in ('Company', 'Entertainment', 'Film', 'International', 
                             'Pictures', 'Productions', 'Studios', 'Television'):
                prodis = []

        if verbose>=1:
            print('--------------')
            print('Übereinstimmung Production & Distributors')
            print('--------------')
            print(" ,".join(prodis))
    return prodis
#m = match_distributors_production(production, distributors_DE, verbose=1)




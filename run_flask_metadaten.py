#######################################################################################
### MetadatenProgramm Webservice
#######################################################################################
from collections import OrderedDict
from datetime import datetime
from flask import Flask, render_template, request #, jsonify
import requests

import app_info_about_movies.inquire_imdb as iimdb

proxies = None



#with open('pkl_dict/manuallyCorrected.txt', 'r') as fin:
#    reader=csv.reader(fin, skipinitialspace=True, delimiter='\t', quotechar="'")
#    manuallyCorrected = {row[0]:row[1] for row in reader}

app = Flask(__name__)
#api = Api(app)

#identified = LRU(3)
#@lru_cache(maxsize=2**12)

#parser = reqparse.RequestParser()
#parser.add_argument('ingredient', required=True, dest='ingredient'
#                    help="Type ingeredient that you want manually correct")
#parser.add_argument('Titel', required=True, dest='title',
#                    help="Type manual identification: {error_msg}")
#parser.add_argument('Jahr', required=True, dest='year', type=int, 
#                    help="Producktionsjahr für Film oder Erfassungsjahr for Serie")
#parser.add_argument('Art', required=True, dest='type_',
#                    help="Spielfilm or Serie")

# ----- pure flask
@app.route('/')
def input_for_metadaten():
    return render_template('input_for_metadaten.html', hostname='https://metadatentv.netrtl.com')  #hostname='https://kochbar-id.netrtl.com'

# ----- does not work
#class InputForMetadaten(Resource):
#    def get(self):
#        # --- #hostname='https://kochbar-id.netrtl.com'
#        return render_template('input_for_metadaten.html', hostname='localhost:5000/')  
# ----- this SHOULD work, 
# ----- see https://stackoverflow.com/questions/19315567/returning-rendered-template-with-flask-restful-shows-html-in-browser
#    def get(self):
#        headers = {'Content-Type': 'text/html'}
#        return make_response(render_template('index.html'),200,headers)






@app.route('/output_metadaten', methods = ['POST', 'GET'])
def output_metadaten():
    if request.method == 'POST':
        # ----- input from the HTML form
        title = request.form.get('Titel')
        year = request.form.get('Jahr');
        try: 
            year = int(year)
        except ValueError:
            year = datetime.today().year
        type_ = request.form.get('Art')

        # ----- output will be saved in the dictionary
        result = OrderedDict()
        poster_url = ''
        
        sess = requests.Session()
        if proxies: 
            sess.proxies = proxies

        imdbID, single_found_df = iimdb.get_ID_from_IMDB(sess, title, year=year, type_=type_, verbose=0)

        if imdbID:
            year_found = iimdb.get_year_in_title(single_found_df, verbose=1)
            titel_found = iimdb.get_title(single_found_df)

            result['titel']=title;
            result['titel_found']=titel_found;
            result['year']=year;
            result['year_found']=year_found;
            r_countries, soup_countries = iimdb.get_r_countries(sess, imdbID)
            
            try:
                poster_url = soup_countries.find('img', attrs={'class': 'ipc-image'}).get('src')
            except AttributeError:
                poster_url = ''
            

            genres = iimdb.get_genres(soup_countries, verbose=1);
            result['genres']=", ".join(genres);
            countries = iimdb.get_countries(soup_countries, verbose=1);
            result['countries']=", ".join(countries);
            #
            r_credits, soup_credits = iimdb.get_r_credits(sess, imdbID)
            
            production, distributors_DE, distributors_countries = iimdb.get_company_credits(soup_credits,
                                                                                      countries=countries, verbose=1)
            result['production_companies'] = ", ".join(production);

            distributors_DE_TV = iimdb.filter_list_nach_string_pattern(distributors_DE)
            distributors_countries_TV = iimdb.filter_list_nach_string_pattern(distributors_countries)

            result['distributors_DE'] = ", ".join(distributors_DE);
            result['TV_distributors_DE'] = ", ".join(distributors_DE_TV);
            
            result['distributors_countries'] = ", ".join(distributors_countries);
            result['TV_distributors_countries'] = ", ".join(distributors_countries_TV);

            prodisDE = iimdb.match_distributors_production(production, distributors_DE)
            result['produc_AND_distrib_DE'] = ", ".join(prodisDE);

            prodisCO = iimdb.match_distributors_production(production, distributors_countries)
            result['produc_AND_distrib_countries'] = ", ".join(prodisCO);

            presents = iimdb.filter_list_nach_string_pattern(production,  patterns=(r'\(presents\)',))
            result['presents1st'] = ''
            if presents:
                result['presents1st'] = presents[0].replace('(presents)', '').strip()

        sess.close()

        return render_template("output_metadaten.html", result = result, poster_url=poster_url)

    
## ----- Actually setup the Api resource routing here
#api.add_resource(UserManual, '/')
#api.add_resource(IdentifiedList, '/identify/')
#api.add_resource(Identify, '/identify/<ingredient>')
#api.add_resource(InputForMetadaten, '/')
#api.add_resource(OutputMetadaten, '/output_metadaten')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)

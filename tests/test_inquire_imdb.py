import pytest
import requests

import app_info_about_movies.inquire_imdb as iimdb


def test_match_distributors_production():
    production_companies = ['Mandeville Films', 'Walt Disney Pictures (presents) (as Disney)']
    distributors_DE = ['Walt Disney Studios Home Entertainment (2020) (all media) (Ultra HD Blu-ray)']
    prodis = iimdb.match_distributors_production(production_companies, distributors_DE, verbose=False)
    assert prodis[0] == 'Walt Disney'


@pytest.fixture(scope='session')
def sess():
    return requests.Session()

def test_get_ID_frim_IMDB(sess):
    imdbID, single_found_df = iimdb.get_ID_from_IMDB(sess, 
                                                        title="Lost", 
                                                        year=2004, 
                                                        type_="serie", 
                                                        verbose=0)
    assert imdbID == 'tt0411008'

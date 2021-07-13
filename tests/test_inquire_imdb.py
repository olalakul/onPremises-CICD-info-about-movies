import importlib
iimdb = importlib.import_module("app-info-about-movies.inquire_imdb", ".")

def test_match_distributors_production():
    production_companies = ['Mandeville Films', 'Walt Disney Pictures (presents) (as Disney)']
    distributors_DE = ['Walt Disney Studios Home Entertainment (2020) (all media) (Ultra HD Blu-ray)']
    prodis = iimdb.match_distributors_production(production_companies, distributors_DE, verbose=False)
    assert prodis[0] == 'Walt Disney'

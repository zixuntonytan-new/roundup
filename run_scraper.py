import traceback
import sys
from datetime import datetime
import pandas as pd
from src.data_comparer import HistoricDataComparer

from src.scraper.sites.bea_scraper import BEAScraper
from src.scraper.sites.bis_scraper import BISScraper
from src.scraper.sites.boe_scraper import BOEScraper
from src.scraper.sites.ecb_scraper import ECBScraper
from src.scraper.sites.fed_atlanta_scraper import FedAtlantaScraper
from src.scraper.sites.fed_board_notes_scraper import FedBoardNotesScraper
from src.scraper.sites.fed_board_scraper import FedBoardScraper
# from src.scraper.sites.fed_boston_scraper import FedBostonScraper  # fedinprint disabled
from src.scraper.sites.fed_chicago_scraper import FedChicagoScraper
from src.scraper.sites.fed_cleveland_scraper import FedClevelandScraper
from src.scraper.sites.fed_dallas_scraper import FedDallasScraper
# from src.scraper.sites.fed_kansas_city_scraper import FedKansasCityScraper  # fedinprint disabled
# from src.scraper.sites.fed_minneapolis_scraper import FedMinneapolisScraper  # fedinprint disabled
from src.scraper.sites.fed_new_york_scraper import FedNewYorkScraper
from src.scraper.sites.fed_san_francisco_scraper import FedSanFranciscoScraper
from src.scraper.sites.fed_philadelphia_scraper import FedPhiladelphiaScraper
from src.scraper.sites.fed_richmond_scraper import FedRichmondScraper
# from src.scraper.sites.fed_st_louis_scraper import FedStLouisScraper  # fedinprint disabled
from src.scraper.sites.imf_scraper import IMFScraper
from src.scraper.sites.nber_scraper import NBERScraper

# List of scraper classes (BFI removed — site returns 403)
scrapers = [
            BEAScraper,
            BISScraper,
            BOEScraper,
            ECBScraper,
            FedAtlantaScraper,
            FedBoardNotesScraper,
            FedBoardScraper,
            # FedBostonScraper,  # fedinprint disabled
            FedChicagoScraper,
            FedClevelandScraper,
            FedDallasScraper,
            # FedKansasCityScraper,  # fedinprint disabled
            # FedMinneapolisScraper,  # fedinprint disabled
            FedNewYorkScraper,
            FedSanFranciscoScraper,
            FedPhiladelphiaScraper,
            FedRichmondScraper,
            # FedStLouisScraper,  # fedinprint disabled
            IMFScraper,
            NBERScraper,
            ]

########## Part 1: Scraping Data ##########
print(f'--------------------\n Part 1: Data Scrape \n--------------------')

total_tasks = len(scrapers)
attempted = 0
succeeded = 0

dfs = []

for ScraperClass in scrapers:
    scraper_instance = ScraperClass()

    try:
        print(f'Scraping {scraper_instance.source} using {ScraperClass.__name__} ...')
        df = scraper_instance.fetch_and_process_data()
        if df is not None:
            dfs.append(df)
            print(df)
            succeeded += 1
            scraper_instance.update_scraper_status(source=scraper_instance.source,
                                                   is_successful=True,
                                                   filename='streamlit/scraper_status.txt')
            print(f"{scraper_instance.source} scraped successfully.")
        else:
            raise Exception("No data returned")

    except Exception as e:
        print(f'Error with {ScraperClass.__name__}: {str(e)}')
        scraper_instance.update_scraper_status(source=scraper_instance.source,
                                               is_successful=False,
                                               filename='streamlit/scraper_status.txt')
        traceback.print_exc()

    attempted += 1
    print(
        f'\n{attempted} of {total_tasks} tasks attempted. {succeeded} of {total_tasks} tasks succeeded.'
        f'\n----------------------------------------'
    )

print('Concatenating all newly scraped data into one data frame...')

if dfs:
    df = pd.concat(dfs, ignore_index=False)
    print(df)
else:
    print('No data frames to concatenate. dfs is empty. Script terminating.')
    sys.exit(1)

########## Part 2: Comparing to Historical Data ##########
print(f'--------------------\n Part 2: Comparing to Historical Data \n--------------------')

comparer = HistoricDataComparer()
print('HistoricDataComparer class instantiated.')

novel_df = comparer.compare(df)
print('novel_df: ')
print(novel_df)

new_count = 0
if not novel_df.empty:
    comparer.save_local_results(novel_df=novel_df)
    comparer.append_ids_to_historic(novel_df=novel_df)
    print(f'Historic set updated in {comparer.WP_IDS_FILEPATH}')
    comparer.append_data_to_historic(novel_df=novel_df)
    print(f'Results saved in {comparer.WP_DATA_FILEPATH}')
    new_count = len(novel_df)

# Write last-run metadata for the Streamlit dashboard
run_date = datetime.now().strftime('%Y-%m-%d')
with open('streamlit/last_run.txt', 'w') as f:
    f.write(f"{run_date},{new_count}")
print(f'Last run info written: {run_date}, {new_count} new papers')

print(f'--------------------\n Script has completed running. \n--------------------')

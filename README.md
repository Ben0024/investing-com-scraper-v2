# Investing.com Scraper
## Execution
#### Development
```bash
MODE=dev python main_tradingview.py
```
#### Production
```bash
MODE=prod python main_tradingview.py
```

## Environment Variables
* variables
    `MODE` - `dev` or `prod`
* dotenv files
    * production
        * `.env.local.production`
        * `.env.production`
        * `.env.local`
        * `.env`
    * development
        * `.env.local.development`
        * `.env.development`
        * `.env.local`
        * `.env`
    * required variables
        * CUSTOM_STORAGE_DIR: directory to store the custom data (investing.com)

## Structure
* main.py
* Investing.com engine
    * packages/investing/engine.py
    * Crawler
        * packages/investing/crawler.py
        * Speeds up by disabling unnecessary browser functions
    * Runs once a day
    * Get raw crawled data from Investing.com with crawler
    * Preprocess raw data
        * packages/investing/preprocessor.py
        * Get release date and index date
        * Fix special cases
        * Get timestamp of index date (First day of the month at 12:00AM UTC)
        * Fill missing timestamps by deducing one month from previous timestamps
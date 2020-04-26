from jqdatasdk import *

if __name__ == "__main__":
    auth('13277099856', '1221gzcC')
    df = finance.run_query(query(finance.SW1_DAILY_VALUATION).filter(finance.SW1_DAILY_VALUATION.code == '801150').limit(10))
    print(df)

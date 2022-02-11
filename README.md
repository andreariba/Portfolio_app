# Portfolio Dashboard

Visualize the current value and simulate the future evolution of the input Portfolio.

## The portfolio

The portfolio is specified by the yaml file (portfolio.yml). It contains information about the tickers (YAHOO format), the amount owned, the currency of the assets and the type they belong to, needed to define an allocation.

To start the dashboard app run
```
python index.py
```
It takes some times to start the app (~1 minute) because it runs the simulations of the forecasted portfolio.

## Pages

The dashboard includes 3 pages (/apps).

 1. Summary. Perfomance of the portfolio in the last year, calculates percentage change and volatility (standard deviation of the relative changes). It shows also the top gainers and losers from the last year, useful to have an overview of the current sentiment.
![home_screenshot](imgs/home.png)

 2. Allocation.
![allocation_screenshot](imgs/allocation.png)

 3. Forecast. Very simple simulation of the future values of each assets and of the overall portfolio. The simulation are based on the estimation of the Copula of the multivariate distribution of percentage changes in the previous year.
![forecast_screenshot](imgs/forecast.png)


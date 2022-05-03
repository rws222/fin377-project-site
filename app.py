# from flask import Flask, render_template

# app = Flask(__name__)

# @app.route("/")
# def index():
    
#     # Load current count
#     f = open("count.txt", "r")
#     count = int(f.read())
#     f.close()

#     # Increment the count
#     count += 1

#     # Overwrite the count
#     f = open("count.txt", "w")
#     f.write(str(count))
#     f.close()

#     # Render HTML with count variable
#     return render_template("index.html", count=count)

# if __name__ == "__main__":
#     app.run()


from flask import Flask, render_template, request, jsonify


import numpy as np
import pandas as pd
import seaborn as sns
import pandas_datareader as pdr  # to install: !pip install pandas_datareader
from datetime import datetime
from datetime import date
import matplotlib.pyplot as plt 
from dateutil.relativedelta import relativedelta
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
import math
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt import risk_models
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import plotting
import copy
from pypfopt import objective_functions
import os

my_path = os.path.abspath(__file__)

#fig, ax = plt.subplots()

app = Flask(__name__)

@app.route('/')
def home():
   return render_template('index.html')



@app.route('/results', methods=['POST', 'GET'])
def get_results():
   if request.method == "POST":      
      req = request.get_json()
      # set answers from the survey
      q1 = float(req[0]['ans1'])
      q2 = float(req[0]['ans2'])
      q3 = float(req[0]['ans3'])
      q4 = float(req[0]['ans4'])
      q5 = float(req[0]['ans5'])
      q6 = float(req[0]['ans6'])
      q7 = float(req[0]['ans7'])
      q8 = float(req[0]['ans8'])
      
      # get A value
      th_score = q1 + q2
      ra_score = q3 + q4 + q5 + q6 + q7 + q8

      type_investor = 'abc'
      a_value = 0

      if 1 < th_score < 2:
         #type_investor = 'conservative investor'
         a_value = 1
      elif 3 < th_score < 10 | 0 < ra_score < 16:
         #type_investor = 'conservative investor'
         a_value = 1
      elif th_score < 11 | 0 < ra_score < 16:
         #type_investor = 'conservative investor'
         a_value = 1
      elif 3 < th_score < 11 | 17 < ra_score < 39:
         #type_investor = 'moderately conservative investor'
         a_value = 2
      elif 3 < th_score < 5 | 40 < ra_score < 100:
         #type_investor = 'moderately conservative investor'
         a_value = 2
      elif 6 < th_score < 11 | 40 < ra_score < 65:
         #type_investor = 'moderate investor'
         a_value = 3
      elif 6 < th_score < 7 | 66 < ra_score < 87:
         #type_investor = 'moderate investor'
         a_value = 3
      elif 8 < th_score < 11 | 66 < ra_score < 87:
         #type_investor = 'moderately aggressive investor'
         a_value = 4
      elif 6 < th_score < 77 | 88 < ra_score < 100:
         #type_investor = 'moderate investor'
         a_value = 5
      elif 8 < th_score < 10 | 88 < ra_score < 100:
         #type_investor = 'moderately aggressive investor'
         a_value = 4
      elif th_score < 11 | 88 < ra_score < 100:
         #type_investor = 'aggressive'
         a_value = 5
            
      

      # if type_investor == 'conservative investor':
      #    a_value = 1
      # elif type_investor == 'moderately conservative investor':
      #    a_value = 2
      # elif type_investor == 'moderate investor':
      #    a_value = 3
      # elif type_investor == 'moderately aggressive investor':
      #    a_value = 4
      # else:
      #    a_value = 5
   
      # at this point, we have our a value in a_value
      # begin the calculations
      
      # create a list of ETFs we will use - multiple industries 
      list_etfs = ['JMOM', 'VUG', 'VONV', 'IUSV', 'FREL', 'XSW', 'VHT', 'MGK', 'JVAL', 
             'VOT', 'VIOG', 'NURE', 'GLD', 'XLU', 'TQQQ', 'VCR', 'FNCL', 'IFRA',
            'PBD', 'RYT', 'FTEC', 'SCHI', 'SUSC', 'VTC', 'VCIT']
      
      # set start and end dates 
      start  = datetime.now() - relativedelta(years=10)
      end    = datetime.now() 
      
      # # download data
      # etf_prices = pdr.get_data_yahoo(list_etfs, start=start, end=end)
      # etf_prices = etf_prices.filter(like='Adj Close') 
      # etf_prices.columns = list_etfs
      
      # get etf_prices from data.csv
      etf_prices = pd.read_csv('etf_prices/data.csv')
      etf_prices.drop(['Date'], axis=1, inplace=True)
      
      etf_data = etf_prices.describe().T
      etf_data['Annualized Volatility'] = etf_data['std'] * math.sqrt(252)
      
      
      
      
      #download current risk free rate

      start2  = datetime.now() - relativedelta(years=1)
      end2    = datetime.now() 
      risk_free_rate = pdr.DataReader("IRLTLT01USM156N", "fred", start2,end2)
      risk_free_rate = risk_free_rate.values[0]/100
      risk_free_rate = risk_free_rate.item()
      
      e_returns = expected_returns.capm_return(etf_prices)#, span = 200)
   
      # all this taken from https://builtin.com/data-science/portfolio-optimization-python
      etf_cm = risk_models.exp_cov(etf_prices)#,span=100)
   
   
   
   
   
      # make and download plots
      
      
      fig, ax = plt.subplots()

      # set up the EF object & dups for alt uses
      ef = EfficientFrontier(e_returns, etf_cm)
      ef_max_sharpe = copy.deepcopy(ef)

      # plot the ports and the frontier
      risk_range = np.linspace(0.05, 0.3, 100)
      plotting.plot_efficient_frontier(ef, ef_param="risk", ef_param_range=risk_range,
                                       ax=ax, show_assets=True)

      ########################################################
      # TO FIGURE OUT:
      # add a max util... Where is the RF asset tho???
      ########################################################

      # Find+plot the tangency portfolio
      ef_max_sharpe.max_sharpe(risk_free_rate=risk_free_rate)
      ret_tangent, std_tangent, _ = ef_max_sharpe.portfolio_performance()
      ax.scatter(std_tangent, ret_tangent, marker="*", s=100, c="r", label="Max Sharpe")

      #max utility
      ef_max_util = EfficientFrontier(np.array([ret_tangent,risk_free_rate]), 
                                       np.array([[std_tangent,0],[0,0]]))
      ef_max_util.max_quadratic_utility(risk_aversion=2, market_neutral = False)
      ret_maxU, std_maxU, _ = ef_max_util.portfolio_performance()
      ax.scatter(std_maxU, ret_maxU, marker="*", s=100, c="b", label="Max Util")

      point1 = [0, risk_free_rate]
      point2 = [std_tangent, ret_tangent]

      x_values = [point1[0], point2[0]]
      y_values = [point1[1], point2[1]]

      plt.plot(x_values, y_values)

      # Output
      ax.set_title("Efficient Frontier with random portfolios")
      ax.legend()
      plt.tight_layout()
      # my_file = "ef_scatter.png"
      # plt.savefig(os.path.join(my_path, my_file))
      plt.savefig("static/img/ef_scatter.png", dpi=200)
      #plt.show()
      
      # clear plot
      plt.cla() 
      plt.clf()
      ax.clear()
      
      
      
      
      
      # get optimal risky portfolio and optimal complete portfolio data
      optimal_risky_portf = pd.DataFrame(ef_max_sharpe.portfolio_performance(verbose=True))
      optimal_complete_portfolio = pd.DataFrame(ef_max_util.portfolio_performance(verbose=True))
      
      
      
      
      list_cweights = list(ef_max_util.clean_weights().values())
      list_sweights = list(ef_max_sharpe.clean_weights().values())
      
      # pie chart for complete portfolio

      list_piechart = []
      for i in list_sweights:
         list_piechart.append(i*list_cweights[1])
      list_piechart.append(list_cweights[0])
      
      my_labels = ['JMOM', 'VUG', 'VONV', 'IUSV', 'FREL', 'XSW', 'VHT', 'MGK', 'JVAL', 
             'VOT', 'VIOG', 'NURE', 'GLD', 'XLU', 'TQQQ', 'VCR', 'FNCL', 'IFRA',
            'PBD', 'RYT', 'FTEC', 'SCHI', 'SUSC', 'VTC', 'VCIT','Risk Free Asset: 10-year Government Bond']

      dataforpie = pd.DataFrame(
         {'Asset': my_labels,
         'Weight': list_piechart
         })
      dataforpie = dataforpie.query('Weight > 0.01')
      
      fig, ax = plt.subplots()
      
      plt.pie(dataforpie["Weight"], labels = dataforpie["Asset"], startangle = 90, shadow = True, autopct='%1.1f%%')
      plt.title('Breakdown of your portfolio')
      plt.savefig("static/img/compl_port_pie.png", dpi=200)

      # clear plot
      plt.cla() 
      plt.clf()
      ax.clear()

      # new_list = list(ef_max_util.clean_weights().values())
      # my_labels = ["Risk Free Asset", "Risky Portfolio"]
      # myexplode = [0.2, 0]

      # plt.pie(new_list, labels=my_labels, startangle = 90, explode = myexplode, shadow = True, autopct='%1.1f%%')
      # plt.title('Breakdown of your portfolio')
      # # my_file = "compl_port_pie.png"
      # # plt.savefig(os.path.join(my_path, my_file))
      # plt.savefig("static/img/compl_port_pie.png", dpi=200)
      
      
      # sharpe results
      
      sharpe_list = list(ef_max_sharpe.clean_weights().items())
      sharpe_results = pd.DataFrame(sharpe_list)
      list_names = ['Jpmorgan US Momentum Factor ETF','Vanguard Growth Index Fund ETF','Vanguard Russell 1000 Value Index Fund ETF'
                  ,'iShares Core S&P US Value ETF', 'Fidelity MSCI Real Estate Index ETF','SPDR S&P Software & Services ETF',
                  'Vanguard Health Care Index Fund ETF', 'Vanguard Mega Cap Growth ETF','Jpmorgan US Value Factor ETF',
                  'Vanguard Mid-Cap Growth Index Fund ETF','Vanguard S&P Small-Cap 600 Growth Index','Nuveen Short-Term REIT ETF',
                  'SPDR Gold Shares','Utilities Select Sector SPDR Fund','ProShares UltraPro QQQ','Vanguard Consumer Discretionary ETF',
                  'Fidelity MSCI Financials Index ETF','iShares US Infrastructure ETF','Invesco Global Clean Energy ETF',
                  'Invesco S&P 500 Eql Wght Technology ETF','Fidelity MSCI Information Technology Index ETF',
                  'Schwab 5-10 Year Corporate Bond ETF','iShares ESG Aware USD Corporate Bond ETF','Vanguard Total Corporate Bond ETF',
                  'Vanguard Intermediate-Term Corp Bond Idx Fund ETF']
      sharpe_results["Etf Name"] = list_names
            
      
      #pie chart for existing portfolio

      new_list1 = sharpe_results[1]
      my_labels1 = sharpe_results["Etf Name"]
      
      fig, ax = plt.subplots()

      plt.pie(new_list1, labels=my_labels1, startangle = 90, shadow = True, autopct='%1.1f%%')
      plt.title('Breakdown of your risky assets')
      # my_file = "existing_port_pie.png"
      # plt.savefig(os.path.join(my_path, my_file))
      plt.savefig("static/img/existing_port_pie.png", dpi=200)
      
      # clear all plots
      plt.cla() 
      plt.clf()
      ax.clear()
   
      # 0 - a value
      # 1 - opimal risky portfolio
      # 2 - optimal complete portfolio
      results = [{'a_value': a_value},
                 {'orp_ear': optimal_risky_portf[0][0], 'orp_annvol': optimal_risky_portf[0][1], 'orp_sr': optimal_risky_portf[0][2]},
                 {'ocp_ear': optimal_complete_portfolio[0][0], 'ocp_annvol': optimal_complete_portfolio[0][1], 'ocp_sr': optimal_complete_portfolio[0][2]}
                 ]
      return jsonify(results)
   return
      


if __name__ == '__main__':
   app.run()
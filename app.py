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
      answer1 = float(req[0]['ans1'])
      answer2 = float(req[0]['ans2'])
      answer3 = float(req[0]['ans3'])
      answer4 = float(req[0]['ans4'])
      answer5 = float(req[0]['ans5'])
      answer6 = float(req[0]['ans6'])
      answer7 = float(req[0]['ans7'])
      answer8 = float(req[0]['ans8'])
      answer9 = float(req[0]['ans9'])
      answer10 = float(req[0]['ans10'])
      
      # determine risk aversion variables for each question
      #q1
      e1 = 5
      v1 = 25
      a1 = 2*(e1-float(answer1))/v1

      #q2
      e2 = 50
      v2 = 2500
      a2 = 2*(e2-float(answer2))/v2

      #q3
      e3 = 500
      v3 = 250000
      a3 = 2*(e3-float(answer3))/v3

      #q4
      e4 = 1
      v4 = 9
      a4 = 2*(e4-float(answer4))/v4

      #q5
      e5 = 10
      v5 = 900
      a5 = 2*(e5-float(answer5))/v5

      #q6
      e6 = 100
      v6 = 90000
      a6 = 2*(e6-float(answer6))/v6

      #q7
      e7 = 75
      v7 = 1875
      a7 = 2*(e7-float(answer7))/v7

      #q8
      e8 = 25
      v8 = 1875
      a8 = 2*(e8-float(answer8))/v8

      #q9
      e9 = 60
      v9 = 2400
      a9 = 2*(e9-float(answer9))/v9

      #q10
      e10 = 600
      v10 = 240000
      a10 = 2*(e10-float(answer10))/v10
      
      # set risk aversion variable as mean of each question's a-value
      
      risk_aversion = (a1 + a2 + a3 + a4 + a5 + a6 + a7 + a8 + a9 + a10) / 10
      if risk_aversion < 0.000001: # avoid the float error when risk_aversion is too small
         risk_aversion = 0.000001
         
      print(risk_aversion)
   
      # at this point, we have our a value in a_value
      # begin the calculations
      
      # get etf_prices from data.csv
      etf_prices = pd.read_csv('etf_prices/data1.csv')
      etf_prices.drop(['Date'], axis=1, inplace=True)
      
      #download current risk free rate
      start2  = datetime.now() - relativedelta(years=1)
      end2    = datetime.now() 
      risk_free_rate = pdr.DataReader("IRLTLT01USM156N", "fred", start2,end2)
      risk_free_rate = risk_free_rate.values[0]/100
      risk_free_rate = risk_free_rate.item()
      
      e_returns = expected_returns.capm_return(etf_prices)#, span = 200)
   
      # covariance matrix
   
      # all this taken from https://builtin.com/data-science/portfolio-optimization-python
      etf_cm = risk_models.exp_cov(etf_prices)#,span=100)
   
      # efficient frontier generator
      
      #######################
      # plotting code follows
      #######################

      fig, ax = plt.subplots()

      # set up the EF object & dups for alt uses

      ef = EfficientFrontier(e_returns, etf_cm)
      ef_max_sharpe = copy.deepcopy(ef)
      ef_min_vol = copy.deepcopy(ef)

      # plot the ports and the frontier

      ef_min_vol.min_volatility()
      ret_min_vol, std_min_vol, _ = ef_min_vol.portfolio_performance()

      risk_range = np.linspace(std_min_vol, 0.8, 100)
      plotting.plot_efficient_frontier(ef, ef_param="risk", ef_param_range=risk_range,
                                       ax=ax, show_assets=True)

      # Find+plot the tangency portfolio

      ef_max_sharpe.max_sharpe(risk_free_rate=risk_free_rate)
      ret_tangent, std_tangent, _ = ef_max_sharpe.portfolio_performance()
      ax.scatter(std_tangent, ret_tangent, marker="*", s=100, c="r", label="Max Sharpe")
      print('Tangent:',ret_tangent, std_tangent)

      # add the CML line

      point1 = [0, risk_free_rate]
      point2 = [std_tangent, ret_tangent]

      x_values = [point1[0], point2[0]]
      y_values = [point1[1], point2[1]]

      plt.plot(x_values, y_values,label='Capital Market Line')

      # get the max utility port

      mu_cml = np.array([risk_free_rate,ret_tangent])
      cov_cml = np.array([[0,0],[0,std_tangent]])
      ef_max_util = EfficientFrontier(mu_cml,cov_cml)               
      ef_max_util.max_quadratic_utility(risk_aversion=risk_aversion)

      # plot the max utility port
      #      ef_max_util.portfolio_performance() fails (bc of RF asset? idk)
      #      so compute the portfolio return on our own...
      #      here is a hacky way to get the weights (%rf, %tan) out
      weights_opt = ef_max_util.clean_weights()
      weights_opt = np.array([e[1] for e in list(weights_opt.items())])
      std_maxU = np.dot(np.array(x_values),weights_opt)
      ret_maxU = np.dot(np.array(y_values),weights_opt)

      ax.scatter(std_maxU, ret_maxU, marker="*", s=100, c="blue", label="Max Util")


      # Output
      ax.set_title("Efficient Frontier with ETFs")
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
      
      my_labels = ['SPY', 'IVV', 'VOO', 'SPLG', 'SPXL', 'SPXS', 'SPDN', 'SPUU', 'NSPI', 'SPXU', 'UPRO', 
             'SDS', 'SH', 'SSO','JMOM', 'VUG', 'VONV', 'IUSV', 'FREL', 'XSW', 'VHT', 'MGK', 'JVAL', 
             'VOT', 'VIOG', 'NURE', 'GLD', 'XLU', 'TQQQ', 'VCR', 'FNCL', 'IFRA',
            'PBD', 'RYT', 'FTEC', 'SCHI', 'SUSC', 'VTC', 'VCIT','VEA','IEFA','EFA',
             'SCHF','EFV','SCZ','SPDW','FNDF','EWC','DBEF','GSIE','Risk Free Asset: 10-year Government Bond']

      dataforpie = pd.DataFrame(
         {'Asset': my_labels,
         'Weight': list_piechart
         })
      dataforpie = dataforpie.query('Weight > 0.01')
      
      fig, ax = plt.subplots()
      
      # pie chart for complete portfolio
      colors = sns.color_palette('Blues')[0:len(dataforpie["Weight"])]
      plt.pie(dataforpie["Weight"], labels = dataforpie["Asset"], startangle = 90, shadow = True, autopct='%1.1f%%', colors=colors)
      plt.title('Breakdown of your portfolio')
      plt.savefig("static/img/compl_port_pie.png", dpi=200)

      # clear plot
      plt.cla() 
      plt.clf()
      ax.clear()
   
   
   
      # Return successful request
   
      # 0 - a value
      # 1 - opimal risky portfolio
      # 2 - optimal complete portfolio
      results = [{'a_value': risk_aversion},
                 {'orp_ear': optimal_risky_portf[0][0], 'orp_annvol': optimal_risky_portf[0][1], 'orp_sr': optimal_risky_portf[0][2]},
                 {'ocp_ear': optimal_complete_portfolio[0][0], 'ocp_annvol': optimal_complete_portfolio[0][1], 'ocp_sr': optimal_complete_portfolio[0][2]}
                 ]
      return jsonify(results)
   return
      


if __name__ == '__main__':
   app.run()
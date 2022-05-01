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
app = Flask(__name__)

@app.route('/')
def home():
   return render_template('index.html')



@app.route('/results', methods=['POST', 'GET'])
def get_results():
   if request.method == "POST":
      req = request.get_json()
      
      myans1 = req[0]['tag1']
      myans1a = req[0]['tag1a']
      myans2 = req[1]['tag2']
      
      # run all of our code
   
      # download graphs
      
      
      results = [{'res_tag1': myans1, 'res_tag1a': myans1a},
                 {'res_tag2': myans2}]
      return jsonify(results)
   return
      
      
   



if __name__ == '__main__':
   app.run()
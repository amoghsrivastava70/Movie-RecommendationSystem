from flask import Flask, render_template ,request
import requests
import pickle as pkl
import numpy as np


popular=pkl.load(open("assets/popular_df.pkl" , 'rb'))

sim_scr=np.load("assets/similarity_scores.npz")['arr_0']
movie_data=pkl.load(open("assets/movie_data.pkl",'rb'))


app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html', 
                           title=list(popular['original_title'].values) , overview=list(popular['overview'].values) , release=list(popular['released'].values) , poster=list(popular['poster'].values) ,runtime=list(popular['runtime']) , rated=list(popular['rated']))

@app.route("/recom")
def recommend_page():
    return render_template('recom.html')



@app.route("/recommend_movies",methods=['POST'])
def recommend():
    try:
        user_inp=request.form.get("user_inp")

        indx=movie_data[movie_data['title']==user_inp].index[0]
        sim=sim_scr[indx]
        ans_arr= sorted(enumerate(sim) , key=lambda x:x[1] ,reverse=True)[1:7]
        # print(ans_arr)
        recomm=[]
        for mv in ans_arr:
            recomm.append(movie_data.iloc[mv[0]]['title'])
        
        
        recommended_movies=[]
         
        api_key='cda377a7'

        for i in recomm:
                try:

                    url=f"https://www.omdbapi.com/?t={i}&apikey={api_key}"
                    response = requests.get(url , timeout=4)
                    if response.status_code==200:
                        data=response.json()
                        # print(data)
                        recommended_movies.append({
                                    'poster': f"{data['Poster']}",
                                    'title': data['Title'],
                                    'release':data['Released'],
                                    'runtime':data['Runtime'],
                                    'overview': data['Plot']
                                })
                    # print(recommended_movies)
                except requests.exceptions.ConnectTimeout:
                    return render_template('connectionerr.html')

        
        return render_template('recom.html',data=recommended_movies)


    except IndexError:
        return render_template('error.html')


@app.route("/more_info",methods=['POST'])
def more_data():
    rec_query=request.form.get("query")
    
    api_key="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"
    

    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    data = {
        "model": "deepseek/deepseek-chat:free",
        "messages": [{"role": "user", "content": f"Provide me details about the movie '{rec_query}' with plot and other necessary details"}]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        data_ret=response.json()["choices"][0]["message"]["content"].replace('**','')
        return render_template('airesponse.html' , data=data_ret )
    else:
        return render_template('error.html')
    
    

if __name__ == "__main__":
    app.run(debug=True)
 
from flask import Flask, render_template ,request
import requests
import pickle as pkl
import numpy as np

popular=pkl.load(open(r'assets\popular_df.pkl' , 'rb'))
# print(popular)
sim_scr=np.load(r'assets\similarity_scores.npz')['arr_0']
# print(sim_scr)
movie_data=pkl.load(open(r'assets\movie_data.pkl','rb'))
# print(movie_data)

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
        
        # print("Movie Names: ",recomm)
        api_key='bdca24f0aa8772134dfc3e96fc8b4ac5'
        recommended_movies=[]
        for i in recomm:
            try:

                url = f"https://api.themoviedb.org/3/search/movie?query={i}&api_key={api_key}"
                response = requests.get(url ,timeout=2)

                if response.status_code == 200:
                    details = response.json()
                    if details['results']:
                        movie = details['results'][0]
                        recommended_movies.append({
                            'poster': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}",
                            'title': movie['title'],
                            'release':movie['release_date'],
                            'lang':movie['original_language'],
                            'overview': movie['overview']
                        })
            # print(recommended_movies)

            except requests.exceptions.ConnectTimeout:
                return render_template('connectionerr.html') 

        return render_template('recom.html',data=recommended_movies)

    except IndexError:
        return render_template('error.html')


if __name__ == "__main__":
    app.run(debug=True)
 
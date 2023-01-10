import streamlit as st
from streamlit import session_state as session
import requests
from itertools import cycle

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Movie Recommender", layout="centered")

# Load Our Dataset
@st.cache(persist=True, show_spinner=False, suppress_st_warning=True)
def load_data(data):
    df = pd.read_pickle(data)
    return df


#def vectorize_text_to_cosine_mat(data):
    tfidf_vect = TfidfVectorizer(analyzer='word', ngram_range=(1,2), stop_words='english')
    tfidf_mat = tfidf_vect.fit_transform(data.values.astype(str))
    # Get the cosine
    cosine_sim_mat = cosine_similarity(tfidf_mat)
    return cosine_sim_mat

# # Recommendation System
# @st.cache(persist=True, show_spinner=False, suppress_st_warning=True)
# def get_recommendations(title, cosine_sim_mat, df, num_of_rec=16):
#     # indices of the movies
#     movie_indices = pd.Series(df.index, index=df['title'])
#     # Index of the Movie
#     idx = movie_indices[title]

#     # Look into the cosine matrix for that index
#     sim_scores = list(enumerate(cosine_sim_mat[idx]))
#     sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
#     selected_movie_indices = [i[0] for i in sim_scores[1:num_of_rec]]
#     selected_movie_scores = [i[0] for i in sim_scores[1:num_of_rec]]
#     # Get the dataframe & title
#     result_df = df.iloc[selected_movie_indices]
#     result_df['similarity_score'] = selected_movie_scores
#     final_recommended_movies = result_df[['title', 'year', 'vote_average']]
#     return final_recommended_movies

def imdb_url(imdb_id):
    return f'https://www.imdb.com/title/{imdb_id}/'


def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=7aa8ed02db282841456234e35f1401a1&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w154/" + poster_path
    return full_path

@st.cache(persist=True, show_spinner=False)
def get_recommendations(title, cosine_sim_mat, df, num_of_rec=16):
    combined = df.reset_index()
    #titles = combined[['title', 'year', 'vote_average']]
    indices = pd.Series(combined.index, index=combined['title'])
    
    id = indices[title]
    sim_scores = list(enumerate(cosine_sim_mat[id]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:num_of_rec+1]

    recommended_movies = []
    recommended_movies_posters = []
    url = []

    for i in sim_scores:
        # Fetch the movies poster
        movie_id = combined.iloc[i[0]].id
        imdb_id = combined.iloc[i[0]].imdb_id
        recommended_movies.append(combined.iloc[i[0]][['title', 'year', 'vote_average']])
        recommended_movies_posters.append(fetch_poster(movie_id))
        url.append(imdb_url(imdb_id))

    return recommended_movies,recommended_movies_posters, url

    # movie_indices = [i[0] for i in sim_scores]
    # return titles.iloc[movie_indices]

# @st.cache(persist=True, show_spinner=False, suppress_st_warning=True)
# def recommend(list_of_movies, tfidf_matrix, df, num_of_rec=16):
    
#     df = df.reset_index()
#     titles = df[['title', 'year', 'vote_average']]
#     movies = tfidf_matrix.reindex(list_of_movies)
#     user_profile = movies.mean()
#     tfidf_subset = tfidf_matrix.drop(list_of_movies)
#     similarity_matrix = cosine_similarity(user_profile.values.reshape(1, -1), tfidf_subset)
#     similarity_df = pd.DataFrame(similarity_matrix.T, index=tfidf_subset.index, columns=['similarity_score'])
#     sorted_similarity_df = similarity_df.sort_values(by='similarity_score', ascending=False).head(num_of_rec)

#     return sorted_similarity_df


# CSS Style
# RESULT_TEMP = """
# <div style="width:90%;height:100%;margin:1px;padding:5px;position:relative;border-radius:5px;border-bottom-right-radius: 60px;
# box-shadow:0 0 15px 5px #ccc; background-color: #a8f0c6;
#   border-left: 5px solid #6c6c6c;">
# <p style="color:blue;"><span style="color:black;">📈Score::</span>{}</p>
# <p style="color:blue;"><span style="color:black;">🔗</span><a href="{}",target="_blank">Link</a></p>
# <p style="color:blue;"><span style="color:black;">💲Price:</span>{}</p>
# </div>
# """

# Search for movie
@st.cache(persist=True, show_spinner=False, suppress_st_warning=True)
def search_term_if_not_found(term, df):
    result_df = df[df['title'].str.contains(term)][['title', 'year', 'vote_average', 'imdb_id']]
    return result_df

def main():

    dataframe = None

    movies = load_data('data/movies.pkl')
    tfidf = load_data('data/similarity.pkl')
    
    buffer1, col1, buffer2 = st.columns([0.1, 1, 0.1])
    title = col1.markdown('# :red[Movie Recommender system]')

    st.text("")
    st.text("")
    st.text("")
    st.text("")

    #buffer1, col2, buffer2 = st.columns([0.45, 1, 0.45])
    session.options = st.selectbox(label="Type or select a movie from the dropdown menu", options=movies['title'])

    st.text("")
    st.text("")

    #buffer1, col3, buffer2 = st.columns([0.45, 1, 0.45])
    session.slider_count = st.select_slider(label="Number of Recommendations", options=[5, 10, 15, 20, 25, 30], value=15)

    
    st.text("")
    st.text("")

    buffer1, col4, buffer2 = st.columns([1.15, 0.5, 1.15])

    session.is_clicked = col4.button(label="Recommend", key=1)

    st.text("")
    st.text("")

    if session.is_clicked:
        rec_movies, posters, url = get_recommendations(session.options, cosine_sim_mat=tfidf, df=movies, num_of_rec=session.slider_count)
         #display with the columns

        # cols = cycle(st.columns(5, gap='medium'))
        # for i, rec_movies in enumerate(rec_movies):
        #     next(cols).write("[![](%s)](%s '%s') %s" % (posters[i], url[i], round(rec_movies.vote_average, 1), rec_movies.title))
            

        for i in range(int(session.slider_count/5)):
            movie_cols = st.columns(5, gap='large')
            for j in range(5):
                movie_cols[j].write("[![img](%s)](%s '%s')" % (posters[j+(i*5)], url[j+(i*5)], round(rec_movies[j+(i*5)].vote_average, 1)))
                movie_cols[j].caption(rec_movies[j+(i*5)].title)
                
                #movie_cols[j].image(posters[j+i], use_column_width=True)
            #st.image(posters[i], caption=st.write("[%s](%s)" % (rec_movies[i].title, url[i])), use_column_width=True)

        # buffer1, col3, buffer2 = st.columns([1.45, 1, 1])
        # session.show_more = col3.button('Show more', key=2)

        # if session.show_more:
        #     rec_movies, posters, url = get_recommendations(session.options, cosine_sim_mat=tfidf, df=movies, num_of_rec=30)
        #     for i in range(3):
        #         movie_cols = st.columns(5, gap='medium')
        #     for j in range(5,11):
        #         movie_cols[j].write("[![](%s)](%s '%s')" % (posters[j+(i*5)], url[j+(i*5)], round(rec_movies[j+(i*5)].vote_average, 1)))
        #         movie_cols[j].caption(rec_movies[j+(i*5)].title)

        # with col1:
        #     #text1= '[link]({link})'.format(link=)
        #     #st.write("[ImDb](https://www.imdb.com/title/tt0468569/)")
            
        #     st.image(posters[0], caption=st.write("[%s](%s)" % (rec_movies[0].title, url[0])), use_column_width=True)#rec_movies[0].title)
        #     #st.markdown('<a href="https://docs.streamlit.io"></a>')
        #     #st.write("[![](%s)](%s)" % (posters[0], url[0]))
        #     st.write(rec_movies[0].title)
        # with col2:
        #     st.image(posters[1], caption=st.write("[%s](%s)" % (rec_movies[1].title, url[1])), use_column_width=True)
        #     # st.text(rec_movies[1])
        #     # st.image(posters[1])
        # with col3:
        #     st.image(posters[2], caption=st.write("[%s](%s)" % (rec_movies[2].title, url[2])), use_column_width=True)
        #     # st.text(rec_movies[2])
        #     # st.image(posters[2])
        # with col4:
        #     #st.image(posters[3], caption=st.write("[%s](%s)" % (rec_movies[3].title, url[3])), use_column_width=True)
        #     # st.text(rec_movies[3])
        #     st.image(posters[3], caption=rec_movies[3].title)



    # if dataframe is not None:
    #     st.table(dataframe)


    # menu = ['Home', 'Recommend', 'About']
    # choice = st.sidebar.selectbox('Menu', menu)

    # df = load_data('movies.pkl')

    # if choice == 'Home':
    #     st.subheader('Home')
    #     st.dataframe(df.head(10))
        
    
    # elif choice == 'Recommend':
    #     st.subheader('Recommend Movies')
    #     cosine_sim_mat = load_data('similarity.pkl')
    #     search_term = st.text_input('Search')
    #     num_of_rec = st.sidebar.number_input('Number', 6, 31, 16)
    #     if st.button('Recommend'):
    #         if search_term is not None:
    #             try:
    #                     result = get_recommendations(search_term, cosine_sim_mat, df, num_of_rec)
    #                     with st.expander('Results as JSON'):
    #                         results_json = result.to_dict('index')
    #                         st.write(results_json)

    #                     #st.write(result)
    #                     for row in result.iterrows():
    #                         rec_title = row[1][0]
    #                         rec_year = row[1][1]
    #                         rec_rating = row[1][2]
    #                         #st.write(rec_title, rec_year, rec_rating)
    #                         stc.html(RESULT_TEMP.format(rec_title, rec_year, rec_rating))
                    
    #             except Exception as e:
    #                 result = 'Not Found'
    #                 st.warning(result)
    #                 st.info('Suggested Options include')
    #                 result_df = search_term_if_not_found(search_term, df)
    #                 st.dataframe(result_df)     

    # else:
    #     st.subheader('About')
    #     st.text('Built with Streamlit & Pandas')




if __name__ == '__main__':
    main()